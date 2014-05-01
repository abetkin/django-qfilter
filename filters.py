# -*- coding: utf-8 -*-
from django.db.query import Q
from functools import reduce
"""
Created on Sun Apr 27 22:52:07 2014

@author: vitalii
"""

import operator

class BaseFilter(object):
    
#    combine = ['AND', 'OR']
    
    def __init__(self, source=None, source_name=None):
        '''
        :param source:
            Source for this filter. Can be: Q object, queryset, filtering function.
            When using with QFilterBackend this is the return value of the filtering method.
        '''
        self.source = source
        self.source_name = source_name
        
    '''
    def __repr__(self):
        'will be overriden'
    '''

    def get_source_name(self):
        return str(self.source)
    
    # TODO define bit operations
    
    def apply(self, other, op):
        raise NotImplementedError()
    
    @classmethod
    def group(self, filters, operation):
        '''
        return filter
        group by filter type
        '''
        assert operation in self.combine
#    
#    def group_peers(other):1
#        
#    def group_all():1
    
    def __call__(self, queryset):
        raise NotImplementedError()
    

class ObjectFilter(BaseFilter):
    
    def filter__obj(self):
        def filter_func(obj):
            return 1
        return filter_func
    
    
class QFilter(BaseFilter):
    
    def __call__(self, queryset):
        return queryset.filter(self.source)
    
    @classmethod
    def group(cls, filters, operation):
        operation = {'OR': operator.or_,
                     'AND': operator.and_}
        q = reduce(operation, [f.source for f in filters])
        return QFilter(source=q, source_name='group %%')

    
    
class QuerysetFilter(BaseFilter):
    
    def __call__(self, queryset):
        return self.source
    
    @classmethod
    def group(cls, filters, operation):
        operation = {'OR': operator.or_,
                     'AND': operator.and_}
        qs = reduce(operation, [f.source for f in filters])
        return QFilter(source=q, source_name='group %%')

        
class FunctionFilter(BaseFilter):
    '''
    `source` is underlying filtering function::

        def filter_func(obj):
            return False or True
    '''
    
    def __call__(self, queryset):
        filter_func = self.source

        return self.queryset.all()
    
    def group():1
    
    '''
    def __init__(self, source=None, **context):
        super(FunctionFilter, self).__init__(source, **context)
        self.filter_func = source
    '''
    

# iteration
class QFilterBackend(object):
    
    group = True
    
    def filter_queryset(self, request, queryset, view):
        self.context = {
            'request': request,
            'queryset': queryset,
            'view': view,    
        }
    
    def get_filters(self):
        self.filters = []
    
    def apply(self, ctx):
        yield ()
    
    def is_filter_method(self, name, method=None):
        return (
            name.startswith('by_') or
            name.startswith('filter__')
        )



#
# Mode: do not combine, apply one by one
#

class Example(QFilterBackend):
    
    def filter__obj(self, obj, fields=['name']):
        if obj.name == 'stub':
            return
    
    def filter__q(self):
        def ids():
            for obj in self.queryset.values('id', 'name'):
                if obj['name'] == 'stub':
                    continue
                yield obj['id']
        return Q(id__in=list(ids()))
                    