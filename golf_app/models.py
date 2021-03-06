from django.db import models 
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Min, Q, Count, Sum, Max
from datetime import datetime
from golf_app import utils
from django.db import transaction
from unidecode import unidecode
import json
import random




# Create your models here.

class Season(models.Model):
    season = models.CharField(max_length=10, null=True)
    current = models.BooleanField()

    def __str__(self):
        return self.season

    def get_users(self):
        ''''returns a list of user pk's as dict values'''
        first_t = Tournament.objects.filter(season=self).first()
        users = TotalScore.objects.filter(tournament=first_t).values('user')
        return users

    def get_total_points(self):
        score_dict = {}
        sorted_dict = {}
        for user in self.get_users():
            u = User.objects.get(pk=user.get('user'))
            score_dict[u.username] = TotalScore.objects.filter(tournament__season=self, user=u).aggregate(Sum('score'))
        min_score = min(score_dict.items(), key=lambda v: v[1].get('score__sum'))[1].get('score__sum')
        for i, (user, data) in enumerate(sorted(score_dict.items(), key=lambda v: v[1].get('score__sum'))):
            sorted_dict[user] = {'total': data.get('score__sum'), 'diff':  int(min_score) - int(data.get('score__sum')), 'rank': i+1}
        return json.dumps(sorted_dict)


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
    leaders = models.CharField(null=True, max_length=500, blank=True)
    playoff = models.BooleanField(default=False)
    saved_cut_num = models.IntegerField(null=True)
    saved_round = models.IntegerField(null=True)
    saved_cut_round = models.IntegerField(null=True)


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
        if ScoreDetails.objects.filter(pick__playerName__tournament=self).\
            exclude(Q(score=None) | Q(score=0) | \
                    Q(thru=None) | Q(thru__in=["not started", " ", "", '--']) | \
                    Q(today_score='WD')).exclude(gross_score=self.saved_cut_num).exists():
            print (self, 'tournament started based on picks lookup')
            print ('finishing started check', datetime.now())
            return True

        try:
            #scores = pga_score.PGAScore(self.pga_tournament_num)
            scores = scrape_espn.ScrapeESPN().get_data()
            if scores.get('info').get('round') == "Tournament Field":
                return False
            elif scores.get('info').get('round') == 1 and \
                len([v for k, v in scores.items() if v.get('round_score') not in ['--', '-', None]]) == 0:
                return False      
            elif scores.get('info').get('round') == 1 and \
                len([v for k, v in scores.items() if v.get('round_score') not in ['--', '-', None]]) > 0:
                return True      
            elif scores.round() > 1:
                print ('******* round above 1')
                print ('finishing started check', datetime.now())
                return True
            else:
                print ('started check in model falling to else, check why')
                return False
        except Exception as e:
            print ('started logic exception', e)
            print ('finishing started check', datetime.now())
            return False
        print ('finishing started check', datetime.now())
        return False
        
    def winning_picks(self, user):
        winning_score= TotalScore.objects.filter(tournament=self).aggregate(Min('score'))
        
        if TotalScore.objects.filter(tournament=self, user=user, score=winning_score.get('score__min')).exists():
            print ('winning picks', TotalScore.objects.filter(tournament=self, user=user, score=winning_score.get('score__min')))
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
            #expected_picks = Group.objects.filter(tournament=self).aggregate(Max('number'))
            expected_picks = 0
            for group in Group.objects.filter(tournament=self):
                expected_picks += group.num_of_picks()
            print ('expected', expected_picks, expected_picks * c)
            print ('pick count', Picks.objects.filter(playerName__tournament=self).count())
            print ('actual', Picks.objects.filter(playerName__tournament=self).count() - (expected_picks * c))
            if Picks.objects.filter(playerName__tournament=self).count() \
            == (expected_picks * c):
                return True
            else:
                return False

    def missing_picks(self):
        #changed  this to use the season obj user list 8/30/2020
        #t = Tournament.objects.filter(season__current=True).earliest('pk')
        #for user in TotalScore.objects.filter(tournament=t).values('user__username'):
        for user in Season.objects.get(current=True).get_users():
            if not Picks.objects.filter(playerName__tournament=self, \
                user=User.objects.get(pk=user.get('user'))).exists():
                print (User.objects.get(pk=user.get('user')), 'no picks so submit random')
                self.create_picks(User.objects.get(pk=user.get('user')), 'missing')
    
    def get_cut_round(self, sd=None):
        if sd == None:
            sd = ScoreDict.objects.get(tournament=self)
            score_dict = sd.data
        else:
            score_dict = sd
        
        #score_dict = ScoreDict.objects.get(tournament=self)
        
        for data in score_dict.values():
            if data.get('rank') == "CUT":
                if data['r3'] in ['--', '_', '-']:
                    return 2
                elif data['r4'] in ['--', '_', '-']: 
                    return 3
        return 2

    
    @transaction.atomic
    def create_picks(self, user, mode=None):
        max_group = Group.objects.filter(tournament=self).aggregate(Max('number'))
        max = max_group.get('number__max')
        random_picks = []
        for group in Group.objects.filter(tournament=self):
            #print ('max', group, group.num_of_picks(), list(Field.objects.filter(tournament=self, group=group, withdrawn=False)))
            if group.num_of_picks() >  1:
                for r in random.sample(list(Field.objects.filter(tournament=self, group=group, withdrawn=False)), group.num_of_picks()):
                    random_picks.append(r)
            else:
                random_picks.append(random.choice(Field.objects.filter(tournament=self, group=group, withdrawn=False)))
        
        #print ('saving random', user, datetime.now(), random_picks)
        self.save_picks(random_picks, user, mode)

        return random_picks 

    def save_picks(self,  pick_list, user, mode=None):

        for p in pick_list:
            pick = Picks()
            pick.playerName = p
            pick.user = user
            pick.save()

            sd, created = ScoreDetails.objects.get_or_create(pick=pick, user=user)
            sd.save()

        pm = PickMethod()
        pm.user = user
        pm.tournament = self
        if mode == 'missing':
            pm.method = '3'
        elif mode == 'random':
            pm.method = '2'
        else:
            pm.method = '1'
        pm.save()

        bd, created = BonusDetails.objects.get_or_create(tournament=self, user=user)
        bd.winner_bonus = 0
        bd.cut_bonus = 0
        bd.major_bonus = 0
        bd.save()
        
        return pick_list
       
    def last_group_multi_pick(self):
        if len(Field.objects.filter(tournament=self)) > 64 and not Group.objects.filter(tournament=self, number=7).exists():
            return True
        else:
            return False


    def cut_num(self, sd=None):
        if sd == None:
            sd = ScoreDict.objects.get(tournament=self)
            score_dict = sd.sorted_dict()
        else:
            #score_dict = {k:v for k, v in sorted(sd.items(), key=lambda item: item[1].get('sort_rank'))}
            score_dict = sd

        return score_dict.get('info').get('cut_num')
        #don't need rest of funciton, use the above from espn score

        if not self.has_cut:
            return len([x for x in score_dict.values() if x['rank'] not in self.not_playing_list()]) + 1

        #round = self.get_cut_round()
        round = self.saved_cut_round
        
        #round = self.get_round()
        #after cut WD's
        #commented for rerun, but do i need the if here?  should not get here normally for old tournament?
        #if self.tournament.current:  wd = len([x for x in self.score_dict.values() if x['rank'] == 'WD' and x['r'+str(round+1)] != '--']) 
        
        #just for wd after cut
        wd = len([x for x in score_dict.values() if x['rank'] == 'WD' and x['r'+str(round+1)] != '--']) 
        print ('wd: ', wd)        

        
        if self.saved_round == 1:
            return 66
        elif self.saved_round <= self.saved_cut_round:
            c_score =  (self.cut_score.split(' ')[len(self.cut_score.split(' '))-1])

            if c_score in [None, 'info']:
                #return len([x for x in score_dict.values() if x['rank'] not in self.not_playing_list()]) + 1 
                return 66
            if c_score == 'E':
                c_score = 0
            else:
                c_score = int(c_score)

            return len([x for x in score_dict.values() if int(x['total_score']) <= c_score and x['rank'] not in self.not_playing_list()]) + 1 
        else:
            #for v in score_dict.values():
            #    if v['rank'] in self.not_playing_list():

            return len([x for x in score_dict.values() if x['rank'] not in self.not_playing_list()]) + wd + 1
            #if self.get_round() != 4 and len(score_dict.values()) >65:
            #    return 66
            #else:
            #    return len([x for x in score_dict.values() if x['rank'] not in self.not_playing_list()]) + wd + 1

    def get_round(self, sd=None):
        #don't need, use the espn score dict from scrape
        if self.complete:
            return 4

        if sd == None:
           sd = ScoreDict.objects.get(tournament=self)
           score_dict = sd.sorted_dict()
        else:
        #     #score_dict = {k:v for k, v in sorted(sd.items(), key=lambda item: item[1].get('sort_rank'))}
           score_dict = sd
        
        return score_dict.get('info').get('round')
        #don't need the rest, use the dict from scrape espn.  

        print (score_dict.get('round'))
        if len([x for x in score_dict.values() if x['r1'] in ['--', '-']]) == len(score_dict):
            return 0

        if len([x for x in score_dict.values() if x['r1'] in ['--', '-'] and x['rank'] not in self.not_playing_list()]) > 0:
            return 1
        elif len([x for x in score_dict.values() if x['r2'] == '--' and x['rank'] not in self.not_playing_list()]) > 0:
            return 2
        elif len([x for x in score_dict.values() if x['r3'] == '--' and x['rank'] not in self.not_playing_list()]) > 0:
            return 3
        elif len([x for x in score_dict.values() if x['r4'] == '--' and x['rank'] not in self.not_playing_list()]) > 0:
            return 4
        else:
            return 4


    def optimal_picks(self):
        optimal_dict = {}

        for group in Group.objects.filter(tournament=self):

           golfer_list = []
           gm_start = datetime.now()
           group_cuts = Field.objects.filter(group=group, rank__in=self.not_playing_list()).count()

           group_min = group.min_score(mode='full')
           print (group_min)
           for gm in group_min:
               f = Field.objects.get(pk=gm[0])
               golfer_list.append(f.playerName)

               optimal_dict[group.number] = {'golfer': golfer_list, 'rank': gm[1], 'cuts': group_cuts, 'total_golfers': group.playerCnt}

        return json.dumps(optimal_dict)


    def not_playing_list(self):
        return ['CUT', 'WD', 'DQ']

    def tournament_complete(self, sd=None):
        if sd == None:
           sd = ScoreDict.objects.get(tournament=self)
           score_dict = sd.sorted_dict()
        else:
           score_dict = sd

        if sd.get('info').get('round') == 'Final':
            return True
        else:
            return False

        #commented to use ESPN scores
        # for v in score_dict.values():
        #     if (v['rank'] not in self.not_playing_list() and \
        #         v['r4'] == "--") or v['rank']  == "T1":
        #         return False

        # if self.get_round(sd) == 4: 
        #     return True
        # else:
        #     return False


