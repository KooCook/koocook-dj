from django.core.validators import MinValueValidator
from django.contrib.postgres.fields import ArrayField
from django.db import models


class Nutrition(models.Model):
    calories = models.IntegerField(validators=[MinValueValidator(0)])


class Ingredient(models.Model):
    nutrition = models.OneToOneField(Nutrition, on_delete=models.CASCADE)
