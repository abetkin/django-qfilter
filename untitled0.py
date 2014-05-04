# -*- coding: utf-8 -*-

#%%



#%%

class as_object(dict):
    def __init__(self, *args, **kw):
        super(as_object, self).__init__(*args, **kw)
        self.__dict__ = self

class A(object):
    
    @property
    def context(self):
        return self._context
    
    @context.setter
    def context(self, dic):
        assert isinstance(dic, dict)
        self._context = as_object(dic)
        
a = A()
a.context = {'at': 4}
#%%

{1: 1}.keys()