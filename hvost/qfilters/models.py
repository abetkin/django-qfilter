from django.db import models

# Create your models here.

class Luck(models.Model):
    value = models.IntegerField()
    