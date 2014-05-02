# -*- coding: utf-8 -*-

from django.db.models import Q, query

#%%

class SimpleQuerysetFilter(object):
    
    filter_type = 'queryset'
    
    def __init__(self, callabl):
        self.callable = callabl
    
    def __and__(self, other):
        if other.filter_type == 'queryset':
            return lambda queryset: self(queryset) & other(queryset)
        return NotImplemented
        
    def __or__(self, other):
        if other.filter_type == 'queryset':
            return lambda queryset: self(queryset) | other(queryset)
        return NotImplemented
    
    def __call__(self, queryset):
        #TODO
        return_value = self.callable(queryset)
        return self.queryset
            

class QFilter(object):
    
    def __init__(self, q_expr):
        self.q_expr = q_expr
    
    def __call__(self, queryset):
        return queryset.filter(self.q_expr)


class QuerysetIterationHook(object):
    
    def __init__(self, hook_function):
        self.hook_function = hook_function
    
    def __call__(self, queryset):
        class QuerysetWrapper(type(queryset)):
            def iterator(this):
                for obj in super(QuerysetWrapper, this).iterator():
                    new_obj = self.hook_function(obj)
                    if new_obj is not None:
                        yield new_obj
        queryset.__class__ = QuerysetWrapper
        return queryset

class ValuesDictFilter(object):
    
    def __init__(self, field_list, filter_func):
        self.filter_func = filter_func
        self.field_list = field_list
    
    def __call__(self, queryset):
        field_list = ['pk'] + self.field_list
        objects = queryset.values(*field_list)
        pks = [obj['pk'] for obj in objects
                         if self.filter_func(obj)]
        return queryset.filter(pk__in=pks)

##%%
#'test QFilter'
#
#q_filter = QFilter(Q(id=11949))
#qs = queryset = BankCompany.objects.all()
#q_filter(qs)
#
##%%
#'test SimpleQuerysetFilter'
#
#qs = BankCompany.objects.filter(id=11949)
#qsfilter = SimpleQuerysetFilter(qs)
#qsfilter(qs)
#
##%%
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
##%%