class Group(models.Model):
    tournament= models.ForeignKey(Tournament, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    playerCnt = models.PositiveIntegerField()

    def __str__(self):
        return str(self.number) + '-' + str(self.tournament)

    def min_score(self, cut_num=None, mode=None):
        start = datetime.now()
        f = list(Field.objects.filter(group=self).exclude(withdrawn=True).values('pk', 'rank', 'handi'))
        s = [(x['pk'], (int(utils.formatRank(x['rank'], self.tournament))) - int(x['handi'])) for x in f]
        #print (s)
        score = min(s, key= lambda x: x[1])
        #print (self, score, Field.objects.get(pk=score[0]))
        print ('duration: ', datetime.now() - start)
        if mode == None:
            return score[1]
        elif mode == 'full':
            return [x for x in s if x[1] == score[1]]
            #return score
        else:
            return score[1]


    def num_of_picks(self):
        if self.tournament.last_group_multi_pick() and self.number == 6:
            return 5
        else:
            return 1


class Golfer(models.Model):
    golfer_pga_num = models.CharField(max_length=100)
    golfer_name = models.CharField(max_length=100)
    pic_link  = models.URLField(max_length=500, null=True, blank=True)
    flag_link = models.URLField(max_length=500, null=True, blank=True)
    espn_number = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return str(self.golfer_name) + ' : ' + str(self.golfer_pga_num)

    def pga_web_name_format(self):
        if  self.golfer_name[1]=='.' and self.golfer_name[3] =='.':
            return self.golfer_name[0].lower() + '-' + self.golfer_name[2].lower() + '--' + self.golfer_name.split(' ')[1].strip(', Jr.').lower()
        else:
            return self.golfer_name.split(' ')[0] + '-' + self.golfer_name.split(' ')[1]



    def golfer_link(self):
        if  self.golfer_name[1]=='.' and self.golfer_name[3] =='.':
            name = str(self.golfer_pga_num) + '.' + self.pga_web_name_format()
        else:
            name = str(self.golfer_pga_num) + '.' + self.pga_web_name_format()
        return 'https://www.pgatour.com/players/player.' + unidecode(name) + '.html'


class Field(models.Model):

    playerName = models.CharField(max_length = 256, null=True)
    currentWGR = models.IntegerField(unique=False, null=True)
    sow_WGR = models.IntegerField(unique=False, null=True)
    soy_WGR = models.IntegerField(unique=False, null=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    alternate = models.BooleanField(null=True)
    withdrawn = models.BooleanField(default=False)
    partner = models.CharField(max_length=100, null=True, blank=True)
    teamID = models.CharField(max_length=30, null=True, blank=True)
    playerID = models.CharField(max_length=100, null=True)
    map_link = models.URLField(null=True)
    pic_link = models.URLField(null=True)
    golfer = models.ForeignKey(Golfer, on_delete=models.CASCADE, null=True)
    rank = models.CharField(max_length=50, null=True)
    handi = models.IntegerField(null=True)

    class Meta:
        ordering = ['group', 'currentWGR']
        

    def __str__(self):
        return  self.playerName

    #def get_absolute_url(self):
    #    return reverse("golf_app:show_picks",kwargs={'pk':self.pk})

    def formatted_name(self):
        return self.playerName.replace(' Jr.','').replace('(am)','')

    def prior_year_finish(self):
        try:
            last_season = str(int(self.tournament.season.season)-1)
            t = Tournament.objects.get(pga_tournament_num=self.tournament.pga_tournament_num, season__season=last_season)
        except Exception as e:
            last_season = str(int(self.tournament.season.season)-2)
            t = Tournament.objects.get(pga_tournament_num=self.tournament.pga_tournament_num, season__season=last_season)
        
        sd = ScoreDict.objects.get(tournament=t)

        try:
            return sd.data.get(self.playerName).get('rank')
        except Exception as e:
            return 'n/a'
        #@s = ScoreDetails.objects.filter(pick__playerName__tournament=t, pick__playerName__playerName=self).first()
   
        #if s == None:
        #    return 'n/a'
        #elif s.today_score == "cut":
        #elif s == "cut":
        #    return s
        #else:
        #    return s

    def handicap(self):
        if round(self.currentWGR*.01) < (Field.objects.filter(tournament=self.tournament).count() * .13):
            return int(round(self.currentWGR*.01))
        return round(Field.objects.filter(tournament=self.tournament).count() * .13)

    def rank_as_int(self):
        if type(self.rank) is int:
            return self.rank
        elif self.rank in ["CUT", "WD", "DQ", "MDF"]:
            return 999
        elif self.rank in  ['', '--', None]:
            return 999
        elif self.rank[0] != 'T':
            return int(self.rank)
        elif self.rank[0] == 'T':
            return int(self.rank[1:])
        else:
            return int(self.rank)



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
        return 'owgr name: ' + self.OWGR_name + 'PGA name: ' + self.PGA_name


class Picks(models.Model):
    #playerName = models.ForeignKey(Field, on_delete=models.CASCADE, blank=True, default='', null=True)
    playerName = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='picks')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.IntegerField(null=True)
    #auto = models.NullBooleanField(default=False, null=True)

    class Meta():
        unique_together = ('playerName', 'user')

    def __str__(self):
        return str(self.playerName) if self.playerName else ''

    def is_winner(self):
        if ScoreDetails.objects.filter(pick=self, gross_score=1, pick__playerName__tournament__complete=True):
            return True
        else:
            return False

    def best_in_group(self):
        
        if self.playerName.playerName in self.playerName.group.best_picks():
            return True
        else:
            return False

    def playoff_loser(self):
        if self.playerName.tournament.playoff and ScoreDetails.objects.filter(pick=self, gross_score=2, pick__playerName__tournament__complete=True):
        #if self.playerName.tournament.playoff and ScoreDetails.objects.filter(pick=self, score=2):
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
    score = models.IntegerField(null=True)
    toPar = models.CharField(max_length=50, null=True)
    today_score = models.CharField(max_length = 50, null=True)
    thru = models.CharField(max_length=100, null=True)
    sod_position = models.CharField(max_length=1000, null=True)
    gross_score = models.IntegerField(null=True)

    def __str__(self):
        return str(self.user) + str(self.pick) + str(self.score)

    class Meta():
        unique_together = ('user', 'pick')

    def  low_in_group(self):
        if self.score == self.pick.playerName.group.min_score():
            return True
        else:
            return False




class BonusDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=True)
    winner_bonus = models.IntegerField(default=0)
    cut_bonus = models.IntegerField(default=0)
    major_bonus = models.IntegerField(default=0)
    playoff_bonus = models.BigIntegerField(default=0)
    best_in_group_bonus = models.BigIntegerField(default=0)


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

    def total_handicap(self):
        handi = 0
        for pick in Picks.objects.filter(playerName__tournament=self.tournament, user=self.user):
            handi = handi + pick.playerName.handicap() 
        return handi





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

