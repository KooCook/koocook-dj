from django.db import models

from .base import SerialisableModel

__all__ = ['Tag', 'TagLabel']


class Tag(SerialisableModel, models.Model):
    """Represents a ``tag`` of recipes.

    Some examples of valid use cases:
        <Tag: French, <Label: cuisine>>,
        <Tag: gluten-free, <Label: clearance>>,
        <Tag: seafood, <Label: allergen>>,

    Attributes:
        name (str): name of the tag
        recipe_set (RelatedManager): from ManyToMany in ``Recipe``
    """
    name = models.CharField(max_length=50)
    label = models.ForeignKey('koocook_core.TagLabel', null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        try:
            tag = Tag.objects.get(name__exact=self.name, label__exact=self.label)
        except Tag.DoesNotExist:
            super().save(force_insert, force_update, using, update_fields)
        else:
            raise ValueError(f'tag `name` and `label` together must be unique, '
                             f"another tag '{tag}' already exists")

    @property
    def as_dict(self) -> dict:
        di = super().as_dict
        di.update({'done': 'true'})
        return di

    def __str__(self):
        return self.name


class TagLabel(SerialisableModel, models.Model):
    """Represents a ``label`` (category) of tags.

    Some examples of valid use cases:
        <Label: allergen>, <label: diet>, <Label: warning>,
        <Label: clearance>, <Label: celebration>, <Label: cuisine>,

    Attributes:
        name (str): name of the label
        tag_set (RelatedManager): from ForeignKey in ``Tag``
    """
    name = models.CharField(max_length=50)
    level = models.IntegerField(default=1)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        try:
            label = TagLabel.objects.get(name__exact=self.name)
        except TagLabel.DoesNotExist:
            super().save(force_insert, force_update, using, update_fields)
        else:
            raise ValueError(f'label `name` must be unique, another label '
                             f"'{label}' already exists")
    # tag_set from Tag's ForeignKey

    def __str__(self):
        return self.name
