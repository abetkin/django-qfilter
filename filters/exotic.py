# -*- coding: utf-8 -*-
from itertools import groupby

from .base import ValuesDictFilter

class Attribute(object):

    _empty = True # does not contain other attributes

    def __init__(self, name=None, values_dict=None):
        self.name = name
        self._dict = values_dict
    
    @classmethod
    def make_class_from_fields_list(cls, fields_list, parent_field=None):
        fields_list = filter(None, fields_list)
        if not fields_list:
            return cls
        result = type('%s_%s' % (parent_field or 'root', cls.__name__),
                          (cls,), {})
        head__tail = [field.partition('__') for field in fields_list]
        
        for head, head__tail in groupby(head__tail, key=lambda t: t[0]):
            if not parent_field:
                parent = head
            else:
                parent = '__'.join([parent_field, head])
            attr_class = cls.make_class_from_fields_list(
                    (parts[-1] for parts in head__tail),
                    parent_field=parent)
            setattr(result, head, attr_class(parent))
            result._empty = False
        return result
    
    def get_value(self):
        assert self._dict and self.name in self._dict, str(self._dict.items()) + str(self.name)
        value = self._dict[self.name]
        if hasattr(self.name, 'transform'):
            value = self.name.transform(value)
        return value
    
    def __get__(self, instance, owner):
        if not instance:
            return self
        self._dict = instance._dict
        return self if not self._empty else self.get_value()


class PropertyBasedFilter(ValuesDictFilter):
    
    def __init__(self, filter_func, fields_list=None, properties=None):
        super(PropertyBasedFilter, self).__init__(filter_func, fields_list)
        if properties:
            self.properties = properties
    
    def _fetch_objects(self, queryset):
        fields_list = ['pk'] + self.fields_list
        Object = Attribute.make_class_from_fields_list(fields_list)
        
        def get_related_model(model, field_name):
            return getattr(model, field_name).field.related.parent_model
        
        for property_name in self.properties:
            split_name = property_name.split('.')
            model_class = reduce(lambda model, field: get_related_model(model, field),
                                 split_name[:-1],
                                 queryset.model)
            if not split_name[:-1]:
                attribute_class = Object
            else:
                get_attr = lambda cls, name: getattr(cls, name).__class__
                attribute_class = reduce(get_attr, split_name[:-1], Object)
            prop = getattr(model_class, split_name[-1])
            setattr(attribute_class, split_name[-1], property(prop.fget))
        
        objects = queryset.values(*fields_list)
        return [Object(values_dict=dic) for dic in objects]