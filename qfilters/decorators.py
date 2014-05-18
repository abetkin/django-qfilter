# -*- coding: utf-8 -*-

'''
Decorators.
'''


def make_filter(*args, **kwargs):
    '''
    Decorator for `MethodFilter` filtering methods.
    '''
    def decorate(func):
        func.make_filter_args = args
        func.make_filter_kwargs = kwargs
        return func
    return decorate