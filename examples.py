# -*- coding: utf-8 -*-
"""
Created on Sat May 10 11:44:15 2014

@author: vitalii
"""

#%%
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'catsbreed.settings'
import django
from django.db.models import Q
#%%
import containers, filters
from dec import make_filter
#%%

class MyFilters(containers.MethodFilter):
    
    @make_filter(filters.ValuesDictFilter, fields_list=['value'])
    def filter__2(self, obj):
        return obj['value'] == 2
    
    def filter__1_2(self):
        return Q(value=2)

#%%
from qfilters.models import Luck
fi = MyFilters()
#%%
fi(Luck.objects.all())