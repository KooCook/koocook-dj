from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from koocook_core.support.label import Label


class Tag(models.Model):
    name = models.CharField(max_length=63)
    label = models.IntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(len(Label)),
    ])
    # recipe_set from Recipe's ManyToMany
