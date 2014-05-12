# -*- coding: utf-8 -*-

#%%
import os
os.environ['DJANGO_SETTINGS_MODULE']='catsbreed.settings'
import django
django.setup()
#%%
from main.models import CatsBreed, Dog, Dummy
#dog = Dog.objects.create(weight=20, breed=u'Бульдог')
#dog
#%%
siam = CatsBreed.objects.all()[4]
#dummy = Dummy.objects.create(field='field')
siam.dummy.field
#siam.save()
#%%
qs=CatsBreed.objects.all()
print qs
#%%
class A(object):
    @property
    def p(self):
        return 1

o = A()
#%%
help(A.p.fget)

