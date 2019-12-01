from django.db import models

from .base import SerialisableModel

__all__ = ['Tag', 'TagLabel']


class Tag(SerialisableModel, models.Model):
    name = models.CharField(max_length=50)
    label = models.ForeignKey('koocook_core.TagLabel', null=True, blank=True, on_delete=models.SET_NULL)
    # recipe_set from Recipe's ManyToMany

    @property
    def as_dict(self) -> dict:
        di = super().as_dict
        di.update({'done': 'true'})
        return di

    def __str__(self):
        return self.name


class TagLabel(SerialisableModel, models.Model):
    name = models.CharField(max_length=50)
    level = models.IntegerField(default=1)
    # tag_set from Tag's ForeignKey

    def __str__(self):
        return self.name
