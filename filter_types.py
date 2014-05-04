# -*- coding: utf-8 -*-
import ipdb
from django.db.models import Q, query

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


class QuerysetIterationHook(object):
    
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

class ValuesDictFilter(object):
    
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
            self.fields_list = fields_list
    
    def __call__(self, queryset):
        fields_list = ['pk'] + self.fields_list
        objects = queryset.values(*fields_list)
        pks = [obj['pk'] for obj in objects
                         if self.filter_func(obj)]
        return queryset.filter(pk__in=pks)

#%%
#with ipdb.launch_ipdb_on_exception():
@ValuesDictFilter(fields_list=[])
def filtr(obj):
    return obj['pk'] == 11978

#%%
from unicom.crm.models import BankCompany
filtr(BankCompany.objects.all())

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