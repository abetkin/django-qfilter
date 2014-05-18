# -*- coding: utf-8 -*-
from itertools import groupby
from functools import reduce

from . import QuerySetFilter, ValuesDictFilter
from .utils import CallablesList



class QuerysetIterationHook(QuerySetFilter):
    
    def __init__(self, hook_function):
        self.hook_function = hook_function
    
    def __and__(self, other):
        if isinstance(other, QuerysetIterationHook):
            # now __and__ and __or__ are identical
            # TODO: add support for lazy operations
            return self.__class__(hook_function=CallablesList.from_callables(
                [self.hook_function, other.hook_function], None))
        return super(QuerysetIterationHook, self).__and__(other)
    
    def __or__(self, other):
        if isinstance(other, QuerysetIterationHook):
            # now __and__ and __or__ are identical
            # TODO: add support for lazy operations
            return self.__class__(hook_function=CallablesList.from_callables(
                [self.hook_function, other.hook_function], None))
        return super(QuerysetIterationHook, self).__or__(other)
    
    def __call__(self, queryset):
        class QuerysetWrapper(type(queryset)):
            def iterator(this):
                for obj in super(QuerysetWrapper, this).iterator():
                    self.hook_function(obj) #TODO: maybe let it throw exception
                    yield obj
        queryset.__class__ = QuerysetWrapper
        return queryset



class _Attribute(object):

    _empty = True # does not contain other attributes

    def __init__(self, name=None, values_dict=None):
        self.name = name
        self._dict = values_dict

    @classmethod
    def make_class_from_fields_list(cls, fields_list, parent_field=None):
        fields_list = list(filter(None, fields_list))
        if not fields_list:
            return cls
        if parent_field:
            result = type('%s_%s' % (parent_field, cls.__name__),
                          (cls,), {})
        else:
            transform_dict = {field: field.transform
                              for field in fields_list if hasattr(field, 'transform')}
            class Object(cls):
                def __getitem__(self, item):
                    return self._dict[item]
                    
                def __init__(self, name=None, values_dict=None):
                    
                    class look_for_transforms(dict):
                        def __getitem__(this, item):
                            rv = super(look_for_transforms, this).__getitem__(item)
                            if item not in transform_dict:
                                return rv
                            transform = transform_dict[item]
                            return transform(self, rv)
                    
                    values_dict = values_dict and look_for_transforms(values_dict)
                    return super(Object, self).__init__(name, values_dict)
                
            result = Object
        
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
        return self._dict[self.name]
    
    def __get__(self, instance, owner):
        if not instance:
            return self
        self._dict = instance._dict
        return self if not self._empty else self.get_value()


class PropertyBasedFilter(ValuesDictFilter):
    
    def __init__(self, filter_func, fields_list=None, properties=None):
        super(PropertyBasedFilter, self).__init__(filter_func, fields_list)
        if properties:
            self.properties = properties
    
    def __mod__(self, other):
        if not isinstance(other, ValuesDictFilter):
            return NotImplemented
        fields_list=self.fields_list + other.fields_list
        properties = set(self.properties)
        if isinstance(other, PropertyBasedFilter):
            properties |= set(other.properties)
        return self.__class__(None, fields_list, properties)
    
    __rmod__ = __mod__
    
    def _fetch_objects(self, queryset):
        fields_list = ['pk'] + self.fields_list
        Object = _Attribute.make_class_from_fields_list(fields_list)
        
        def get_related_model(model, field_name):
            return getattr(model, field_name).field.related.parent_model
        
        for property_name in self.properties:
            split_name = property_name.split('.')
            model_class = reduce(lambda model, field: get_related_model(model, field),
                                 split_name[:-1],
                                 queryset.model)
            if not split_name[:-1]:
                attribute_class = Object
            else:
                get_attr = lambda cls, name: getattr(cls, name).__class__
                attribute_class = reduce(get_attr, split_name[:-1], Object)
            prop = getattr(model_class, split_name[-1])
            setattr(attribute_class, split_name[-1], property(prop.fget))
        
        objects = queryset.values(*fields_list)
        return [Object(values_dict=dic) for dic in objects]
