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
    
    _filter = None
    
#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#        self.context = self.get_context()
    
    
    def __init__(self, method_name):
        classes = (self.__class__, 'choose')
    
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
        new instance of (FiltersContainer, <resp. filter>)
        '''
    

    def make_callable(self, method):
        1
    
    ## Filter interface

    def __call__(self, queryset):
        return self._filter(queryset)
    
    def __and__(self, other):
        return self._filter & other
    
    def __or__(self, other):
        return self._filter | other

    ##

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



'''
__new__:
    new instance from method_name
    -> new filter instance
    inst1.__class__ = 1
    register as filter class
    return inst1

'''