# -*- coding: utf-8 -*-

'''
Instances passed to methods below are registered (via abc) to be of some <FilterType>
and delegate filtering functionality to the `_filter` attribute. 

The factory methods return a new instance of <FilterType>
so that it could be wrapped into the `_filter` attribute.
'''

import filter_types
from decimal import Decimal

from functools import singledispatch

#%%

@singledispatch
def make_filter(instance, *args, **kw):
    default = make_filter.dispatch(filter_types.QFilter)
    return default(instance, *args, **kw)

@make_filter.register(filter_types.QFilter)
def _(instance):
    def filter_callable(queryset):
        method = getattr(instance, instance.method_name)
        instance.context['queryset'] = queryset
        return method()
    return filter_types.QFilter(filter_callable)

@make_filter.register(filter_types.ValuesDictFilter)
def _(instance, fields_list):
    method = getattr(instance, instance.method_name)
    return filter_types.ValuesDictFilter(method, fields_list)

@make_filter.register(filter_types.QuerysetIterationHook)
def _(instance):
    method = getattr(instance, instance.method_name)
    return filter_types.QuerysetIterationHook(method)

#%%

 

#%%
#%%