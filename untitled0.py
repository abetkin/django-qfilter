# -*- coding: utf-8 -*-
import abc
#%%

class A(object):
    
    def __init__(self, a):
        self.a = a

def from_bases(tupl):
    'klass'


klasses = {}

class Builder(object):
    
    @singledispatch
    def __init__(self):
        1