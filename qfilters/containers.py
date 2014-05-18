# -*- coding: utf-8 -*-

import operator
from functools import reduce
from . import (QFilter, ValuesDictFilter, QuerysetIterationHook,
                     PropertyBasedFilter)


class MethodFilter(object):
    '''
    Allows to create filter instances from methods.
    '''
    
    _filter = None

    def __new__(cls, method_name=None, *args, **kw):
        if not method_name:
            return FilterContainer(cls, *args, **kw)
        return super(MethodFilter, cls).__new__(cls)

    def __init__(self, method_name, context={}):
        self.method_name = method_name
        self.context = context
        method = getattr(self, method_name)
        default_filter_class = QFilter
        # `make_filter_args` and `make_filter_kwargs`
        #  are usually obtained from method decorator arguments. See examples.
        make_filter_args = getattr(method, 'make_filter_args',
                                   (default_filter_class,))
        filter_class, make_filter_args = make_filter_args[0], make_filter_args[1:]
        make_filter_kwargs = getattr(method, 'make_filter_kwargs', {})
        self._filter = makefilter(filter_class, self,
                                  *make_filter_args, **make_filter_kwargs)

    ## Delegate filtering to `_filter`

    def __call__(self, queryset):
        return self._filter(queryset)
    
    def __and__(self, other):
        return self._filter & other
    
    def __or__(self, other):
        return self._filter | other

    ##

    def __repr__(self):
        return '%s (%s)' % (self.method_name, self._filter.__class__)
    
    @classmethod
    def is_filter_method(cls, name):
        return name.startswith('filter__')

    @classmethod
    def _get_methods_names(cls):
        attrs = dir(cls)
        return filter(lambda name: cls.is_filter_method(name), attrs)


class FilterContainer(object):
    '''
    Container for `MethodFilter`s (from now on: "items").
    '''
    
    combine = operator.and_
    
    def __init__(self, items_class, *args, **kw):
        if 'combine' in kw:
            self.combine = kw.pop('combine')
        self._filters = []
        for method_name in items_class._get_methods_names():
            self._filters.append(
                    items_class(method_name=method_name, *args, **kw))
    
    def __iter__(self):
        return iter(self._filters)
    
    def __call__(self, queryset):
        if self._filters:
            combined = reduce(self.combine, self._filters)
            return combined(queryset)
        return queryset
    


'''
A generic function to create filters from `MethodFilter` instances.
Is dispatched on `filter_class`.
'''

# Obviously registering factory functions globally is BAD
# TODO: move to a class

from simplegeneric import generic
#%%
@generic
def makefilter(filter_class, instance, *args, **kw):
    raise NotImplementedError()
#%%

@makefilter.when_object(QFilter)
def _(filter_class, instance):
    def filter_callable(queryset):
        method = getattr(instance, instance.method_name)
        instance.context['queryset'] = queryset
        return method()
    return QFilter(filter_callable)


@makefilter.when_object(ValuesDictFilter, PropertyBasedFilter)
def _(filter_class, instance, *args, **kw):
    method = getattr(instance, instance.method_name)
    return filter_class(method,  *args, **kw)


@makefilter.when_object(QuerysetIterationHook)
def _(filter_class, instance):
    method = getattr(instance, instance.method_name)
    return QuerysetIterationHook(method)





