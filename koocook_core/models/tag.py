from django.db import models

__all__ = ['Tag', 'TagLabel']


class Tag(models.Model):
    name = models.CharField(max_length=50)
    label = models.ForeignKey('koocook_core.TagLabel', null=True, blank=True, on_delete=models.SET_NULL)
    # recipe_set from Recipe's ManyToMany


class TagLabel(models.Model):
    name = models.CharField(max_length=50)
    level = models.IntegerField(default=0)
    # tag_set from Tag's ForeignKey
