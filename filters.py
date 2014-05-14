# -*- coding: utf-8 -*-
import ipdb
from django.db.models import Q, query
import operator
#%%
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'unicom.settings'
from unicom.private.questionary.models import Questionary

#%%
for q in Questionary.objects.all()[:1000]:
    if q.has_guarantee:
        print q.id,
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
        pks = [obj['pk'] for obj in objects
                         if self.filter_func(obj)]
        return queryset.filter(pk__in=pks)
#%%
fields_list = [
    'name',
    'dummy__field',
    'can_live_with__weight'
]

#XXX extend: make field extend str and define `def value()`

#%%
class Attribute(object):

    def __init__(self, name, lookup_dict=None):
        self.name = name
        self._dict = lookup_dict
    
    @classmethod
    def from_fields_list(cls, fields_list, parent_field=None):
        fields_list = filter(None, fields_list)
        if not fields_list:
            return cls(parent_field)
        attr_class = type('%s_%s' % (parent_field or 'root', cls.__name__),
                          (cls,), {})
        head__tail = [field.partition('__') for field in fields_list]
        
        for head, head__tail in groupby(head__tail, key=lambda t: t[0]):
            if not parent_field:
                parent = head
            else:
                parent = '__'.join([parent_field, head])
            attr = cls.from_fields_list(
                    (parts[-1] for parts in head__tail),
                    parent_field=parent)
            setattr(attr_class, head, attr)
        return attr_class(parent_field)
    
    @property
    def value(self):
        'FIXME'
    
    def __get__(self, instance, owner):
        assert instance
        self._dict = instance._dict
        if self._dict and self.name in self._dict:
            return self._dict[self.name]
        return self

#%%
from itertools import groupby
Attribute.from_fields_list(fields_list)
#%%

#classmethod for Atribute
#def make_tree(tuples, name=None):
#    '''
#    [(1, 2, 3),
#    (1, 3, 4),
#    (1, 3, 5)]
#    -> dict
#    result[1][3][5]
#    '''
#    tuples = filter(None, tuples)
#    def gen():
#        for first_elt, tupls in groupby(tuples, key=lambda t: t[0]):
#            sub_name = '__'.join(filter(None, [name, first_elt]))
#            subtree = make_tree((t[1:] for t in tupls), name=sub_name)
#            print subtree
#            yield first_elt, subtree if subtree else "LEAF"
#            # by first elt
#    return dict(gen())

#%%
def make_tree(fields_list, parent_field=None):
    '''
    [(1, 2, 3),
    (1, 3, 4),
    (1, 3, 5)]
    -> dict
    result[1][3][5]
    '''
    fields_list = filter(None, fields_list)
    def gen():
        head__tail = [field.partition('__') for field in fields_list]
        
        for head, head__tail in groupby(head__tail, key=lambda t: t[0]):
            if not parent_field:
                parent = head
            else:
                parent = '__'.join([parent_field, head])
            subtree = make_tree((parts[-1] for parts in head__tail),
                                parent_field=parent)
            yield head, subtree
            # cls.head = Attribute
    return Attribute(gen())
#%%
tree = make_tree(fields_list)
tree
#%%
tuples
#%%
class Attribute(str):
    '''Obviously can be overriden.'''
    
    def lookup(self, dic):
        return dic[self]

#%%
d = {'a': 1}
d[Attribute('a')]
#%%
class PropertyBasedFilter(ValuesDictFilter):
    
    def __init__(self, filter_func, fields_list=None, properties=None):
        super(PropertyBasedFilter, self).__init__(filter_func, fields_list)
        if properties:
            self.properties = properties
    
    def _fetch_objects(self, queryset):
        
        class Lookup(object):
            prefix = None
            keys = make_tree(key.split('__') for key in self.fields_list)
    
            def __getattr__(self, name):
                if name in self._keys:
                    lookup = ('__'.join((self.prefix, name))
                              if self.prefix else name)
                    self._keys = self._keys[name]
                    if not self._keys:
                        self._lookup = None
                        return self[lookup]
                    else:
                        self._lookup = lookup
                        return self
        
        class FetchedObject(dict):

            def __getattr__(self, name):
                if name in self._keys:
                    lookup = ('__'.join((self._lookup, name))
                                    if self._lookup else name)
                    self._keys = self._keys[name]
                    if not self._keys:
                        self._lookup = None
                        return self[lookup]
                    else:
                        self._lookup = lookup
                        return self
        
        for property_name in self.properties:
            prop = getattr(queryset.model, property_name)
            setattr(FetchedObject, property_name, property(prop.fget))
        
        fields_list = ['pk'] + self.fields_list
        objects = queryset.values(*fields_list)
        return [FetchedObject(dic) for dic in objects]
        
#%%
@PropertyBasedFilter('@', fields_list=['dummy__field'], properties=['has_dummy'])
def filter_func(obj):
    import ipdb
    ipdb.set_trace()
    return obj.has_dummy

#%%
filter_func(CatsBreed.objects.all())
#%%
d = {}
class MyDict(dict):
    pass
