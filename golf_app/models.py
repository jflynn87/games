from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


# Create your models here.

class Season(models.Model):
    season = models.CharField(max_length=10, null=True)
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
    pga_tournament_num = models.CharField(max_length=10, null=True)

    #def get_queryset(self):
    #    return self.objects.filter().first()

    def __str__(self):
        return self.name


class Group(models.Model):
    tournament= models.ForeignKey(Tournament, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    playerCnt = models.PositiveIntegerField()

    def __str__(self):
        return str(self.number) + '-' + str(self.tournament)


class Field(models.Model):
    playerName = models.CharField(max_length = 256, null=True)
    currentWGR = models.IntegerField(unique=False, null=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    alternate = models.NullBooleanField(null=True)
    withdrawn = models.BooleanField(default=False)
    partner = models.CharField(max_length=100, null=True, blank=True)
    teamID = models.CharField(max_length=30, null=True, blank=True)
    playerID = models.CharField(max_length=100, null=True)

    class Meta:
        ordering = ['group', 'currentWGR']

    def __str__(self):
        return  self.playerName

    def get_absolute_url(self):
        return reverse("golf_app:show_picks",kwargs={'pk':self.pk})

    def get_group(self, args):
        group = self.objects.filter(group=args)
        return group

    #def current_field(self):
    #    return self.objects.filter(tournament__current=True)

    def formatted_name(self):
        return self.playerName.replace(' Jr.','').replace('(am)','')

    def withdrawal(self):
        pass




class Name(models.Model):
    OWGR_name = models.CharField(max_length=256)
    PGA_name = models.CharField(max_length=256)

    def __str__(self):
        return self.OWGR_name


class Picks(models.Model):
    #playerName = models.ForeignKey(Field, on_delete=models.CASCADE, blank=True, default='', null=True)
    playerName = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='picks')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(null=True)
    #auto = models.NullBooleanField(default=False, null=True)

    class Meta():
        unique_together = ('playerName', 'user')

    def __str__(self):
        return str(self.playerName) if self.playerName else ''

    def is_winner(self):
        if ScoreDetails.objects.filter(pick=self, score=1, pick__playerName__tournament__complete=True):
            return True
        else:
            return False


class PickMethod(models.Model):
    CHOICES = (('1', 'player'), ('2', 'random'), ('3', 'auto'))

    method = models.CharField(max_length=20, choices=CHOICES)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user) + self.method

class ScoreDetails(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pick = models.ForeignKey(Picks, on_delete=models.CASCADE, blank=True, null=True)
    score = models.PositiveIntegerField(null=True)
    toPar = models.CharField(max_length=50, null=True)
    today_score = models.CharField(max_length = 50, null=True)
    thru = models.CharField(max_length=100, null=True)
    sod_position = models.CharField(max_length=30, null=True)

    def __str__(self):
        return str(self.user) + str(self.pick) + str(self.score)

    class Meta():
        unique_together = ('user', 'pick')


class BonusDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=True)
    winner_bonus = models.IntegerField(default=0)
    cut_bonus = models.IntegerField(default=0)

    def __str__(self):
        return str(self.user)

    class Meta():
        unique_together = ('tournament', 'user')



class TotalScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=True)
    score = models.IntegerField(null=True)
    cut_count = models.IntegerField(null=True)


    class Meta():
        unique_together = ('tournament', 'user')

    def __str__(self):
        return str(self.user) + str(self.score)

    def auto_pick(self):
        if PickMethod.objects.filter(user=self.user, tournament=self.tournament, method='3'):
            return True
        else:
            return False


class mpScores(models.Model):
    bracket = models.CharField(max_length=5)
    round = models.FloatField()
    match_num = models.CharField(max_length=5)
    #pick = models.ForeignKey(Picks, on_delete=models.CASCADE, null=True, related_name='picks')
    result = models.CharField(max_length=10)
    score = models.CharField(max_length=10)
    player = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='player', null=True)

    class Meta():
        unique_together = ('player', 'round')

    def __str__(self):
        return str(self.round) + str(self.player.playerName) + self.result

    def leader(self):
        pass
        #field = Field.objects.filter(group=self.player.group).values('playerName').annotate(Count('result'))
        #print (field)
        #return