class ScoreDict(models.Model):
    tournament = models.ForeignKey(Tournament, null=True, on_delete=models.CASCADE, related_name='score_dict')
    data = models.JSONField(null=True)
    pick_data = models.JSONField(null=True)
    cbs_data = models.JSONField(null=True)



    def __str__(self):
        return (self.tournament.name)

    def sorted_dict(self):
        d = self.data
        for k, v in d.items():
            v.update({'sort_rank': utils.formatRank(v.get('rank'))})
            # if Field.objects.filter(tournament=self.tournament, playerName=k).exists():
            #     f = Field.objects.get(tournament=self.tournament, playerName=k)
            #     v.update({'sort_rank': f.rank_as_int()})
            # else:


                # if v.get('rank') != None and v.get('rank') not in self.tournament.not_playing_list(): 
                #     if type(v.get('rank')) == int:
                #         v.update({'sort_rank': v.get('rank')})
                #     else:
                #         v.update({'sort_rank': int(v.get('rank')[1:])})
                # else:
                #     v.update({'sort_rank': 999})

        
        sorted_score_dict = {k:v for k, v in sorted(d.items(), key=lambda item: item[1].get('sort_rank'))}
        
        return sorted_score_dict

    def clean_dict(self):
        return  {key.replace('(a)', '').strip(): v for key, v in self.data.items()}

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_picks = models.BooleanField(default=False)