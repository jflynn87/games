from django.db import models
from django.db.models.base import Model
from django.contrib.auth.models import User
# Create your models here.

class Event(models.Model):
    name = models.CharField(max_length=200)
    year = models.IntegerField(null=True)
    current = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)
    set_started = models.BooleanField(default=False)
    set_not_started = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)


class Group(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    group = models.CharField(max_length=20)

    def __str__(self):
        return str(self.group)


class Team(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    rank = models.IntegerField(default=0)
    flag_link = models.URLField(null=True, blank=True)
    info_link = models.URLField(null=True, blank=True)
    full_name = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return str(self.name)


class Picks (models.Model):
    CHOICES = (('1', 'Group'), ('2', 'Knock-out'))
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wc_user')
    stage = models.CharField(max_length=100, choices=CHOICES)
    rank = models.IntegerField()
    def __str__(self):
        return str(self.user.username) + ' ' + str(self.team)
