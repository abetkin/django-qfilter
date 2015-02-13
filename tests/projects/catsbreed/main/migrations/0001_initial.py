# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Animal',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('weight', models.FloatField(verbose_name='Вес, кг', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CatsBreed',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20)),
                ('fur', models.CharField(choices=[('К', 'Короткошёрстная'), ('Д', 'Длинношёрстная'), ('С', 'Сфинкс')], max_length=20, verbose_name='Тип шерсти')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Dog',
            fields=[
                ('animal_ptr', models.OneToOneField(to='main.Animal', parent_link=True, auto_created=True, serialize=False, primary_key=True)),
                ('breed', models.CharField(max_length=20)),
            ],
            options={
            },
            bases=('main.animal',),
        ),
        migrations.CreateModel(
            name='Traits',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('good_hunter', models.NullBooleanField()),
                ('weight_min', models.FloatField(verbose_name='Вес от, кг', null=True)),
                ('weight_max', models.FloatField(verbose_name='Вес до, кг', null=True)),
                ('weight', models.FloatField(verbose_name='Вес, кг', null=True)),
                ('text', models.CharField(max_length=1000, verbose_name='Отличительные черты в свободной форме', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='catsbreed',
            name='can_live_with',
            field=models.ManyToManyField(to='main.Animal', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='catsbreed',
            name='traits',
            field=models.OneToOneField(to='main.Traits'),
            preserve_default=True,
        ),
    ]
