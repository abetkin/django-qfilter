# -*- coding: utf-8 -*-

import inspect
import filter_types
import filter_factory


def make_filter(*args, **kwargs):
    '''
    Decorator for `FilterContainer` filtering methods.
    '''
    def decor(func):
        func.make_filter_args = args
        func.make_filter_kwargs = kwargs
        return func
    return decor


class FilterContainer(object):

    ##
    
#    @property
#    def queryset(self):
#        return self.context['queryset']


    def __init__(self, context={}, *args, **kw):
        if 'method_name' not in kw:
            self._init_all(context, *args, **kw)
        self._filter = None
        self.method_name = kw['method_name']
        self.context = context
        filter_class, *make_filter_args = get(self, kw['method_name']).make_filter_args
        make_filter_kwargs = get(self, kw['method_name']).make_filter_kwargs
        filter_class.register(self)
        self._filter = filter_factory.make_filter(filter_class,
                                                  *make_filter_args,
                                                  **make_filter_kwargs)

    ## Delegate filtering to _filter

    def __call__(self, queryset):
        return self._filter(queryset)
    
    def __and__(self, other):
        return self._filter & other
    
    def __or__(self, other):
        return self._filter | other

    ##
    
    def __repr__(self):
        return '%s (%s)' % (self.method_name, self._filter.__class__)
    
    def _init_all(self, context, *args, **kw):
        self._filters = []
        for method_name in self._get_methods_names():
            self._filters.append(
                    self.__class__(context, *args, method_name=method_name, **kw))
    
    def __iter__(self):
        try:
            return iter(self._filters)
        except AttributeError:
            raise Exception('Not a filter container')
    
    @classmethod
    def is_filter_method(cls, name):
        return name.startswith('filter__')

    @classmethod
    def _get_methods_names(cls):
        attrs = dir(cls)
        return filter(lambda name: inspect.ismethod(getattr(cls, name))
                                   and cls.is_filter_method(name),
                      attrs)

#%%
class A:
    1
o = A()
o
#%%
