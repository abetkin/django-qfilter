# -*- coding: utf-8 -*-
import django
import os
from django.db.models import Q
from unittest import TestCase

print 'PP:', os.environ.get('PYTHONPATH')

from filters import *

class BareFiltersTests(TestCase):

    @classmethod
    def setUpClass(cls):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'catsbreed.settings'
        django.setup()
        from main.models import CatsBreed
        cls.CatsBreed = CatsBreed
        cls.filters = dict(cls.create_filters())
    
    def test_cats_exist(self):
        assert self.CatsBreed.objects.count() > 3
    
    @classmethod
    def create_filters(cls):
        @QFilter
        def qfilter(qs):
            return Q(name=u'Персидская')
        yield 'qfilter', qfilter
        
        @QuerysetIterationHook
        def mark(obj):
            obj.marked = True
        yield 'mark_filter', mark
        
        @ValuesDictFilter('@', fields_list=['traits__good_hunter'])
        def not_very_good_hunters(obj):
            return obj['traits__good_hunter'] is False
        yield 'hunter_skills', not_very_good_hunters
    
    def test_QFilter_basic(self):
        f = self.filters['qfilter']
        qs = f(self.CatsBreed.objects.all())
        assert qs.count() == 1 and qs[0].name == u'Персидская'

    def test_QuerysetIterationHook_basic(self):
        f = self.filters['mark_filter']
        qs = f(self.CatsBreed.objects.all())
        assert qs.count() == self.CatsBreed.objects.count()
        for cat in qs:
            assert hasattr(cat, 'marked')
        
    def test_ValuesDictFilter_basic(self):
        # more than a half should be good hunters
        f = self.filters['hunter_skills']
        qs = f(self.CatsBreed.objects.all())
        assert qs.count() * 2 <= self.CatsBreed.objects.count()

    def test_PropertyBasedFilter(self):
        @PropertyBasedFilter('@',
                             fields_list=['traits__weight', 'traits__weight_max'], 
                             properties=['traits.kg'])
        def light_cats(obj):
            return obj.traits.kg < 3

        qs = light_cats(self.CatsBreed.objects.all())
        assert qs.exists() and qs.count() < self.CatsBreed.objects.count()
#%%


'TODO: test ~qs'

#
#(my_filter & filtr)(BankCompany.objects.all())





#
##%%
#
##with ipdb.launch_ipdb_on_exception():
#@ValuesDictFilter(fields_list=[])
#def filtr(obj):
#    return obj['pk'] == 11978
#
#@ValuesDictFilter(fields_list=['region_list__city_type'])
#def fname(obj):
#    return obj['region_list__city_type']
##    return obj['company_name'] in (u'Альфа-Банк', u'Абсолют Банк', u'Авангард')
#
#
##%%
#import operator
#from unicom.crm.models import BankCompany
#f = filtr & fname
#f
#
##%%
##BankCompany.objects.get(pk=11978).company_name
#qs = f(BankCompany.objects.all())
#qs.count()
#
##%%
#
#@QuerysetIterationHook
#def set_hvost(obj):
#    obj.hvost = 30
#
#@QuerysetIterationHook
#def set_color(obj):
#    obj.color = 'grey'
#
#f = set_color | set_hvost
#
##%%
#
#qs = f(BankCompany.objects.filter(id=11978))
#qs[0].color + ' ' + str(qs[0].hvost)
##%%
#
##%%
#
#'Init project'
#
#import os
#os.environ['DJANGO_SETTINGS_MODULE'] = 'unicom.settings'
#

#
##%%
#
#@QFilter
#def my_filter(queryset):
#    return BankCompany.objects.filter(id__in=(11949, 11978))
#
# Q(id=11978)

#%%
#
#(my_filter & filtr)(BankCompany.objects.all())
#
###%%
##'test QFilter'
##
##q_filter = QFilter(Q(id=11949))
##qs = queryset = BankCompany.objects.all()
##q_filter(qs)
##
##%%
#'test SimpleQuerysetFilter'
#
#qs = BankCompany.objects.filter(id=11949)
#qsfilter = SimpleQuerysetFilter(qs)
#qsfilter(qs)
#
#%%
#'test ValuesDictFilter'
#
#values_filter = ValuesDictFilter([], lambda obj: obj['pk']==11949)
#values_filter(queryset)
##%%
#'test QuerysetIterationHook'
#
#qs = BankCompany.objects.all()[:5]
#def hook_func(obj):
#    print obj.pk
#    return obj
#
#iter_hook = QuerysetIterationHook(hook_func)
#nu = iter_hook(qs)
#nu
#
#%%