from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Tournament(models.Model):
    name = models.CharField(max_length=264)
    start_date = models.DateField(null=True)
    field_json_url = models.URLField(null=True)
    score_json_url = models.URLField(null=True)

    def get_queryset(self):
        return self.objects.filter().first()

    def __str__(self):
        return self.name

class Field(models.Model):
    playerName = models.CharField(max_length = 256)
    currentWGR = models.IntegerField(unique=False, null=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    group = models.ForeignKey('Group', on_delete=models.CASCADE)
    alternate = models.NullBooleanField(null=True)

    class Meta:
        ordering = ['group', 'currentWGR']

    def __str__(self):
        return  self.playerName

    def get_absolute_url(self):
        return reverse("golf_app:show_picks",kwargs={'pk':self.pk})

    def get_group(self, args):
        group = self.objects.filter(group=args)
        return group

class Name(models.Model):
    OWGR_name = models.CharField(max_length=256)
    PGA_name = models.CharField(max_length=256)

    def __str__(self):
        return self.OWGR_name


class Picks(models.Model):
    playerName = models.ForeignKey(Field, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(null=True)

    class Meta():
        unique_together = ('playerName', 'user')

    def __str__(self):
        return str(self.user) if self.user else ''


class Group(models.Model):
    number = models.PositiveIntegerField()
    playerCnt = models.PositiveIntegerField()

    def __str__(self):
        return str(self.number)


class ScoreDetails(models.Model):
    user = models.CharField(max_length=100)
    player = models.CharField(max_length=256)
    score = models.PositiveIntegerField()
    toPar = models.CharField(max_length=10, null=True)
    today_score = models.CharField(max_length = 10, null=True)
    thru = models.CharField(max_length=100, null=True)
    sod_position = models.CharField(max_length=30, null=True)

class BonusDetails(models.Model):
    user = models.CharField(max_length=100)
    winner_bonus = models.IntegerField(null=True)
    cut_bonus = models.IntegerField(null=True)


class TotalScore(models.Model):
    user = models.CharField(max_length=100)
    score = models.PositiveIntegerField()

    def __str__(self):
        return self.user + str(self.score)
