# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations

def fill_dogs(apps, schema_editor):
    CatsBreed = apps.get_model('main', 'CatsBreed')
    Dog = apps.get_model('main', 'Dog')
    bulldog, created = Dog.objects.get_or_create(breed=u'Бульдог')
    dachshund, created = Dog.objects.get_or_create(breed=u'Такса')
    CatsBreed.objects.get(name=u'Сиамская').can_live_with.add(bulldog, dachshund)

class Migration(migrations.Migration):

    dependencies = [
        (b'main', b'0002_fill_cat_breeds'),
    ]

    operations = [
        migrations.RunPython(fill_dogs)
    ]
