from django.db import models

# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=70, blank=True)
    phone = models.CharField(max_length=20, blank=True)