from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


# Create your models here.

class Season(models.Model):
    season = models.CharField(max_length=10)
    current = models.BooleanField()

    def __str__(self):
        return self.season

class Tournament(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    name = models.CharField(max_length=264)
    start_date = models.DateField(null=True)
    field_json_url = models.URLField(null=True)
    score_json_url = models.URLField(null=True)
    current = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)
    pga_tournament_num = models.CharField(max_length=10)

    def get_queryset(self):
        return self.objects.filter().first()

    def __str__(self):
        return self.name


class Group(models.Model):
    tournament= models.ForeignKey(Tournament, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    playerCnt = models.PositiveIntegerField()

    def __str__(self):
        return str(self.number)


class Field(models.Model):
    playerName = models.CharField(max_length = 256)
    currentWGR = models.IntegerField(unique=False, null=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(null=True)

    class Meta():
        unique_together = ('playerName', 'user')

    def __str__(self):
        return str(self.playerName) if self.playerName else ''

    def is_winner(self):
        winner = ScoreDetails.objects.get(pick=self, score=1)
        print (winner)
        if (self.playerName == winner.pick.playerName and self.playerName.tournament.complete):
           return True
        else:
           return False


class ScoreDetails(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pick = models.ForeignKey(Picks, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(null=True)
    toPar = models.CharField(max_length=10, null=True)
    today_score = models.CharField(max_length = 10, null=True)
    thru = models.CharField(max_length=100, null=True)
    sod_position = models.CharField(max_length=30, null=True)

    def __str__(self):
        return str(self.user) + str(self.pick) + str(self.score)


class BonusDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=True)
    winner_bonus = models.IntegerField(null=True)
    cut_bonus = models.IntegerField(null=True)


class TotalScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=True)
    score = models.IntegerField(null=True)

    class Meta():
        unique_together = ('tournament', 'user')

    def __str__(self):
        return str(self.user) + str(self.score)

    
