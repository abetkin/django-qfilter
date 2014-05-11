# -*- coding: utf-8 -*-

#%%
import os
os.environ['DJANGO_SETTINGS_MODULE']='catsbreed.settings'
import django
django.setup()
#%%
from main.models import CatsBreed
#%%

#%%
qs=CatsBreed.objects.all()

class A(object):
    @property
    def p(self):
        return 1

o = A()
#%%
help(A.p.fget)

