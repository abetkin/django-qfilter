# -*- coding: utf-8 -*-
import ipdb
from django.db.models import Q, query
import operator
#%%

class QuerySetFilter(object):
    
    def __and__(self, other):
        if isinstance(other, QuerySetFilter):
            return lambda queryset: self(queryset) & other(queryset)
        return NotImplemented
        
    def __or__(self, other):
        if isinstance(other, QuerySetFilter):
            return lambda queryset: self(queryset) | other(queryset)
        return NotImplemented    


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
    
    def __call__(self, queryset):
        class QuerysetWrapper(type(queryset)):
            def iterator(this):
                for obj in super(QuerysetWrapper, this).iterator():
                    self.hook_function(obj) #TODO: maybe let it throw exception
                    yield obj
        queryset.__class__ = QuerysetWrapper
        return queryset

#%%

class CallablesList(list):
    
    def __init__(self, *args, **kw):
        self.operation = kw.pop('operation', lambda x,y: None)
        super(CallablesList, self).__init__(*args, **kw)
    
    def __call__(self, *args, **kw):
        results = [f(*args, **kw) for f in self]
        results = reversed(results) # make it queue not stack
        return reduce(self.operation, results)

#%%

class ValuesDictFilter(QuerySetFilter):
    
    def __new__(cls, *args, **kw):
        if not args and kw.keys() == ['fields_list']:
            # this is reserved for using class as decorator
            def newobj(*fargs, **fkw):
                obj = cls(*fargs, **fkw)
                obj.fields_list = kw['fields_list']
                return obj
            return newobj
        return super(ValuesDictFilter, cls).__new__(cls, *args, **kw)
    
    def __init__(self, filter_func, fields_list=None):
        self.filter_func = filter_func
        if fields_list:
            self.fields_list = list(fields_list)
    
    def _apply(self, other, operation):
        assert isinstance(other, ValuesDictFilter)
        def list_callables():
            for callabl in (self.filter_func, other.filter_func):
                try:
                    for f in callabl:
                        yield f
                except TypeError:
                    yield callabl
        filter_func = CallablesList(list_callables(), operation=operation)
        return self.__class__(filter_func=filter_func,
                              fields_list=self.fields_list + other.fields_list)
    
    def __and__(self, other):
        if isinstance(other, ValuesDictFilter):
            return self._apply(other, operation=lambda x, y: x and y)
        return super(ValuesDictFilter, self).__and__(other)
    
    def __or__(self, other):
        if isinstance(other, ValuesDictFilter):
            return self._apply(other, operation=lambda x, y: x or y)
        return super(ValuesDictFilter, self).__or__(other)
    
    def __call__(self, queryset):
        fields_list = ['pk'] + self.fields_list
        objects = queryset.values(*fields_list)
        pks = [obj['pk'] for obj in objects
                         if self.filter_func(obj)]
        return queryset.filter(pk__in=pks)

#%%

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'unicom.settings'

#%%

#with ipdb.launch_ipdb_on_exception():
@ValuesDictFilter(fields_list=[])
def filtr(obj):
    return obj['pk'] == 11978

@ValuesDictFilter(fields_list=['region_list__city_type'])
def fname(obj):
    return obj['region_list__city_type']
#    return obj['company_name'] in (u'Альфа-Банк', u'Абсолют Банк', u'Авангард')


#%%
import operator
from unicom.crm.models import BankCompany
f = filtr | fname
f

#%%
#BankCompany.objects.get(pk=11978).company_name
qs = f(BankCompany.objects.all())
qs.count()

#%%

@QuerysetIterationHook
def set_hvost(obj):
    obj.hvost = 30

qs = set_hvost(BankCompany.objects.filter(id=11978))
qs[0].hvost
#%%

#%%

'Init project'

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'unicom.settings'

from django.db.models import Q

#%%

@QFilter
def my_filter(queryset):
    return BankCompany.objects.filter(id__in=(11949, 11978))

@QFilter
def filtr(qs):
    return Q(id=11978)

#%%

(my_filter & filtr)(BankCompany.objects.all())

##%%
#'test QFilter'
#
#q_filter = QFilter(Q(id=11949))
#qs = queryset = BankCompany.objects.all()
#q_filter(qs)
#
#%%
'test SimpleQuerysetFilter'

qs = BankCompany.objects.filter(id=11949)
qsfilter = SimpleQuerysetFilter(qs)
qsfilter(qs)

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