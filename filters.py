# -*- coding: utf-8 -*-

import inspect
import filter_types
import filter_factory
import operator


from django.db.models import Q, query


def make_filter(*args, **kwargs):
    '''
    Decorator for `FilterContainer` filtering methods.
    '''
    def decor(func):
        func.make_filter_args = args
        func.make_filter_kwargs = kwargs
        return func
    return decor

#%%
class FilterContainer(object):

    combine = operator.and_
    ##
    
#    @property
#    def queryset(self):
#        return self.context['queryset']


    def __init__(self, context={}, *args, **kw):
        if 'method_name' not in kw:
            self._init_all(context, *args, **kw)
            return
        self._filter = None
        self.method_name = kw['method_name']
        self.context = context
        method = getattr(self, kw['method_name'])
        default_filter_class = filter_types.QFilter
        make_filter_args = getattr(method, 'make_filter_args',
                                   (default_filter_class,))
        filter_class, make_filter_args = make_filter_args[0], make_filter_args[1:]
        make_filter_kwargs = getattr(method, 'make_filter_kwargs', {})
        self._filter = filter_factory.make_filter(filter_class, self,
                                                 *make_filter_args, **make_filter_kwargs)

    ## Delegate filtering to _filter

    def __call__(self, queryset):
        return self._filter(queryset)
    
    def __and__(self, other):
        return self._filter & other
    
    def __or__(self, other):
        return self._filter | other

    ##
    
    def __repr__(self):
        try:
            return '%s (%s)' % (self.method_name, self._filter.__class__)
        except AttributeError:
            return super().__repr__()
    
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
    
#    def __call__(self):
#        return reduce(self.combine, self._filters, query.EmptyQuerySet())
    
    @classmethod
    def is_filter_method(cls, name):
        return name.startswith('filter__')

    @classmethod
    def _get_methods_names(cls):
        attrs = dir(cls)
        return filter(lambda name: cls.is_filter_method(name),
                      attrs)
#%%
#import os
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hvost.settings")
#import django
#django.setup()
##%%
#from qfilters.models import Luck
#Luck.objects.filter(value=1)
#%%


class MyFilters(FilterContainer):
    
    def filter__method(self):
        return Q(value=1)

#%%
filters = MyFilters()
#%%
#inspect.ismemberdescriptor(getattr(MyFilters, 'filter__method'))

#%%
#%%










