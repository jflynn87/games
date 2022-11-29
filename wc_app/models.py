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

    def get_users(self):
        l = []
        users = Picks.objects.filter(team__group__stage__current=True).values('user').distinct()
        for u in users:
            l.append(User.objects.get(pk=u.get('user')))
        return l


class Stage(models.Model):
    PICK_TYPE_CHOICES = (('1', 'rank'), ('2', 'bracket'))
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    current = models.BooleanField(default=False)
    complete = models.BooleanField(default=False)
    set_started = models.BooleanField(default=False)
    set_not_started = models.BooleanField(default=False)
    pick_type = models.CharField(max_length=100, choices=PICK_TYPE_CHOICES)
    score_url = models.URLField(null=True)

    def __str__(self):
        return str(self.name)

    def started(self):
        if self.set_started:
            return True
        return False

    def ko_match_order(self):
        if self.name == 'Knockout Stage':
            return [1,10, 3, 12, 5, 14, 7, 16, 2, 9, 4, 11, 6, 13, 8, 15]
        else:
            return []


class Group(models.Model):
    #event = models.ForeignKey(Event, on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    group = models.CharField(max_length=20)

    def __str__(self):
        return str(self.group)

    def perfect_picks(self, espn, user):
    
        x = [k for k, v in sorted(espn.get(self.group).items(), key= lambda r: r[1].get('rank'))]
        if Picks.objects.filter(team__name=x[0], rank=1, user=user).exists() and \
            Picks.objects.filter(team__name=x[1], rank=2, user=user).exists() and \
            Picks.objects.filter(team__name=x[2], rank=3, user=user).exists() and \
            Picks.objects.filter(team__name=x[3], rank=4, user=user).exists():
             print ('WC Perfect Picks ', self.group, user)
             return True
        return False


class Team(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    rank = models.IntegerField(default=0)
    flag_link = models.URLField(null=True, blank=True)
    info_link = models.URLField(null=True, blank=True)
    full_name = models.CharField(max_length=200, null=True, blank=True)
    #stage = models.ForeignKey(Stage, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)

    def upset_bonus(self):
        second_ranked_team = Team.objects.filter(group=self.group).order_by('rank')[1]
        #print (self.name, second_ranked_team)
        if self.rank > second_ranked_team.rank:
            return round((self.rank - second_ranked_team.rank)*.3,2)
        else:
            return 0

    def ko_first_game(self):
        order = [1, 10, 3, 12, 5, 14, 7, 16, 2, 9, 4, 11, 6, 13, 8, 15]
        if order.index(self.rank) % 2 == 0:
            i = order.index(self.rank) + 2
        else:
            i = order.index(self.rank) + 1
        game = int(round(i/2, 0))
        
        return game

    def ko_path(self):
        if self.rank in [1, 10, 3, 12]:
            path = []


class Picks (models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wc_user')
    #stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    rank = models.IntegerField()
    data = models.JSONField(blank=True, null=True)

    def __str__(self):
        return str(self.user.username) + ' ' + str(self.team)


class Data(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    rankings = models.JSONField(null=True, blank=True)
    group_data = models.JSONField(null=True, blank=True)
    display_data = models.JSONField(null=True, blank=True)
    force_refresh = models.BooleanField(default=False)

    def __str__(self):
        return str(self.stage)


class AccessLog(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wc_al_user')
    screen = models.CharField(max_length=100)
    count = models.IntegerField(default=0, null=True)

    def __str__(self):
        return str(self.stage)


class TotalScore(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wc_ts_user')
    score = models.FloatField(default=0)

    def __str__(self):
        return str(self.stage) + str(self.user) + str(self.score)

