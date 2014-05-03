# -*- coding: utf-8 -*-

import inspect
import filter_types

#%%

"""
Filter is a callable that returns queryset
"""

class self_is__dict__(dict):
    def __init__(self, *args, **kw):
        super(self_is__dict__, self).__init__(*args, **kw)
        self.__dict__ = self


class FilterSet(object):

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
    
    def __iter__(self):
        'depends on grouping setting'

    def as_filter(self):
        def callabl(queryset):
            method = getattr(self, self._method_name)
            self.context.queryset = queryset
            return method()
        klass = self._dispatch(self._method_name)
        return klass(callabl)

    @classmethod
    def _dispatch(cls, method_name):
        return 'filter class'

    @classmethod
    def is_filter_method(cls, name):
        return name.startswith('filter__')

    @classmethod
    def _find_methods(cls):
        'return {method_name: method_info}'
        def gen():
            for name in dir(cls):
                method = getattr(cls, name)
                if not inspect.ismethod(method) or not cls.is_filter_method(name):
                    continue
                info = cls._collect_method_info(name)
                yield name, info
        return dict(gen())

    @classmethod
    def _collect_method_info(cls, method_name):
        method = getattr(cls, method_name)
        if hasattr(method, 'type'):
            return {'class': cls.get_filter_class(method.type)}
        return {'class': filter_types.SimpleQuerysetFilter}
    
    filter_types = {'queryset': filter_types.SimpleQuerysetFilter}
    
    @classmethod
    def get_filter_class(cls, filter_type):
        return cls.filter_types.get(filter_type) 
#

