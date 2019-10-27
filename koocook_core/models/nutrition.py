from django.core.validators import MinValueValidator
from django.contrib.postgres.fields import ArrayField
from django.db import models


class NutritionInfo(models.Model):
    calories = models.IntegerField(validators=[MinValueValidator(0)])


class Ingredient(models.Model):
    pass
