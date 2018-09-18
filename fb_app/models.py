from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.

class Week(models.Model):
    season = models.CharField(max_length=30)
    week = models.PositiveIntegerField()
    game_cnt = models.PositiveIntegerField()
    current = models.BooleanField(default=False)
    #start_date = models.DateField()
    #end_date = models.DateField()

    def __str__(self):
        return str(self.week)

    def save(self, *args, **kwargs):
        if self.current==True:
            last_week = Week.objects.get(current=True)
            last_week.current = False
            last_week.save()
        super(Week, self).save()


#class TeamManager(models.Manager):
#    def as_choices(self):
#        for team in self.all():
#            yield (team.pk, force_text(nfl_abbr))


class Teams(models.Model):
    mike_abbr = models.CharField(max_length=4, null=True)
    nfl_abbr = models.CharField(max_length=4, null=True)
    long_name = models.CharField(max_length=30, null=True)
    typo_name = models.CharField(max_length=30,null=True, blank=True)
    typo_name1 = models.CharField(max_length=30,null=True, blank=True)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
#    objects = TeamManager()

    class Meta:
        ordering = ('nfl_abbr',)

    def __str__(self):
        return str(self.nfl_abbr)


    def get_mike_abbr(self):
        return self.mike_abbr



class Games(models.Model):
    eid = models.CharField(max_length=30)
    week = models.ForeignKey(Week,on_delete=models.CASCADE, db_index=True)
    fav = models.ForeignKey(Teams, on_delete=models.CASCADE,null=True, related_name='fav')
    dog = models.ForeignKey(Teams, on_delete=models.CASCADE,null=True, related_name='dog')
    home = models.ForeignKey(Teams, on_delete=models.CASCADE,null=True, related_name='home', db_index=True)
    away = models.ForeignKey(Teams, on_delete=models.CASCADE,null=True, related_name='away', db_index=True)
    opening = models.CharField(max_length=10, null=True)
    spread = models.CharField(max_length=10,null=True)
    winner = models.ForeignKey(Teams, on_delete=models.CASCADE,null=True, related_name='winner')
    loser = models.ForeignKey(Teams, on_delete=models.CASCADE,null=True, related_name='loser')
    final = models.BooleanField(default=False)
    home_score = models.PositiveIntegerField(null=True)
    away_score = models.PositiveIntegerField(null=True)
    qtr = models.CharField(max_length=5, null=True)
    tie = models.BooleanField(default=False)
    date = models.DateField(null=True)
    time = models.CharField(max_length=20, null=True)
    day = models.CharField(max_length=10, null=True)

    def __str__(self):
        return str(self.home) + str(self.away)

    class Meta:
        index_together = ['week', 'home', 'away']



    #def get_game_id(self):
    #    return self.eid

class League(models.Model):
    league = models.CharField(max_length=30)

    def __str__(self):
        return self.league

class Player(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


    def __str__(self):
        return str(self.name)

class Picks(models.Model):
    week = models.ForeignKey(Week,on_delete=models.CASCADE, db_index=True)
    player  = models.ForeignKey(Player,on_delete=models.CASCADE,related_name="picks", db_index=True)
    pick_num = models.PositiveIntegerField()
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name="picksteam")


    def __str__(self):
        return str(self.player) + str(self.pick_num) + str(self.team)

    class Meta:
        index_together = ['week', 'player']

    def is_loser(self):
        try:
            game = Games.objects.get(Q(final=True), Q(week__current=True), (Q(home=self.team) | (Q(away= self.team))))
            if self.team == game.loser:
                return True
            elif self.team == game.winner:
                return False
            elif game.tie:
                return True
            else:
                print ('something wrong in is_loser')
                return False
        except ObjectDoesNotExist:
            return False

    def is_proj_loser(self):
        try:
            game = Games.objects.get(Q(final=False), Q(week__current=True), (Q(home=self.team) | Q(away=self.team)))
            if game.home_score == game.away_score:
                return False
            elif game.home == self.team:
                if home_score < away_score:
                    return True
                else:
                    return False
            elif game.away == self.team:
                if away_score < home_score:
                    return True
                else:
                    return False
            else:
                return False
                print ('projected issue', game)
        except ObjectDoesNotExist:
            return False



class WeekScore(models.Model):
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(null=True)
    projected_score = models.PositiveIntegerField(null=True)

    def __str__(self):
        return str(self.player)

class MikeScore(models.Model):
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    total = models.PositiveIntegerField()

    def __str__(self):
        return str(self.player) + str(self.total)
