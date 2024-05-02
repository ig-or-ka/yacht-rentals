from django.db import models


class Yacht(models.Model):
    name = models.TextField()
    rent_price = models.IntegerField()
    available = models.BooleanField()