from django.db import models
from django.contrib.auth.models import User


class Yacht(models.Model):
    name = models.TextField()
    rent_price = models.IntegerField()
    available = models.BooleanField(default=True)


class Request(models.Model):
    yacht = models.ForeignKey(Yacht, models.PROTECT)
    time_req = models.TimeField()
    get = models.BooleanField()
    from_time = models.TimeField()
    to_time = models.TimeField()


class UserInfo(models.Model):
    user = models.ForeignKey(User, models.PROTECT)
    current_yacht = models.ForeignKey(Yacht, models.PROTECT, blank=True, null=True)
    balance = models.IntegerField(default=0)