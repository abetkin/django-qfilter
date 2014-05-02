# -*- coding: utf-8 -*-
from django.db.models import Q, query

#%%

"""
Filter is a callable that returns queryset
"""

class self_is__dict__(dict):
    def __init__(self, *args, **kw):
        super(self_is__dict__, self).__init__(*args, **kw)
        self.__dict__ = self


class QuerysetFilter(object):

    _method_name = None
    
    filter_type = None # filter type is taken into account when combining filters
    context = None
    
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.context = self.get_context()
    
    @property
    def context(self):
        return self._context
    
    @context.setter
    def context(self, dic):
        assert isinstance(dic, dict), 'context should be a dict'
        self._context = self_is__dict__(dic)
    
    def get_context(self):
        'for overriding'
        return self.context
    
    def run_filter(self, context=None):
        '''return queryset
        '''
        self.context.update(context)
        #FIXME construct filter from method
        method = getattr(self, self._method_name)
        return method(queryset)


class FilterRunner(object):
    '''
    finds
    
    run adapter (backend?)
        create
        combine
    '''

    def get_method_names(self, filter_class):
        'return list(names)'
    
    def combine_filters(self):
        'return filter (callable)'
        
        '''
        sort by type
        apply op
        '''

#%%

class SimpleQuerysetFilter(FilterInterface):
    
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
        return_value = self.callable(queryset)
        return self.queryset
            

class QFilter(FilterInterface):
    
    def __init__(self, q_expr):
        self.q_expr = q_expr
    
    def __call__(self, queryset):
        return queryset.filter(self.q_expr)


class QuerysetIterationHook(FilterInterface):
    
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

class ValuesDictFilter(FilterInterface):
    
    def __init__(self, field_list, filter_func):
        self.filter_func = filter_func
        self.field_list = field_list
    
    def __call__(self, queryset):
        field_list = ['pk'] + self.field_list
        objects = queryset.values(*field_list)
        pks = [obj['pk'] for obj in objects
                         if self.filter_func(obj)]
        return queryset.filter(pk__in=pks)

#%%
'test QFilter'

q_filter = QFilter(Q(id=11949))
qs = queryset = BankCompany.objects.all()
q_filter(qs)

#%%
'test SimpleQuerysetFilter'

qs = BankCompany.objects.filter(id=11949)
qsfilter = SimpleQuerysetFilter(qs)
qsfilter(qs)

#%%
'test ValuesDictFilter'

values_filter = ValuesDictFilter([], lambda obj: obj['pk']==11949)
values_filter(queryset)
#%%
'test QuerysetIterationHook'

qs = BankCompany.objects.all()[:5]
def hook_func(obj):
    print obj.pk
    return obj

iter_hook = QuerysetIterationHook(hook_func)
nu = iter_hook(qs)
nu

#%%

def factory(typ, method, context):
    '''
    Q type is default
    '''
    

