#coding: utf-8
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
#%%

# Create your models here.

class CatsBreed(models.Model):
    name = models.CharField(max_length=20)
    good_hunter = models.NullBooleanField()
    can_live_with = models.ManyToManyField('Animal', null=True)
    fur = models.CharField(u'Тип шерсти', max_length=20,
                           choices = (
                               (u'К', u'Короткошёрстная',),
                               (u'Д', u'Длинношёрстная',),
                               (u'С', u'Сфинкс')
                           ))
    weight_min = models.FloatField(u'Вес от, кг', null=True)
    weight_max = models.FloatField(u'Вес до, кг', null=True)
    # если не указывать мин и макс
    weight = models.FloatField(u'Вес, кг', null=True)
    traits = models.CharField(u'Отличительные черты в свободной форме',
                              max_length=1000, null=True)
    
    def __unicode__(self):
        return self.name


class Animal(models.Model):
    weight = models.FloatField(u'Вес, кг', null=True)

class Dog(Animal):
    breed = models.CharField(max_length=20)