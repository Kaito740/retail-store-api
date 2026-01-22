from django.db import models

# Create your models here.
class Customer(models.Model):
    name = models.CharField(max_length=70, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def save(self,*args,**kwargs):
        if self.name:
            self.name = self.name.strip()
        if not self.name:
            self.name = 'ANONIMO'

        if self.phone:
            self.phone = self.phone.strip()
        if not self.phone:
            self.phone = '000000000'
        self.full_clean()
        super().save(*args,**kwargs)