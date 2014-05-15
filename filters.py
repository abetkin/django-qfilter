# -*- coding: utf-8 -*-
import ipdb
from django.db.models import Q, query
import operator
from itertools import groupby
#%%
import os

#%%

class QuerySetFilter(object):
    '''
    An instance is a QuerySet filter if instance(queryset) returns a queryset.
    Filter class also defines operations with other querysets.
    '''

    def __and__(self, other):
        return lambda queryset: self(queryset) & other(queryset)
        
    def __or__(self, other):
        return lambda queryset: self(queryset) | other(queryset)


class QFilter(QuerySetFilter):

    def __init__(self, callabl):
        self.callable = callabl
    
    def __call__(self, queryset):
        return_value = self.callable(queryset)
        if isinstance(return_value, Q):
            return queryset.filter(return_value)
        assert isinstance(return_value, query.QuerySet)
        return return_value


class QuerysetIterationHook(QuerySetFilter):
    
    def __init__(self, hook_function):
        self.hook_function = hook_function

    def _combine(self, other):
        #TODO: add support for lazy operations
        assert isinstance(other, QuerysetIterationHook)
        hook_function = CallablesList.from_callables(
                [self.hook_function, other.hook_function], None)
        return self.__class__(hook_function)
    
    def __and__(self, other):
        if isinstance(other, QuerysetIterationHook):
            return self._combine(other)
        return super(QuerysetIterationHook, self).__and__(other)
    
    def __or__(self, other):
        if isinstance(other, QuerysetIterationHook):
            return self._combine(other)
        return super(QuerysetIterationHook, self).__or__(other)
    
    def __call__(self, queryset):
        class QuerysetWrapper(type(queryset)):
            def iterator(this):
                for obj in super(QuerysetWrapper, this).iterator():
                    self.hook_function(obj) #TODO: maybe let it throw exception
                    yield obj
        queryset.__class__ = QuerysetWrapper
        return queryset

#%%

class LazyOperator(object):
    '''
    like `and`: f() and g() # g might not get executed
    '''
    #TODO

#%%

class CallablesList(list):
    
    def __init__(self, *args, **kw):
        self.operation = kw.pop('operation', lambda x,y: None)
        super(CallablesList, self).__init__(*args, **kw)
    
    @classmethod
    def from_callables(cls, callables, operation=None):
        '''
        Assuming some of callables may be instances of `CallablesList`
        construct a new instance with a list of plain functions.
        '''
        def flat_list():
            for callabl in callables:
                try:
                    for f in callabl:
                        yield f
                except TypeError:
                    yield callabl
        operation = operation or (lambda x,y: None)
        return cls(flat_list(), operation=operation)
    
    
    def __call__(self, *args, **kw):
        results = [f(*args, **kw) for f in self]
        results = reversed(results) # make it queue not stack
        return reduce(self.operation, results)


#%%

class ValuesDictFilter(QuerySetFilter):
    
    def __new__(cls, *args, **kw):
        if args == ('@',):
            # this is reserved for using class as decorator
            def newobj(func):
                obj = cls(func)
                obj.__dict__.update(kw)
                return obj
            return newobj
        return super(ValuesDictFilter, cls).__new__(cls, *args, **kw)
    
    def __init__(self, filter_func, fields_list=None):
        self.filter_func = filter_func
        if fields_list:
            self.fields_list = list(fields_list)
    
    def _apply_op(self, operation, other):
        assert isinstance(other, ValuesDictFilter)
        fields_list=self.fields_list + other.fields_list
        filter_func = CallablesList.from_callables(
                [self.filter_func, other.filter_func], operation)
        return self.__class__(filter_func, fields_list)
    
    def __and__(self, other):
        if isinstance(other, ValuesDictFilter):
            return self._apply_op(lambda x, y: x and y, other)
        return super(ValuesDictFilter, self).__and__(other)
    
    def __or__(self, other):
        if isinstance(other, ValuesDictFilter):
            return self._apply_op(lambda x, y: x or y, other)
        return super(ValuesDictFilter, self).__and__(other)
    
    def _fetch_objects(self, queryset):
        fields_list = ['pk'] + self.fields_list
        return queryset.values(*fields_list)
    
    def __call__(self, queryset):
        objects = self._fetch_objects(queryset)
        get_pk = lambda obj: getattr(obj, 'pk', None) or obj['pk']
        pks = [get_pk(obj) for obj in objects
                         if self.filter_func(obj)]
        return queryset.filter(pk__in=pks)

#%%
class Attribute(object):

    _empty = True # does not contain other attributes

    def __init__(self, name=None, values_dict=None):
        self.name = name
        self._dict = values_dict
    
    @classmethod
    def make_class_from_fields_list(cls, fields_list, parent_field=None):
        fields_list = filter(None, fields_list)
        if not fields_list:
            return cls
        result = type('%s_%s' % (parent_field or 'root', cls.__name__),
                          (cls,), {})
        head__tail = [field.partition('__') for field in fields_list]
        
        for head, head__tail in groupby(head__tail, key=lambda t: t[0]):
            if not parent_field:
                parent = head
            else:
                parent = '__'.join([parent_field, head])
            attr_class = cls.make_class_from_fields_list(
                    (parts[-1] for parts in head__tail),
                    parent_field=parent)
            setattr(result, head, attr_class(parent))
            result._empty = False
        return result
    
    def get_value(self):
        assert self._dict and self.name in self._dict, str(self._dict.items()) + str(self.name)
        value = self._dict[self.name]
        if hasattr(self.name, 'transform'):
            value = self.name.transform(value)
        return value
    
    def __get__(self, instance, owner):
#        if owner:
#            return self
        try:
            self._dict = instance._dict
            return self if not self._empty else self.get_value()
        except:
            return self

#%%
class PropertyBasedFilter(ValuesDictFilter):
    
    def __init__(self, filter_func, fields_list=None, properties=None):
        super(PropertyBasedFilter, self).__init__(filter_func, fields_list)
        if properties:
            self.properties = properties
    
    def _fetch_objects(self, queryset):
        fields_list = ['pk'] + self.fields_list
        Object = Attribute.make_class_from_fields_list(fields_list)
        
        def get_field_model(model, field_name):
            return getattr(model, field_name).field.related.parent_model
        
        for property_name in self.properties:
            split_name = property_name.split('.')
            model_class = reduce(lambda model, field: get_field_model(model, field),
                                 split_name[:-1],
                                 queryset.model)
            attribute_class = reduce(lambda x, y: getattr(x, y), split_name[:-1], Object)
            prop = getattr(model_class, split_name[-1])
            setattr(attribute_class, split_name[-1], property(prop.fget))
        
        
        objects = queryset.values(*fields_list)
        return [Object(values_dict=dic) for dic in objects]
        
##%%
#from collections import namedtuple
#Exists = namedtuple('Exists', ['exists'])
#
#class M2MAnimal(str):
#    def transform(self, pk):
#        return Exists(lambda: True) if pk else Exists(lambda: False)
#
#@PropertyBasedFilter('@',
#                     fields_list=[M2MAnimal('can_live_with')], 
#                     properties=['can_have_other_animals'])
#def filter_func(obj):
#    return obj.can_have_other_animals
#
##%%
#print filter_func(CatsBreed.objects.all())
#%%

#%%


