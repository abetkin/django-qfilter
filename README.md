What it is
=========

Lightweight package for django which does the filtering of django querysets. The central object - a filter - is a callable that takes a queryset as a parameter and returns a queryset:

    filtered_queryset = filtr(Model.objects.all())

Django itself has a similar object - Q-object (`django.db.models.Q`). Q-objects can be combined toghether (with `|`, `&` operations) or inverted (`~`) and then passed to `queryset.filter`.

With `qfilters`, what you get in the most common case, is just a wrapper around the Q-object. However there are __2 features__ that may be the reasons to use the package:
    
__1. Support for additional filter types.__

For example, there is `ValuesDictFilter`, that is constructed from a field list, that will be passed to `queryset.values` and retrieve a list of dictionaries, and a filtering function, which accepts that dict as a parameter.

This filters can be combined or inverted in the same way Q-objects do, so that using multiple filters would result in a single call to `queryset.values`.

This is what it looks like in practice (all examples are taken from `qfilter` testsuite):
      
    @ValuesDictFilter('@', fields_list=['traits__good_hunter'])
    def nas_i_zdes_neploho_kormyat(obj):
        return obj['traits__good_hunter'] is False # because it can be None
    
    cats = nas_i_zdes_neploho_kormyat(self.CatsBreed.objects.all())
    assert cats.exists()
    
There are also exotic variants (`qfilters.exotic_types`) like `QuerysetIterationHook`, which appends attributes to objects when queryset is iterated over. Another one is `PropertyBasedFilter`, which can access object's attributes and even properties like it were a regular django model object. The implementation is not very straightforward, still it passes the tests so far. Here is what it looks like:
    
    class CatsBreed(models.Model):
        # ...
        traits = models.OneToOneField('Traits')

    class Traits(models.Model):
        #...
        weight_min = models.FloatField(u'Вес от, кг', null=True)
        weight_max = models.FloatField(u'Вес до, кг', null=True)
        # if you can't specify min and max 
        weight = models.FloatField(u'Вес, кг', null=True)

        def kg(self):
            return self.weight or self.weight_max
    
    
    from qfilters import PropertyBasedFilter
    
    @PropertyBasedFilter('@',
             fields_list=['traits__weight', 'traits__weight_max'], 
             properties=['traits.kg'])
    def light_cats(obj):
        return not obj.traits.kg or obj.traits.kg < 3
    
    assert light_cats(CatsBreed.objects.all()).exists()



