# -*- coding: utf-8 -*-

#%%

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'unicom.settings'

#%%
from django.db.models import Q
#%%

from unicom.crm.models import BankCompany
BankCompany.objects.all()[0].pk

#%%

import sys
sys.path