# -*- coding: utf-8 -*-

#from django.db.models import Q, query
from functools import reduce
from .utils import CallablesList

class QuerySetFilter(object):
    '''
    An instance is a QuerySet filter if instance(queryset) returns a queryset.
    Filter class also defines operations with other querysets.
    '''

    def __init__(self, wrapped_callable=None):
        self._wrapped_callable = wrapped_callable # if any

    def __and__(self, other):
        return QuerySetFilter(
                lambda queryset: self(queryset) & other(queryset))
        
    def __or__(self, other):
        return QuerySetFilter(
                lambda queryset: self(queryset) | other(queryset))

    def __call__(self, queryset):
        if not self._wrapped_callable:
            raise NotImplementedError()
        return self._wrapped_callable(queryset)


class QFilter(QuerySetFilter):
    '''
    Wraps a Q instance or a callable that produces it.
    
    Supports invertion (~).
    '''

    def __init__(self, get_q):
        from django.db.models import Q
        if isinstance(get_q, Q):
            self.get_q = lambda queryset: get_q
        else:
            assert hasattr(get_q, '__call__')
            self.get_q = get_q

    def __call__(self, queryset):
        return_value = self.get_q(queryset)
        from django.db.models import Q
        assert isinstance(return_value, Q), (
                "%s should return a Q instance" % self.get_q.__name__)
        return queryset.filter(return_value)

    def __invert__(self):
        def inverted_q(queryset, get_q=self.get_q):
            return ~get_q(queryset)
        self.get_q = inverted_q
        return self


class ValuesDictFilter(QFilter):
    
    def __new__(cls, *args, **kw):
        if args == ('@',):
            # this is reserved for using class as decorator
            def newobj(func):
                obj = cls(func)
                obj.__dict__.update(kw)
                return obj
            return newobj
        return super(ValuesDictFilter, cls).__new__(cls)
    
    def __init__(self, filter_func, fields_list=None):
        self.filter_func = filter_func
        if fields_list:
            self.fields_list = list(fields_list)
    
    def __mod__(self, other):
        '''
        For internal use.
        This operation means: merge 2 filters, i.e., create a new one,
        initialized with as many attributes of both filters as possible (or makes sense).
        '''
        if type(other) == ValuesDictFilter:
            fields_list=self.fields_list + other.fields_list
            return self.__class__(None, fields_list)
        return NotImplemented
    
    __rmod__ = __mod__

    def __and__(self, other):
        if isinstance(other, ValuesDictFilter):
            try:
                result = self % other
            except TypeError:
                return NotImplemented
            result.filter_func = CallablesList.from_callables(
                    [self.filter_func, other.filter_func],
                    lambda x, y: x and y)
            return result
        return super(ValuesDictFilter, self).__and__(other)
    
    def __or__(self, other):
        if isinstance(other, ValuesDictFilter):
            try:
                result = self % other
            except TypeError:
                return NotImplemented
            result.filter_func = CallablesList.from_callables(
                    [self.filter_func, other.filter_func],
                    lambda x, y: x or y)
            return result
        return super(ValuesDictFilter, self).__or__(other)
    
    def _fetch_objects(self, queryset):
        fields_list = ['pk'] + self.fields_list
        return queryset.values(*fields_list)
    
    def get_q(self, queryset):
        objects = self._fetch_objects(queryset)
        pks = [obj['pk'] for obj in objects
                         if self.filter_func(obj)]
        from django.db.models import Q
        return Q(pk__in=pks)
