# -*- coding: utf-8 -*-
"""
Created on Sat May 10 11:44:15 2014

@author: vitalii
"""

#%%
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'hvost.settings'
import django
from django.db.models import Q
#%%
import containers, filters
from dec import make_filter
#%%

class MyFilters(containers.MethodFilter):
    
    @make_filter(filters.ValuesDictFilter, fields_list=['value'])
    def filter__method(self, obj):
        return obj['value'] == 1
#%%

from qfilters.models import Luck
m = list(MyFilters())[0]
for luck in m(Luck.objects.all()):
    print luck.value,