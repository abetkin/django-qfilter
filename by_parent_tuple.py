# -*- coding: utf-8 -*-


class as_object(dict):
    '''
    self.__dict__ is self.
    '''
    
    def __init__(self, *args, **kw):
        super(as_object, self).__init__(*args, **kw)
        self.__dict__ = self

#%%

def make_nested_object(values_dict):
    values_dict = {tuple(key.split('__')): value
                   for key, value in values_dict.items()}

#%%
values_dict = {tuple(key.split('__')): value for key, value in {
    'aa': 1,
    'a__bb': 2,
    'a__b__c': 3,
    'a__b__d': 4,
}.items()}

class merge_values(dict):
    '''
    Assume values in a dict are dicts. When setting value for key with existing value
    merge values (i.e. dicts) instead of ovewriting the old one.
    '''  
    
    def __setitem__(self, key, value):
        if self.get(key):
            value = self.fromitems(self[key].items() + value.items())
        super(merge_values, self).__setitem__(key, value)
    
    @classmethod
    def fromitems(cls, items):
        dic = None
        for key, value in items:
            if not dic:
                dic_type = type('special_%s' % value.__class__.__name__,
                              (cls, value.__class__),
                              {})
                dic = dic_type(key=value)
            assert isinstance(dic, value.__class__), 'Items must be of the same type'
            dic[key] = value
        return dic
        
#%%
def by_parent_tuple(tuples_dict):
    for tupl, value in values_dict.items():
        if not tupl:
            yield tupl, value
        else:
            yield tupl[:-1], as_object({tupl[-1]: value})
items = list(by_parent_tuple(values_dict))
print items

#%%
o = items[0][1]
p = items[1][1]
print o
print p
#%%
q = o.__class__(o.items() + u.items())
q
#%%
values_dict = merge_values.fromitems(items)
values_dict
#%%
#tuples_dict = dict(tuples)

tuples = values_dict.keys()
tuples