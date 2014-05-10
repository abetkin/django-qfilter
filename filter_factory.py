# -*- coding: utf-8 -*-

'''
A factory to create filters from `FilterContainer` instances.
Generic function is dispatched on `filter_class`.
'''

import filter_types
from simplegeneric import generic

@generic
def make_filter(filter_class, instance, *args, **kw):
    raise NotImplementedError()

@make_filter.when_object(filter_types.QFilter)
def _(filter_class, instance):
    def filter_callable(queryset):
        method = getattr(instance, instance.method_name)
        instance.context['queryset'] = queryset
        return method()
    return filter_types.QFilter(filter_callable)

@make_filter.when_object(filter_types.ValuesDictFilter)
def _(filter_class, instance, fields_list):
    method = getattr(instance, instance.method_name)
    return filter_types.ValuesDictFilter(method, fields_list)

@make_filter.when_object(filter_types.QuerysetIterationHook)
def _(filter_class, instance):
    method = getattr(instance, instance.method_name)
    return filter_types.QuerysetIterationHook(method)
