from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from koocook_core.support.label import Label

__all__ = ['Tag', 'Label']


class Tag(models.Model):
    name = models.CharField(max_length=63)
    label = models.IntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(len(Label)),
    ], null=True, blank=True)
    # recipe_set from Recipe's ManyToMany