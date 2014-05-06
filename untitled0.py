# -*- coding: utf-8 -*-
import abc
#%%

class A(object):
    
    __metaclass__ = abc.ABCMeta
    
    def __init__(self):
        self.a = 1
    

class B(A):
    def f(self):
        return 1
    
class C(object):
    def f(self):
        return 'c'

#%%
c.f()
#%%

c = C()
b = B()
B.register(C)
