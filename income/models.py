from django.db import models
from django.contrib.auth.models import User
#from django.utils.timezone import now
import datetime


class Income(models.Model):
    now = datetime.datetime.now()

    amount = models.FloatField()
    date = models.DateField(models.DateField)
    description = models.TextField()
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    source = models.CharField(max_length=255)

    def __str__(self):
        return self.source

    class Meta:
        ordering: ['-date']


class Source(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
