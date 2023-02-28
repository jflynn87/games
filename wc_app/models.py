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
    logo_file = models.CharField(null=True, blank=True, max_length=200)
    data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return str(self.name)

    def get_users(self):
        l = []
        first_stage = Stage.objects.filter(event=self).order_by('pk')[0]
        users = Picks.objects.filter(team__group__stage=first_stage).values('user').distinct()
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


    def ko_fix_picks(self):
        if self.rank == 13 and self.data.get('from_ele') == 'm13_fav':
            #p1 = Picks.objects.get(rank=9, user=self.user, team__group=self.team.group)
            return Picks.objects.get(rank=9, user=self.user, team__group=self.team.group)
        elif self.rank == 13 and self.data.get('from_ele') == 'm13_dog':
            return Picks.objects.get(rank=10, user=self.user, team__group=self.team.group)

        elif self.rank == 14 and self.data.get('from_ele') == 'm14_fav':
            return Picks.objects.get(rank=11, user=self.user, team__group=self.team.group)
        elif self.rank == 14 and self.data.get('from_ele') == 'm14_dog':
            return Picks.objects.get(rank=12, user=self.user, team__group=self.team.group)
        else:
            return None

    def calc_score(self, data, source):
        p_score = 0
        best_score = 0
        
        if source == 'web':

            if self.rank < 9 and len([v for k, v in data.items() if k == 'stage_2' and self.team.full_name in v]) > 0:
                p_score += 5
            elif self.rank > 8 and self.rank < 13 and len([v for k, v in data.items() if k == 'stage_3' and self.team.full_name in v]) > 0:
                p_score += 10
            elif self.rank > 13 and self.rank < 15 and len([v for k, v in data.items() if k == 'stage_4' and self.team.full_name in v]) > 0:
                p_score += 15
            elif self.rank == 15 and len([v for k, v in data.items() if k == 'stage_5' and self.team.full_name in v]) > 0:  # need to figure out how to make this winners
                p_score += 30
            elif self.rank == 16 and len([v for k, v in data.items() if k == 'stage_6' and self.team.full_name in v]) > 0:  # need to figure out how to make this winners
                p_score += 20
        elif source == 'api':
            if self.rank < 9 and self.team.name in data.get('round-of-16').get('winners'):
                p_score += 5
            elif self.rank in [9, 10, 11, 12] and self.team.name in data.get('quarterfinals').get('winners'):
                p_score += 10
            elif self.rank in [13, 14] and self.team.name in data.get('semifinals').get('winners'):
                p_score += 15
            elif self.rank == 15 and self.team.name in data.get('final').get('winners'):
                p_score += 30
            elif self.rank == 16 and self.team.name in data.get('3rd-place').get('winners'):
                p_score += 20

            if p_score > 0:
                best_score = p_score
            elif self.rank < 9 and self.team.name not in data.get('round-of-16').get('losers'):
                best_score += 5
            elif self.rank in [9, 10, 11, 12] and not (self.team.name in data.get('round-of-16').get('losers') or self.team.name in data.get('quarterfinals').get('losers')):
                best_score += 10
            elif self.rank in [13, 14] and not (self.team.name in data.get('round-of-16').get('losers') or self.team.name in data.get('quarterfinals').get('losers') or self.team.name in data.get('semifinals').get('losers')):
                best_score += 15
            elif self.rank == 15 and not (self.team.name in data.get('round-of-16').get('losers') or self.team.name in data.get('quarterfinals').get('losers') or self.team.name in data.get('semifinals').get('losers') or self.team.name in data.get('final').get('losers')):
                best_score += 30
            elif self.rank == 16 and not (self.team.name in data.get('round-of-16').get('losers') or self.team.name in data.get('quarterfinals').get('losers') or self.team.name in data.get('semifinals').get('losers') or self.team.name in data.get('3rd-place').get('losers')):
                best_score += 20

        else:
            raise Exception ('invalid source') 


        return (p_score, best_score)

    def in_out(self, data):
        result = 'in'
        if self.rank < 9:
           return result
        elif self.rank in [9, 10, 11, 12] and self.team.name in data.get('round-of-16').get('losers'):
            result = 'out'
        elif self.team.name in data.get('round-of-16').get('losers') or self.team.name in data.get('quarterfinals').get('losers'):
            result = 'out'
        #elif self.rank == 15 and (self.team.name in data.get('round-of-16').get('losers') or self.team.name in data.get('quarterfinals').get('losers') or self.team.name in data.get('semifinals').get('losers') ):
        #    result = 'out'
        #elif self.rank == 16 and self.team.name not in data.get('3rd-place').get('losers'):
        #    best_score += 20
        return result


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

