from django.contrib.auth.models import User
from django.db import models


class RecipeAuthor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
