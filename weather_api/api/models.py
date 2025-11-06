from django.db import models
from django.contrib.auth.models import User


class UserCity(models.Model):
    # user = models.IntegerField(unique=True)
    user = models.CharField(max_length=100, unique=True)
    city = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user} - {self.city}"
