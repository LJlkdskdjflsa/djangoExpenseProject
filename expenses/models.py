from django.db import models
from django.contrib.auth.models import User
#from django.utils.timezone import now
import datetime


class Expense(models.Model):
    now = datetime.datetime.now()

    amount = models.FloatField()
    date = models.DateField(models.DateField)
    description = models.TextField()
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    category = models.CharField(max_length=255)

    def __str__(self):
        return self.category

    class Meta:
        ordering: ['-date']


class Category(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = 'Categories'
        # set the showing of Category

    def __str__(self):
        return self.name
