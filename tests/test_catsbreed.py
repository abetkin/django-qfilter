# -*- coding: utf-8 -*-
import django
import os
from django.db.models import Q
from unittest import TestCase
import operator
from collections import namedtuple

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
        
        @PropertyBasedFilter('@',
                 fields_list=['traits__weight', 'traits__weight_max'], 
                 properties=['traits.kg'])
        def light_cats(obj):
            return obj.traits.kg < 3
        yield 'light_cats', light_cats
    
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
        light_cats = self.filters['light_cats']
        qs = light_cats(self.CatsBreed.objects.all())
        assert qs.exists() and qs.count() < self.CatsBreed.objects.count()
    
    def test_PropertyBasedFilter_exotic(self):
        
        class ManyRelatedManager(str):
            Exists = namedtuple('Exists', ['exists'])
            
            def transform(self, pk):
                return self.Exists(lambda: True) if pk else self.Exists(lambda: False)
        
        @PropertyBasedFilter('@',
                 fields_list=[ManyRelatedManager('can_live_with')], 
                 properties=['can_live_with_other_animals'])
        def social_cats(obj):
            return obj.can_live_with_other_animals
        
        count = self.CatsBreed.objects.count()
        assert social_cats(self.CatsBreed.objects.all()).count() <= count // 2
    
    def tesT_inversion_for_filter(self, name):
        filtr = self.filters[name]
        qs_all = self.CatsBreed.objects.all()
        filtered = filtr(qs_all)
        rest = (~filtr)(qs_all)
        assert filtered.count() + rest.count() == qs_all.count()
    
    def test_invertion(self):
        for name in 'qfilter', 'hunter_skills', 'light_cats':
            yield self.tesT_inversion_for_filter, name
    
    def tesT_combinations(self, name1, name2, op):
        f = self.filters[name1]
        g = self.filters[name2]
        combined = op(f, g)
        qs_all = self.CatsBreed.objects.all()
        assert combined(qs_all).count() == op(f(qs_all), g(qs_all)).count()
    
    def test_combinations(self):
        for op in (operator.and_, operator.or_):
            for name1 in ('qfilter', 'hunter_skills', 'light_cats'
            ):
                for name2 in ('qfilter', 'hunter_skills', 'light_cats'
                ):
                    yield self.tesT_combinations, name1, name2, op
