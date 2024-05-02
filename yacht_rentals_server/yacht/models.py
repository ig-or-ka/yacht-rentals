from django.db import models
from django.contrib.auth.models import User
import enum


class RequestStatus(enum.Enum):
    new = 0
    allow = 1
    deny = 2


class UserRole(enum.Enum):
    user = 0
    clerk = 1


class Yacht(models.Model):
    name = models.TextField()
    rent_price = models.IntegerField()
    available = models.BooleanField(default=True)


class UserInfo(models.Model):
    user = models.ForeignKey(User, models.PROTECT)
    user_role = models.IntegerField(default=UserRole.user.value)
    current_yacht = models.ForeignKey(Yacht, models.PROTECT, blank=True, null=True)
    balance = models.IntegerField(default=0)


class Request(models.Model):
    status = models.IntegerField(default=0)
    yacht = models.ForeignKey(Yacht, models.PROTECT)
    user = models.ForeignKey(UserInfo, models.PROTECT)
    time_req = models.TimeField()
    get = models.BooleanField()
    from_time = models.TimeField()
    to_time = models.TimeField()
    answer = models.TextField(default="")