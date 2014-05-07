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

#    def __init__(self, **kwargs):
#        self.__dict__.update(kwargs)
#        self.context = self.get_context()



    '''
    Assume we use method markers, smth. like
    ...
    '''

    ## context attribute

    _context = {}

    
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
        
    ##
        
    def __init__(self, method_name, filter_class):
        pass

#    def filter_factory(cls, )


    def make_filter(self, callabl):
        '''
        new instance of (FiltersContainer, <resp. filter>)
        '''
    

    def make_callable(self, method):
        1
    
    ## Filter interface
    
    _filter = None

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

#%%

from functools import singledispatch

#%%

#XXX enum?

## Filter factories

@singledispatch
def make_filter(klass, method):
    pass

@make_filter.register(filter_types.QFilter)
def make_qfilter(klass, method):
    1

'''
__new__:
    new instance from method_name
    -> new filter instance
    inst1.__class__ = 1
    register as filter class
    return inst1

-------
contxt_obj registers itself as a filter it wants to be
than is called to_filter(context_obj) dispatching on the registered class.


'''