d.__class__ = MyDict
#%%

class as_object(dict):
    '''
    self.__dict__ is self.
    '''
    
    def __init__(self, *args, **kw):
        super(as_object, self).__init__(*args, **kw)
        self.__dict__ = self

#%%

def make_nested_object(values_dict):
    values_dict = {tuple(key.split('__')): value
                   for key, value in values_dict.items()}

#%%
values_dict = {tuple(key.split('__')): value for key, value in {
    'aa': 1,
    'a__bb': 2,
    'a__b__c': 3,
    'a__b__d': 4,
}.items()}

class merge_values(dict):
    '''
    Assume values in a dict are dicts. When setting value for key with existing value
    merge values (i.e. dicts) instead of ovewriting the old one.
    '''  
    
    def __setitem__(self, key, value):
        if self.get(key):
            value = self.fromitems(self[key].items() + value.items())
        super(merge_values, self).__setitem__(key, value)
    
    @classmethod
    def fromitems(cls, items):
        dic = None
        for key, value in items:
            if not dic:
                dic_type = type('special_%s' % value.__class__.__name__,
                              (cls, value.__class__),
                              {})
                dic = dic_type(key=value)
            assert isinstance(dic, value.__class__), 'Items must be of the same type'
            dic[key] = value
        return dic
        
#%%
def by_parent_tuple(tuples_dict):
    for tupl, value in values_dict.items():
        if not tupl:
            yield tupl, value
        else:
            yield tupl[:-1], as_object({tupl[-1]: value})
items = list(by_parent_tuple(values_dict))
print items

#%%
o = items[0][1]
p = items[1][1]
print o
print p
#%%
q = o.__class__(o.items() + u.items())
q
#%%
values_dict = merge_values.fromitems(items)
values_dict
#%%
#tuples_dict = dict(tuples)

tuples = values_dict.keys()
tuples
#%%
def _groups():
#    for key, obj in tuples:
#        if not key:
#            yield key, obj
#    tuples
    tuples
    tuples = sorted(tuples, key=lambda t: len(t[0]), reverse=True)
    for key, it in groupby([t[0] for t in nonzero], key=lambda t: t[:-1]):
        d = as_object()
        for tupl in it:
            d[tupl[-1]] = tuples_dict[tupl]
        yield key, d
tuples = list(_groups()) 
#%%
tuples
#%%
d = {}
tuples = sorted(tuples, reverse=True)

length = len(tuples[0][0])
for t, v in tuples:
    if len(t) < length:
        d.
        d = as_object({t[-1]: d})
    else:
        d[t[-1]] = v
#%%
d.a.b
#%%



#
#import os
#os.environ['DJANGO_SETTINGS_MODULE'] = 'unicom.settings'
#
##%%
#
##with ipdb.launch_ipdb_on_exception():
#@ValuesDictFilter(fields_list=[])
#def filtr(obj):
#    return obj['pk'] == 11978
#
#@ValuesDictFilter(fields_list=['region_list__city_type'])
#def fname(obj):
#    return obj['region_list__city_type']
##    return obj['company_name'] in (u'Альфа-Банк', u'Абсолют Банк', u'Авангард')
#
#
##%%
#import operator
#from unicom.crm.models import BankCompany
#f = filtr & fname
#f
#
##%%
##BankCompany.objects.get(pk=11978).company_name
#qs = f(BankCompany.objects.all())
#qs.count()
#
##%%
#
#@QuerysetIterationHook
#def set_hvost(obj):
#    obj.hvost = 30
#
#@QuerysetIterationHook
#def set_color(obj):
#    obj.color = 'grey'
#
#f = set_color | set_hvost
#
##%%
#
#qs = f(BankCompany.objects.filter(id=11978))
#qs[0].color + ' ' + str(qs[0].hvost)
##%%
#
##%%
#
#'Init project'
#
#import os
#os.environ['DJANGO_SETTINGS_MODULE'] = 'unicom.settings'
#
#from django.db.models import Q
#
##%%
#
#@QFilter
#def my_filter(queryset):
#    return BankCompany.objects.filter(id__in=(11949, 11978))
#
#@QFilter
#def filtr(qs):
#    return Q(id=11978)
#
##%%
#
#(my_filter & filtr)(BankCompany.objects.all())
#
###%%
##'test QFilter'
##
##q_filter = QFilter(Q(id=11949))
##qs = queryset = BankCompany.objects.all()
##q_filter(qs)
##
##%%
#'test SimpleQuerysetFilter'
#
#qs = BankCompany.objects.filter(id=11949)
#qsfilter = SimpleQuerysetFilter(qs)
#qsfilter(qs)
#
#%%
#'test ValuesDictFilter'
#
#values_filter = ValuesDictFilter([], lambda obj: obj['pk']==11949)
#values_filter(queryset)
##%%
#'test QuerysetIterationHook'
#
#qs = BankCompany.objects.all()[:5]
#def hook_func(obj):
#    print obj.pk
#    return obj
#
#iter_hook = QuerysetIterationHook(hook_func)
#nu = iter_hook(qs)
#nu
#
#%%