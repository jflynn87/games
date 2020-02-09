from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Min, Q, Count, Sum, Max
from datetime import datetime
from golf_app import pga_score
from django.db import transaction
import random



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
    major = models.BooleanField(default=False)
    late_picks = models.BooleanField(default=False)
    set_started = models.BooleanField(default=False)
    set_notstarted = models.BooleanField(default=False)
    manual_score_file = models.BooleanField(default=False)
    score_update_time = models.DateTimeField(null=True, blank=True)
    cut_score = models.CharField(max_length=100, null=True, blank=True)
    has_cut = models.BooleanField(default=True)

    #def get_queryset(self):t
    #    return self.objects.filter().first()

    def __str__(self):
        return self.name

    def started(self):
        print ('starting started check', datetime.now())
        if self.set_started:
            print ('overrode to started')
            return True
        if self.set_notstarted:
            print ('overrode to not started')
            return False
        #if ScoreDetails.objects.filter(pick__playerName__tournament=self).exclude(Q(score__in=[0, None]) or Q(thru__in=["not started", None, " ", ""])) or Q(today_score__in=["WD", None]).exists():
        if ScoreDetails.objects.filter(pick__playerName__tournament=self).\
            exclude(Q(score=None) or Q(score=0) or \
                    Q(thru=None) or Q(thru__in=["not started", " ", ""]) or \
                    Q(today_score='WD')).exists():
            #if ScoreDetails.objects.filter(pick__playerName__tournament=self).exclude(Q(score=0) or Q(thru__in=["not started", " ", ""]) or Q(today_score="WD")).exists():
            print (self, 'tournament started based on picks lookup')
            print ('finishing started check', datetime.now())
            return True

        try:
            scores = pga_score.PGAScore(self.pga_tournament_num)
            if scores.round() > 1:
                print ('******* round above 1')
                print ('finishing started check', datetime.now())
                return True
        except Exception as e:
            print ('started logic exception', e)
            print ('finishing started check', datetime.now())
            return False
        print ('finishing started check', datetime.now())
        return False
        
    def winning_picks(self, user):
        winning_score= TotalScore.objects.filter(tournament=self).aggregate(Min('score'))
        
        if TotalScore.objects.filter(tournament=self, user=user, score=winning_score.get('score__min')).exists():
            print ('true', TotalScore.objects.filter(tournament=self, user=user, score=winning_score.get('score__min')))
            return True
        else:
            return False

    def num_of_winners(self):
        winning_score = TotalScore.objects.filter(tournament=self).aggregate(Min('score'))
        return TotalScore.objects.filter(tournament=self, score=winning_score.get('score__min')).count()
    
    def winner(self):
        winning_score = TotalScore.objects.filter(tournament=self).aggregate(Min('score'))
        return TotalScore.objects.filter(tournament=self, score=winning_score.get('score__min'))

    def picks_complete(self):
        if self.started():
            t = Tournament.objects.filter(season__current=True).earliest('pk')
            c=  len(Picks.objects.filter(playerName__tournament=t).values('user').annotate(unum=Count('user')))
            expected_picks = Group.objects.filter(tournament=self).aggregate(Max('number'))
            print ('expected', expected_picks, expected_picks['number__max'] * c)
            print ('actual', Picks.objects.filter(playerName__tournament=self).count() - expected_picks['number__max'] * c)
            if Picks.objects.filter(playerName__tournament=self).count() \
            == (expected_picks.get('number__max') * c):
                return True
            # elif (expected_picks.get('number__max') - Picks.objects.filter(playerName__tournament=self.tournament).count()) \
            # % expected_picks.get('number__max') == 0:
            #     print ('missing full picks')
            #     #using first tournament, should update to use league
            #     for user in TotalScore.objects.filter(tournament=t).values('user__username'):
            #         if not Picks.objects.filter(playerName__tournament=self.tournament, \
            #         user=User.objects.get(username=user.get('user__username'))).exists():
            #             print (user.get('user__username'), 'no picks so submit random')
            #             self.create_picks(self.tournament, User.objects.get(username=user.get('user__username')))
            else:
                return False

    def missing_picks(self):
        t = Tournament.objects.filter(season__current=True).earliest('pk')
        for user in TotalScore.objects.filter(tournament=t).values('user__username'):
            if not Picks.objects.filter(playerName__tournament=self, \
                user=User.objects.get(username=user.get('user__username'))).exists():
                print (user.get('user__username'), 'no picks so submit random')
                self.create_picks(User.objects.get(username=user.get('user__username')))
    
    
    @transaction.atomic
    def create_picks(self, user):
        for group in Group.objects.filter(tournament=self):
            pick = Picks()
            if self.manual_score_file:
                random_picks = random.choice(Field.objects.filter(tournament=self, group=group))
            else:      
                random_picks = random.choice(Field.objects.filter(tournament=self, group=group, withdrawn=False))
            pick.playerName = Field.objects.get(playerName=random_picks.playerName, tournament=self)
            pick.user = user
            pick.save()

        pm = PickMethod()
        pm.user = user
        pm.tournament = self
        pm.method = '3'
        pm.save()

        return
       


class Group(models.Model):
    tournament= models.ForeignKey(Tournament, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    playerCnt = models.PositiveIntegerField()

    def __str__(self):
        return str(self.number) + '-' + str(self.tournament)


class Field(models.Model):
    playerName = models.CharField(max_length = 256, null=True)
    currentWGR = models.IntegerField(unique=False, null=True)
    sow_WGR = models.IntegerField(unique=False, null=True)
    soy_WGR = models.IntegerField(unique=False, null=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    alternate = models.NullBooleanField(null=True)
    withdrawn = models.BooleanField(default=False)
    partner = models.CharField(max_length=100, null=True, blank=True)
    teamID = models.CharField(max_length=30, null=True, blank=True)
    playerID = models.CharField(max_length=100, null=True)
    map_link = models.URLField(null=True)
    pic_link = models.URLField(null=True)

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


class PGAWebScores(models.Model):
    tournament= models.ForeignKey(Tournament, on_delete=models.CASCADE)
    golfer=models.ForeignKey(Field, on_delete=models.CASCADE)
    rank = models.CharField(max_length=30, null=True)
    thru = models.CharField(max_length=30, null=True)
    round_score = models.CharField(max_length=30, null=True)
    total_score = models.CharField(max_length=30, null=True)
    r1 = models.CharField(max_length=30, null=True)
    r2 = models.CharField(max_length=30, null=True)
    r3 = models.CharField(max_length=30, null=True)
    r4 = models.CharField(max_length=30, null=True)
    change = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.tournament) + str(self.golfer)




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
    sod_position = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.user) + str(self.pick) + str(self.score)

    class Meta():
        unique_together = ('user', 'pick')


class BonusDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=True)
    winner_bonus = models.IntegerField(default=0)
    cut_bonus = models.IntegerField(default=0)
    major_bonus = models.IntegerField(default=0)

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
