import enum

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


@enum.unique
class Label(enum.Enum):
    WARNING = enum.auto()
    CLEARANCE = enum.auto()
    CUISINE = enum.auto()
    CATEGORY = enum.auto()


class Tag(models.Model):
    name = models.CharField(max_length=63)
    label = models.IntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(len(Label)),
    ])
    # recipe_set from Recipe's ManyToMany
