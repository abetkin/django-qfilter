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


class FiltersContainer(object):

    _context = {}
    
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.context = self.get_context()
    
    ## small trick for convenience
    @property
    def context(self):
        return self._context
    
    @context.setter
    def context(self, dic):
        assert isinstance(dic, dict), 'context should be a dict'
        self._context = self_is__dict__(dic)
    
    ##
    
    #TODO: make instance for each filter
    
    def get_context(self):
        'for overriding'
        return self.context

    '''
    Assume we use method markers, smth. like
    ...
    '''
    
    def _add_queryset_arg(self, method):
        def callabl(queryset):
            self.context.queryset = queryset
            return method()
        return callabl

    def make_filter(self, callabl):
        '''
        `method` is an instance method made to accept queryset argument
        '''
        marker_args = method.marker_args
        marker_kwargs = method.marker_kwargs
        
        if marker_args and marker_args[0] == 'filter_function':
            return lambda self: None
        return filter_types.QFilter
        
    def make_callable(self, method):
        1


#    @classmethod
#    def get_filter_class(cls, method_marker):
#        '''Method markers are strings in the simplest case.'''
#        if method_marker == 'filter function':
#            return filter_types.ValuesDictFilter
#        if method_marker == 'iteration hook':
#            return filter_types.QuerysetIterationHook
#        return filter_types.QFilter

    @classmethod
    def is_filter_method(cls, name):
        return name.startswith('filter__')

    @classmethod
    def _get_methods_names(cls):
        attrs = dir(cls)
        def filter_func(name):
            method = getattr(cls, name)
            return inspect.ismethod(method) and cls.is_filter_method(name)
        return filter(filter_func, attrs)

#

