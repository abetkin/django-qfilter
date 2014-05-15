#coding: utf-8
from django.db import models
#%%

class CatsBreed(models.Model):
    name = models.CharField(max_length=20)
    can_live_with = models.ManyToManyField('Animal', null=True)
    fur = models.CharField(u'Тип шерсти', max_length=20,
                       choices = (
                           (u'К', u'Короткошёрстная',),
                           (u'Д', u'Длинношёрстная',),
                           (u'С', u'Сфинкс')
                       ))
    traits = models.OneToOneField('Traits')

    @property
    def can_live_with_other_animals(self):
        return self.can_live_with.exists()
    
    def __unicode__(self):
        return self.name


class Traits(models.Model):
    good_hunter = models.NullBooleanField()
    weight_min = models.FloatField(u'Вес от, кг', null=True)
    weight_max = models.FloatField(u'Вес до, кг', null=True)
    # если не указывать мин и макс
    weight = models.FloatField(u'Вес, кг', null=True)
    text = models.CharField(u'Отличительные черты в свободной форме',
                              max_length=1000, null=True)

    @property
    def kg(self):
        return self.weight or self.weight_max


class Animal(models.Model):
    weight = models.FloatField(u'Вес, кг', null=True)

class Dog(Animal):
    breed = models.CharField(max_length=20)