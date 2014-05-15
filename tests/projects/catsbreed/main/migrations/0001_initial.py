# encoding: utf8
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name=b'Traits',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (b'good_hunter', models.NullBooleanField()),
                (b'weight_min', models.FloatField(null=True, verbose_name='\u0412\u0435\u0441 \u043e\u0442, \u043a\u0433')),
                (b'weight_max', models.FloatField(null=True, verbose_name='\u0412\u0435\u0441 \u0434\u043e, \u043a\u0433')),
                (b'weight', models.FloatField(null=True, verbose_name='\u0412\u0435\u0441, \u043a\u0433')),
                (b'text', models.CharField(max_length=1000, null=True, verbose_name='\u041e\u0442\u043b\u0438\u0447\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u0435 \u0447\u0435\u0440\u0442\u044b \u0432 \u0441\u0432\u043e\u0431\u043e\u0434\u043d\u043e\u0439 \u0444\u043e\u0440\u043c\u0435')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name=b'Animal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (b'weight', models.FloatField(null=True, verbose_name='\u0412\u0435\u0441, \u043a\u0433')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name=b'CatsBreed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                (b'name', models.CharField(max_length=20)),
                (b'fur', models.CharField(max_length=20, verbose_name='\u0422\u0438\u043f \u0448\u0435\u0440\u0441\u0442\u0438', choices=[('\u041a', '\u041a\u043e\u0440\u043e\u0442\u043a\u043e\u0448\u0451\u0440\u0441\u0442\u043d\u0430\u044f'), ('\u0414', '\u0414\u043b\u0438\u043d\u043d\u043e\u0448\u0451\u0440\u0441\u0442\u043d\u0430\u044f'), ('\u0421', '\u0421\u0444\u0438\u043d\u043a\u0441')])),
                (b'traits', models.OneToOneField(to=b'main.Traits', to_field='id')),
                (b'can_live_with', models.ManyToManyField(to=b'main.Animal', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name=b'Dog',
            fields=[
                ('animal_ptr', models.OneToOneField(auto_created=True, primary_key=True, to_field='id', serialize=False, to=b'main.Animal')),
                (b'breed', models.CharField(max_length=20)),
            ],
            options={
            },
            bases=(b'main.animal',),
        ),
    ]
