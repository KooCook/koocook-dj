from django.db import models

__all__ = ['Tag', 'TagLabel']


class Tag(models.Model):
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


class TagLabel(models.Model):
    """Represents a ``label`` (category) of tags.

    Some examples of valid use cases:
        <Label: allergen>, <label: diet>, <Label: warning>,
        <Label: clearance>, <Label: celebration>, <Label: cuisine>,

    Attributes:
        name (str): name of the label
        tag_set (RelatedManager): from ForeignKey in ``Tag``
    """
    name = models.CharField(max_length=50)
