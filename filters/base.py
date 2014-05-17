# -*- coding: utf-8 -*-

from django.db.models import Q, query


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

    def __init__(self, get_q):
        if isinstance(get_q, Q):
            self.get_q = lambda queryset: get_q
        else:
            assert hasattr(get_q, '__call__')
            self.get_q = get_q

    def __call__(self, queryset):
        return_value = self.get_q(queryset)
        assert isinstance(return_value, Q), (
                "%s should return a Q instance" % self.get_q.__name__)
        return queryset.filter(return_value)

    def __invert__(self):
        def inverted_q(queryset, get_q=self.get_q):
            return ~get_q(queryset)
        self.get_q = inverted_q
        return self


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

class ValuesDictFilter(QFilter):
    
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
    
    def get_q(self, queryset):
        objects = self._fetch_objects(queryset)
        get_pk = lambda obj: getattr(obj, 'pk', None) or obj['pk']
        pks = [get_pk(obj) for obj in objects
                         if self.filter_func(obj)]
        return Q(pk__in=pks)
