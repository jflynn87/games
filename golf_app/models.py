from django.core.exceptions import ImproperlyConfigured
from django.db import models 
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Min, Q, Count, Sum, Max, fields
from datetime import datetime
from django.db.models.base import Model
from django.forms import JSONField

from scipy.stats.stats import rankdata
from golf_app import utils 
from django.db import transaction
from unidecode import unidecode
import json
import random
import urllib
import unidecode 
from collections import OrderedDict
from bs4 import BeautifulSoup


# Create your models here.

class Season(models.Model):
    #season = models.CharField(max_length=10, null=True)
    season = models.IntegerField(default=0)
    current = models.BooleanField()
    data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return str(self.season)

    def get_users(self, mode=None):
        ''''returns a list of user pk's as dict values or native objects if mode == obj'''

        f = False
        new_users = []
        l = []

        if Tournament.objects.filter(season=self).count() > 1:
            first_t = Tournament.objects.filter(season=self).first()
        else:
            first_t = Tournament.objects.filter(season__season=str(int(self.season) - 1)).first()
            f = True

        users =list(TotalScore.objects.filter(tournament=first_t).values('user'))

        if f:
            old = [v.get('user') for v in users]
            new_users = Picks.objects.filter(playerName__tournament=Tournament.objects.get(current=True)).exclude(user__pk__in=old).values('user').distinct()
               
        if mode == 'obj':
            for u in users:
                l.append(u.get('user'))
            if f: 
                for n in new_users:
                    l.append(n.get('user'))
            return User.objects.filter(pk__in=l)
        else:
            if f:
                for n in new_users:
                    users.append({'user': n.get('user')}) 
                
            return users

    def get_total_points(self, tournament=None):
        '''takes a season and optional tournament object and returns a json response'''
        score_dict = {}
        sorted_dict = {}
        if not tournament:
            t_list = list(Tournament.objects.filter(season=self).values_list('pk', flat=True))
        else:
            t_list = list(Tournament.objects.filter(season=self, pk__lte=tournament.pk).values_list('pk', flat=True))

        for u in self.get_users('obj'):
            t_scores = TotalScore.objects.filter(tournament__pk__in=t_list, user=u).aggregate(Sum('score'))
            total_score = 0 if t_scores.get('score__sum') is None else t_scores.get('score__sum')
            score_dict[u.username] = {'score__sum': total_score, 
                                    'fed_ex_score': self.fed_ex_scores(u)}
        #print (score_dict)
        min_score = min(score_dict.items(), key=lambda v: v[1].get('score__sum'))[1].get('score__sum')
        second = sorted(score_dict.items(), key=lambda v: v[1].get('score__sum'))[1][1].get('score__sum')

        #print ('fed ex scores: ', fed_ex_scores)
        for i, (user, data) in enumerate(sorted(score_dict.items(), key=lambda v: v[1].get('score__sum'))):
            sorted_dict[user] = {'total': score_dict.get(user).get('score__sum'), 'diff':  int(min_score) - int(data.get('score__sum')), 'rank': i+1, 
                                'points_behind_second': int(second) - int(data.get('score__sum')), #'t_scores': score_dict.get(user).get('t_scores'),
                                'fed_ex_score': score_dict.get(user).get('fed_ex_score'),
                                'player': user

                                    }
                                
                                
        return json.dumps(sorted_dict)
        # else:
        #     for u in self.get_users('obj'):
        #         t_scores = TotalScore.objects.filter(tournament__season=self, user=u, tournament__pk__lte=tournament.pk).aggregate(Sum('score'))
        #         total_score = 0 if t_scores.get('score__sum') is None else t_scores.get('score__sum')
        #         score_dict[u.username] = {'score__sum': total_score, 't_scores': t_scores.get('score__sum'), 'fed_ex_score': self.fed_ex_scores(u, tournament)}
        #     min_score = min(score_dict.items(), key=lambda v: v[1].get('score__sum'))[1].get('score__sum')
        #     second = sorted(score_dict.items(), key=lambda v: v[1].get('score__sum'))[1][1].get('score__sum')

        #     #print ('fed ex scores: ', fed_ex_scores)
        #     for i, (user, data) in enumerate(sorted(score_dict.items(), key=lambda v: v[1].get('score__sum'))):
        #         sorted_dict[user] = {'total': score_dict.get(user).get('score__sum'), 'diff':  int(min_score) - int(data.get('score__sum')), 'rank': i+1, 
        #                             'points_behind_second': int(second) - int(data.get('score__sum')),
        #                             'fed_ex_score': score_dict.get(user).get('fed_ex_score'),
        #                             'player': user
        #                             }
                                    
                                    
        #     return json.dumps(sorted_dict)

    def fed_ex_scores(self, user, t=None):

        if t:
            score = t.fedex_data.get('player_points').get(user.username).get('score')
        else:
            score = FedExPicks.objects.filter(pick__season__season=self, user=user).aggregate(Sum('score')).get('score__sum')
            #if FedExPicks.objects.filter(pick__season__season=self, user=user, top_3=True, rank__in=[1, 2, 3]).exists():
            top3 = FedExSeason.objects.get(season=self).top_3()
            for p in FedExPicks.objects.filter(pick__season__season=self, user=user, top_3=True, pick__golfer__golfer_name__in=top3.keys()):
                fed_ex_rank = [x.get('rank') for k, x in top3.items() if k == p.pick.golfer.golfer_name][0]
                if fed_ex_rank in [1, '1']:
                    score -= 100
                elif fed_ex_rank in [2, '2']:
                    score -= 75
                elif fed_ex_rank in [3, '3']:
                    score -= 50
        
        return score


    def regular_prize(self):
        return 30

    def major_prize(self):
        return 100

    def major_count(self):
        return 4

    def special_fields(self):
        return ['999', '470', '468', '018']



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
    ignore_name_mismatch = models.BooleanField(default=False)
    espn_t_num = models.CharField(max_length=100, null=True, blank=True)
    auction = models.BooleanField(default=False)
    fedex_data = models.JSONField(null=True, blank=True)
    round_data = models.JSONField(null=True, blank=True)
    individual_stats = models.JSONField(null=True, blank=True)


    class Meta():
        unique_together = ('season', 'pga_tournament_num')
        indexes = [models.Index(fields=['season', 'pga_tournament_num']),]


    #def get_queryset(self):t
    #    return self.objects.filter().first()

    def __str__(self):
        return self.name

    
    def natural_key(self):
        return self.name

    
    def prior_t(self):
        if Tournament.objects.filter(season=self.season).exclude(pk__gte=self.pk).exists():
            keys = Tournament.objects.filter(season=self.season).exclude(pk__gte=self.pk).values_list('pk', flat=True)
            return Tournament.objects.get(pk=max(keys))
        else:
            #should only need for first T of season
            keys = Tournament.objects.all().exclude(pk__gte=self.pk).values_list('pk', flat=True)
            return Tournament.objects.get(pk=max(keys))
    

    def started(self):
        start = datetime.now()
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
            print ('started check dur: ', datetime.now() - start)
            return True

        try:
            from golf_app import espn_api 
            return espn_api.ESPNData().started()

        except Exception as e:
            print ('started logic exception', e)
            print ('finishing started check', datetime.now())
            return False
        
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
            c = len(self.season.get_users())
            expected_picks = 0
            for group in Group.objects.filter(tournament=self):
                expected_picks += group.num_of_picks()
            print ('expected per player and total', expected_picks, expected_picks * c)
            print ('total pick count', Picks.objects.filter(playerName__tournament=self).count())
            print ('missing picks', Picks.objects.filter(playerName__tournament=self).count() - (expected_picks * c))
            if Picks.objects.filter(playerName__tournament=self).count() \
            == (expected_picks * c):
                return True
            else:
                return False

    def missing_picks(self):
        for user in Season.objects.get(current=True).get_users():
            if not Picks.objects.filter(playerName__tournament=self, \
                user=User.objects.get(pk=user.get('user'))).exists():
                print (User.objects.get(pk=user.get('user')), 'no picks so submit random')
                self.create_picks(User.objects.get(pk=user.get('user')), 'missing')

        return 
    
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
        
        if self.pga_tournament_num in ['468', '500']:
            cp = CountryPicks()
            cp.country = ''
            cp.ryder_cup_score = 0
            cp.tournament = self
            cp.user = user
            cp.save()
        print ('saving random', user, datetime.now(), random_picks)
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

        if PickMethod.objects.filter(user=user, tournament=self, method='3').exists() and mode != 'missing':
            PickMethod.objects.filter(user=user, tournament=self, method='3').update(method='4')

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

        #bd, created = BonusDetails.objects.get_or_create(tournament=self, user=user)
        #bd.winner_bonus = 0
        #bd.cut_bonus = 0
        #bd.major_bonus = 0
        #bd.save()
        
        return pick_list
       
    def last_group_multi_pick(self):
        if int(self.season.season) > 2021:
            return False
        if len(Field.objects.filter(tournament=self)) > 64 and not Group.objects.filter(tournament=self, number=7).exists():
            return True
        else:
            return False

       
    def first_group_multi_pick(self):
        if int(self.season.season) < 2022:
            return False
        #if len(Field.objects.filter(tournament=self)) > 70:
        #    return True
        #else:
        #    return False
        g_1 = Group.objects.get(tournament=self, number=1)
        if g_1.playerCnt >= 10:
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

    # commented before 2023 season
    # def optimal_picks(self):
    #     optimal_dict = {}

    #     for group in Group.objects.filter(tournament=self):

    #        golfer_list = []
    #        gm_start = datetime.now()
    #        group_cuts = Field.objects.filter(group=group, rank__in=self.not_playing_list()).count()

    #        group_min = group.min_score(mode='full')
    #        #print (group_min)
    #        for gm in group_min:
    #            f = Field.objects.get(pk=gm[0])
    #            golfer_list.append(f.playerName)

    #            optimal_dict[group.number] = {'golfer': golfer_list, 'rank': gm[1], 'cuts': group_cuts, 'total_golfers': group.playerCnt}

    #     return json.dumps(optimal_dict)


    def not_playing_list(self):
        #ordered to appear correctly in leaderboard
        return ['WD', 'DQ', 'CUT', 'MDF']

    def tournament_complete(self, sd=None):
        if sd == None:
           sd = ScoreDict.objects.get(tournament=self)
           #score_dict = sd.sorted_dict()
        #else:
           #score_dict = sd

        if sd.get('info').get('round') == 'Final':
            return True
        else:
            return False


    def total_required_picks(self):
        tot = 0
        for g in Group.objects.filter(tournament=self):
            tot += g.num_of_picks()
        return tot

    def get_country_counts(self):
        '''retruns a dict of all the countries in the tournament'''
        #if self.pga_tournament_num == '999': #Olympics
        try:
            #t = Tournament.objects.get(pga_tournament_num='999')
            sex = 'men'
            d = {'men': {}, 'woman': {}}
            for f in Field.objects.filter(tournament=self):
                if f.playerName == "Nelly Korda": sex = 'woman'  # top ranked woman
                country = f.golfer.flag_link.split('/')[9][0:3].upper()
                if self.pga_tournament_num == '999' and country == "NIR": #For Rory
                    country = "IRL"
                if d.get(sex).get(country):
                    d.get(sex).update({country: d.get(sex).get(country) +  1})
                else:
                    d.get(sex).update({country: 1})
                
            return d
        except Exception as e:
            return {'msg': e}

    def individual_country_count(self, country, gender):
        '''takes a t obj and strings for country and gender, returns an int'''
        all_countries = self.get_country_counts()
        if all_countries.get(gender):
            if all_countries.get(gender).get(country):
                return all_countries.get(gender).get(country)
        return 0

    def field_quality(self):
        if self.major:
            return "major"
        from golf_app import utils , pga_t_data
        
        if int(self.season.season) < 2023:
            f_len = Field.objects.filter(tournament=self).count()
            #owgr_sum = Field.objects.filter(tournament=self).exclude(currentWGR=9999).aggregate(Sum('currentWGR'))
            #unranked = Field.objects.filter(tournament=self, currentWGR=9999).count()
            top_100 = round(Field.objects.filter(tournament=self, currentWGR__lte=122).count()/f_len,2)

            if top_100 > .3:
                return "strong"
            else:
                return "weak"
        else:
            t_data = pga_t_data.PGAData(season=self.season)
            t_type = t_data.get_t_type(self.pga_tournament_num)
            if t_type == 'MJR':
                return 'major'
            elif t_type in ['PLF', 'PLS'] or self.pga_tournament_num == '500':  #500 for Pres cup
                return 'special'
            elif int(t_data.get_purse(self.pga_tournament_num).replace(',', '')) >= 10000000:
                return 'strong'
            elif int(t_data.get_purse(self.pga_tournament_num).replace(',','')) < 10000000:
                return 'weak'
            else:
                print ('field quality in else, why?')
                return 'weak'



    def special_field(self):
        if self.pga_tournament_num in ['999', '470', '468', '018']:
            return True
        else:
            return False


    def good_api_data(self):
        if self.pk >= 201:
            return True
        else:
            return False
    
    def pga_t_type(self):
        for s in self.season.data.get('schedule'):
            for year in s.get('years'):
                if str(year.get('year')) == str(self.season.season):
                    for tour in year.get('tour'):
                        if tour.get('desc') == 'PGA TOUR':
                            for t in tour.get('trns'):
                                if str(t.get('permNum')) == str(self.pga_tournament_num):
                                     return (t.get('trnType'))
        print ('models file pga_t_type not finding t')                           
        return None

    def prize(self):
        if int(self.season.season)< 2023:
            if self.major:
                return 100
            elif self.pga_t_type() in ['PLF', 'PLS']:
                return 75
            else:
                return 30
        else:
            field_quality = self.field_quality()
            if field_quality == 'major':
                return 100
            elif field_quality == 'special':
                return 75
            elif field_quality == 'strong':
                return 50
            elif field_quality == 'weak':
                return 25
        
        print ('Prize ERROR no prize found')
        return 0

    def winner_bonus_points(self):
        field_type = self.field_quality()
        if int(self.season.season) < 2023:
            print ('T winner_bonus_points before 2023 need to update code')
            return 0
        else:
            if field_type == 'weak':
                return 50
            elif field_type == 'strong':
                return 100
            elif field_type == 'major':
                return 150 
            elif field_type == 'special':
                return 125
            else:
                print ('T winner_bonus_points unknown')
                return 0        




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
        elif int(self.tournament.season.season) > 2021 and self.tournament.first_group_multi_pick() \
            and self.number == 1:
            return 2
        else:
            return 1


    def natural_key(self):
        return self.number

    #commented before 2023, dont think this is used anymore
    # def optimal_pick(self, score_dict):
    #     '''takes a dict returns a list'''
    #     if score_dict.get('info'):   #check if espn scrape dict
    #         best_score = min(utils.formatRank(x.get('rank')) - x.get('handicap') for k, x in score_dict.items() if k != 'info' and x.get('group') == self.number) 
    #         best_list = {v['pga_num']:k for (k,v) in score_dict.items() if v.get('group') == self.number and utils.formatRank(v.get('rank')) - v.get('handicap') == best_score}
    #         #print ('best: ', best_list, best_score)
    #         return best_list


    def cut_count(self, score_dict=None, espn_api_data=None):
        if not score_dict and not espn_api_data:
            raise Exception('cut count requires either a score dict or api data')

        if score_dict:
            return len([v for k, v in score_dict.items() if k != 'info' and v.get('group') == self.number and v.get('rank') in self.tournament.not_playing_list()])
        #else:
        #    return 0  # add score dict lookup here and fix code
        elif espn_api_data:
            golfers = self.get_golfers()

            if self.tournament.pga_tournament_num == '018':
                return len([x.get('roster')[0].get('playerId') for x in espn_api_data.field_data if (str(x.get('roster')[0].get('playerId')) in golfers or str(x.get('roster')[1].get('playerId')) in golfers) and x.get('status').get('type').get('id') == '3'])
            else:
                return len([x for x in espn_api_data.field_data if x.get('id') in golfers and x.get('status').get('type').get('id') == '3']) - len(espn_api_data.golfers_post_cut_wd(golfers))

    def get_golfers(self):
        '''takes a group and returns a list of espn numbers'''
        return Field.objects.filter(group=self).values_list('golfer__espn_number', flat=True)

    def get_made_cut_golfers(self, espn_api_data):
        '''takes a group and returns a list of espn numbers'''
        golfers = self.get_golfers()

        post_cut_wd = espn_api_data.golfers_post_cut_wd(golfers)     
        return post_cut_wd


    def cut_penalty(self):
        if self.number in [1, 2, 3]:
            return True
        else:
            return False


    def cut_penalty_score(self, score_dict=None, espn_api_data=None):
        if not score_dict and not espn_api_data:
            raise Exception('cut penalty score requires either a score dict or api data')
        
        if not self.cut_penalty():
            return 0
        elif score_dict:
            cut_count = self.cut_count(score_dict, espn_api_data)
            return self.playerCnt - cut_count
       # elif espn_api_data:
       #     cut_count = self.cut_count(espn)

    def lock_group(self, espn_api, user):
        if Picks.objects.filter(user=user, playerName__group=self).exists():
            started_count = 0
        for p in Picks.objects.filter(user=user, playerName__group=self, playerName__tournament=self.tournament):
            if espn_api.player_started(p.playerName.golfer.espn_number):
                started_count += 1
                if started_count == self.num_of_picks():
                    return True
        return False



class Golfer(models.Model):
    golfer_pga_num = models.CharField(max_length=100)
    golfer_name = models.CharField(max_length=100)
    pic_link  = models.URLField(max_length=500, null=True, blank=True)
    flag_link = models.URLField(max_length=500, null=True, blank=True)
    espn_number = models.CharField(max_length=100, null=True, blank=True)
    results = models.JSONField(null=True, blank=True)


    def __str__(self):
        return str(self.golfer_name) + ' : ' + str(self.golfer_pga_num)

    def pga_web_name_format(self):
        if  self.golfer_name[1]=='.' and self.golfer_name[3] =='.':
            return self.golfer_name[0].lower() + '-' + self.golfer_name[2].lower() + '--' + self.golfer_name.split(' ')[1].strip(', Jr.').lower()
        else:
            return self.golfer_name.split(' ')[0] + '-' + self.golfer_name.split(' ')[1]

    # def golfer_link(self):
        
    #     if  self.golfer_name[1]=='.' and self.golfer_name[3] =='.':
    #         name = str(self.golfer_pga_num) + '.' + self.pga_web_name_format()
    #     else:
    #         name = str(self.golfer_pga_num) + '.' + self.pga_web_name_format()
    #     return 'https://www.pgatour.com/players/player.' + unidecode(name) + '.html'

    def espn_link(self):
        if not self.espn_number:
            return None
        name = ''
        name_list = self.golfer_name.split(' ')
        for word in name_list:
            if name != '':
                name = name + '-' + word 
            else:
                name = word

        return 'https://www.espn.com/golf/player/_/id/' + self.espn_number +'/' + name.lstrip().lower().replace(',','').replace('.', '')
        

    def natural_key(self):
        return self.golfer_pga_num

    def summary_stats(self, season, rerun=False):
        '''takes a golfer object and season object, returns a dict'''
        start = datetime.now()
        d = {'played': 0,
                'won': 0,
                'top10': 0,
                'bet11_29': 0,
                'bet30_49': 0,
                'over50': 0,
                'cuts': 0
                }
        
        fields = Field.objects.filter(tournament__season=season, golfer=self).exclude(tournament__current=True). \
            exclude(tournament__pga_tournament_num__in=season.special_fields()).exclude(withdrawn=True).count()

        if fields == 0:
            print ('summary stats: ', self.golfer_name, ' : first tournament')
            return d
        else:
            last_played = Field.objects.filter(tournament__season=season, golfer=self).exclude(tournament__current=True). \
              exclude(tournament__pga_tournament_num__in=season.special_fields()).latest('pk')
            #print ('diff: ', fields - last_played.season_stats.get('played'), fields, last_played.season_stats.get('played'))
            if rerun:        
                print ('summary stats: ', self.golfer_name, ' : rerun updating all tournaments')
                fields = Field.objects.filter((Q(golfer=self) | Q(partner_golfer=self)), tournament__season=season).exclude(tournament__current=True).exclude(tournament__pga_tournament_num='468').values_list('tournament__pk',flat=True).order_by('tournament__pk')
                t_list = Tournament.objects.filter(pk__in=fields)
            elif fields == last_played.season_stats.get('played'):
                print ('summary stats: ', self.golfer_name, ' : no change returning last t stats')
                return last_played.season_stats
            elif fields - last_played.season_stats.get('played') == 1:
                print ('summary stats: ', self.golfer_name, ' : updating last T only')
                t_list = [last_played.tournament.pk]
                data = Field.objects.get((Q(golfer=self) | Q(partner_golfer=self)), tournament=last_played.tournament).season_stats
                d = {'played': data.get('played'),
                    'won': data.get('won'),
                    'top10': data.get('top10'),
                    'bet11_29': data.get('bet11_29'),
                    'bet30_49': data.get('bet30_49'),
                    'over50': data.get('over50'),
                    'cuts': data.get('cuts')
                        }
            else:
                print ('summary stats: ', self.golfer_name, ' : updating all tournaments')
                fields = Field.objects.filter((Q(golfer=self) | Q(partner_golfer=self)), tournament__season=season).exclude(tournament__current=True).exclude(tournament__pga_tournament_num='468').values_list('tournament__pk',flat=True).order_by('tournament__pk')
                #print (fields)
                t_list = Tournament.objects.filter(pk__in=fields)

        played = 0

        # if rerun:        
        #     fields = Field.objects.filter((Q(golfer=self) | Q(partner_golfer=self)), tournament__season=season).exclude(tournament__current=True).exclude(tournament__pga_tournament_num='468').values_list('tournament__pk',flat=True).order_by('tournament__pk')
        #     t_list = Tournament.objects.filter(pk__in=fields)

        # elif Field.objects.filter((Q(golfer=self) | Q(partner_golfer=self)), tournament__season=season).exclude(tournament__current=True).exclude(tournament__pga_tournament_num='468').count() == \
        #       Field.objects.get((Q(golfer=self) | Q(partner_golfer=self)), tournament__current=True).season_stats.get('played'):
        #     print ('golfer stats already up to date: ', self)
        # else:
        #     #fields = Field.objects.filter((Q(golfer=self) | Q(partner_golfer=self)), tournament__season=season).exclude(tournament__current=True).exclude(tournament__pga_tournament_num='468').values_list('tournament__pk',flat=True).order_by('tournament__pk')
        #     t_list = []
        #     t_list.append(Tournament.objects.exclude(current=True).exclude(pga_tournament_num='468').latest('pk').pk)

        
        #for sd in ScoreDict.objects.filter(tournament__season=season).exclude(tournament__current=True):
        for sd in ScoreDict.objects.filter(tournament__pk__in=t_list):
            #if sd.tournament.pga_tournament_num == '470':
            if sd.tournament.special_field() and sd.tournament.pga_tournament_num != '018':
                continue
            
            try:
                if sd.data:
                    x = [v.get('rank') for k, v in sd.data.items() if k !='info' and v.get('pga_num') in [self.espn_number, self.golfer_pga_num]]
                    print (sd.tournament, x)
                if not x:
                    print (self, 'not in sd: ', sd.tournament)
                    continue
                    
                elif x[0] in sd.tournament.not_playing_list():
                    played += 1
                    t = d.get('cuts') + 1
                    d.update({'cuts':  t})
                elif utils.formatRank(x[0]) == 1:
                    played += 1
                    t = d.get('won') + 1
                    d.update({'won':  t})
                elif utils.formatRank(x[0]) < 11:
                    played += 1
                    t = d.get('top10') + 1
                    d.update({'top10':  t})
                elif utils.formatRank(x[0]) < 30:
                    played += 1
                    t = d.get('bet11_29') + 1
                    d.update({'bet11_29':  t})
                elif utils.formatRank(x[0]) < 50:
                    played += 1
                    t = d.get('bet30_49') + 1
                    d.update({'bet30_49':  t})
                elif utils.formatRank(x[0]) >= 50:
                    played += 1
                    t = d.get('over50') + 1
                    d.update({'over50':  t})
                #print (d)
            except Exception as e:
                print ('summary stats issue: ', self, sd.tournament, e)
        #d.update({'played': played})
        d.update({'played': d.get('played') + played})
        #print ('summary stats: ', self, d, datetime.now() - start)
        return d

    def get_season_results(self, season=None, rerun=False, espn_api=None, t_list=None):
        '''takes a golfer and an optional season object, returns a dict with only the updated data'''
        # fix so this runs from 2021 and beyond
        start = datetime.now()
        if not season:
            curr_s = Season.objects.get(current=True)
            if Tournament.objects.filter(season=curr_s).count() > 1:
                season = Season.objects.get(current=True)
            else:
                season = Season.objects.get(season=str(int(curr_s.season)-1))

        if t_list:
            tournaments=t_list
        elif self.results and not rerun:
            tournaments = Tournament.objects.filter(season__season__gte='2021').exclude(pk__in=list(self.results.keys())).exclude(current=True).exclude(pga_tournament_num='468') #ryder cup
        else:
            tournaments = Tournament.objects.filter(season__season__gte='2021').exclude(current=True).exclude(pga_tournament_num='468')
            self.results = {}
        
        # print ('Updating golfer results: ', self)
        #print ('golfer results post t : ', self, datetime.now() - pre_t, tournaments)
        for t in tournaments:
            sd = ScoreDict.objects.get(tournament=t)
            if not t.special_field() or (t.season.season > 2021 and t.pga_tournament_num == '018'):
                score = [v for k, v in sd.data.items() if k != 'info' and v.get('pga_num') == self.espn_number] 
                #print (score[0].get('rank'))
                if score:
                    rank = score[0].get('rank')
                else:
                    rank = 'n/a'
            #elif t.pga_tournament_num == '470':
            #    from golf_app import espn_api
            #    if Field.objects.filter(golfer=self, tournament=t).exists():
            #        if not espn_api:
            #            espn = espn_api.ESPNData(t=f.tournament, data=sd.espn_api_data)
            #       f = Field.objects.get(golfer=self, tournament=t)
            #        rank = str(f.mp_calc_score(espn.mp_golfers_per_round(), espn))
            #    else:
            #        rank = 'n/a'
            elif t.season.season >= 2022 and t.pga_tournament_num == '470' and Field.objects.filter(golfer=self, tournament=t).exists():
                from golf_app import espn_api
                sd = ScoreDict.objects.get(tournament=t)
                espn = espn_api.ESPNData(t=t, data=sd.espn_api_data)
                f = Field.objects.get(golfer=self, tournament=t)
                rank = str(f.mp_calc_score(espn.mp_golfers_per_round(), espn))
            elif t.season.season == 2021 and t.pga_tournament_num == '470' and Field.objects.filter(golfer=self, tournament=t).exists():
                f = Field.objects.get(golfer=self, tournament=t)
                rank = str(f.get_mp_result(t))
            else:
                rank = 'n/a'

            res = self.results
            #self.results.update({t.pk: {'rank': rank,
            res.update({t.pk: {'rank': rank,
                                't_name': t.name,
                                'season': t.season.season
                }})
            self.results = res


        #self.results.update(data)
        self.save()
        #print (data)
        #print (self.golfer_name, datetime.now() - start)
        return self.results

    def get_pga_player_link(self):
        try:
            if self.golfer_name[1]=='.' and self.golfer_name[3] =='.':
                name = str(self.golfer_pga_num) + '.' + self.golfer_name[0].lower() + '-' + self.golfer_name[2].lower() + '--' + self.golfer_name.split(' ')[1].replace(', Jr.', '').lower()
            else:
                name = str(self.golfer_pga_num) + '.' + self.golfer_name.split(' ')[0].lower() + '-' + self.golfer_name.split(' ')[1].replace(', Jr.', '').lower()
            #print ('name', name)
            link = 'https://www.pgatour.com/players/player.' + unidecode.unidecode(name) + '.html'
            return link
        except Exception as e:
            print ('get pga player link exception', e)
            return None

    def get_flag(self):
        from golf_app import espn_golfer_base_data_api
        #try:
        #     player_html = urllib.request.urlopen(self.get_pga_player_link())
        #     player_soup = BeautifulSoup(player_html, 'html.parser')
        #     country = (player_soup.find('div', {'class': 'country'}))
        #     flag = country.find('img').get('src')

        #     return  "https://www.pgatour.com" + flag
        # except Exception as e:
        #     print ('Issue with PGA.com Flag lookup use espn?: ', self.golfer_name, e)
        #     return None
        try:
            return espn_golfer_base_data_api.ESPNGolfer(self.espn_number).get_flag()
        except Exception as e:
            print ('issue with espn flag lookup', e)
            return None


    def get_fedex_stats(self):
        #not reliable as pga site frequently fails to load player
        try:
            player_html = urllib.request.urlopen(self.get_pga_player_link())
            player_soup = BeautifulSoup(player_html, 'html.parser')
            fedex_rank = player_soup.find('div', {'class': 'career-notes'}).find_all('div',{'class': 'value'})[0].text.lstrip().rstrip()
            fedex_points = player_soup.find('div', {'class': 'career-notes'}).find_all('div',{'class': 'value'})[1].text.lstrip().rstrip()

            return  {'rank': fedex_rank, 'points': fedex_points}
        except Exception as e:
             print ('Issue with get_fedex_stats: ', self.golfer_name, e)
             return {'rank': None, 'points': None}

    def get_pic_link(self):
        return "https://pga-tour-res.cloudinary.com/image/upload/c_fill,d_headshots_default.png,f_auto,g_face:center,h_85,q_auto,r_max,w_85/headshots_" + self.golfer_pga_num + ".png"


    def country(self):
        #if self.flag_link.split('/')[9][0:3].upper() == "NIR":
        #    return "IRL"
        #else:
        return self.flag_link.split('/')[9][0:3].upper()

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
    partner_golfer = models.ForeignKey(Golfer, on_delete=models.CASCADE, null=True, related_name='partner_golfer', blank=True)
    partner_owgr = models.IntegerField(unique=False, null=True, blank=True)
    playerID = models.CharField(max_length=100, null=True)
    map_link = models.URLField(null=True, blank=True)
    pic_link = models.URLField(null=True, blank=True)
    golfer = models.ForeignKey(Golfer, on_delete=models.CASCADE, null=True)
    rank = models.CharField(max_length=50, null=True, blank=True)
    handi = models.IntegerField(null=True)
    prior_year = models.CharField(max_length=100, null=True)
    recent = models.JSONField(null=True)
    season_stats = models.JSONField(null=True)

    class Meta:
        ordering = ['-tournament', 'group', 'currentWGR']
        

    def __str__(self):
        return  self.playerName

    def formatted_name(self):
        return self.playerName.replace(' Jr.','').replace('(am)','')

    def prior_year_finish(self):
        try:
            last_season = str(int(self.tournament.season.season)-1)
            t = Tournament.objects.get(pga_tournament_num=self.tournament.pga_tournament_num, season__season=last_season)
        except Exception as e:
            try:
                last_season = str(int(self.tournament.season.season)-2)
                t = Tournament.objects.get(pga_tournament_num=self.tournament.pga_tournament_num, season__season=last_season)
            except Exception as e1:
                try: 
                    if self.tournament.pga_tournament_num == '536':
                        #hard coded for masters 2021 
                        t = Tournament.objects.get(pga_tournament_num='014', season__season='2021')
                    elif self.tournament.pga_tournament_num == '535':
                        #hard coded for US Openrs 2021 
                        t = Tournament.objects.get(pga_tournament_num='026', season__season='2021')

                except Exception as e2:
                    print ('cant find prior tournament ', e2)
                    return 'n/a'
        #print (t, t.season)
        try:
            sd = ScoreDict.objects.get(tournament=t)
            if t.pga_tournament_num != "470":
                rank = [v.get('rank') for k, v in sd.data.items() if k !='info' and v.get('pga_num') in [self.golfer.espn_number, self.golfer.golfer_pga_num]]
                #print (rank)
                if rank[0] != '-':
                    return rank[0]
                else:
                    mdf = [v for k, v in sd.data.items() if k !='info' and v.get('pga_num') in [self.golfer.espn_number, self.golfer.golfer_pga_num]]
                    if mdf[0].get('r4') == '--' and int(mdf[0].get('r3')) > 0:
                        return "MDF"
                    else:
                        return rank[0]

            else:
                return str(self.get_mp_result(t))
        except Exception as e:
            #print ('prior_year_exception', self, e)
            return 'n/a'

    def handicap(self):
        if self.tournament.pga_tournament_num == '018': #Zurich
            return 0
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

    def recent_results(self):
        from golf_app import espn_api
        data = {}
        start = datetime.now()
        for t in Tournament.objects.all().order_by('pk').exclude(pga_tournament_num='468').reverse()[1:5]:  # excld ryder cup
            try:

                if Field.objects.filter(tournament=t, golfer=self.golfer).exclude(withdrawn=True).exclude(golfer__espn_number__isnull=True).exists():
                    sd = ScoreDict.objects.get(tournament=t)
                    #f = Field.objects.get(tournament=t, golfer__espn_number=self.golfer.espn_number)
                    f = Field.objects.get(tournament=t, golfer=self.golfer)
                    
                    if t.pga_tournament_num not in ['470',]:
                        x = [v.get('rank') for k, v in sd.data.items() if k !='info' and v.get('pga_num') in [self.golfer.espn_number, self.golfer.golfer_pga_num]]
                        if len(x) > 0:
                            data.update({t.pk:{'name': t.name, 'rank': x[0]}})
                        else:
                            data.update({t.pk:{'name': t.name, 'rank': 'DNP'}})    
                    elif t.pga_tournament_num == '470':
                        #data.update({t.pk: {'name': t.name, 'rank': 'MP ' + str(self.get_mp_result(t))}})  #for 2021 using pga data
                        espn = espn_api.ESPNData(t=f.tournament, data=sd.espn_api_data)
                        data.update({t.pk: {'name': t.name, 'rank': 'MP ' + str(self.mp_calc_score(espn.mp_golfers_per_round(), espn))}})
                elif Field.objects.filter(tournament=t, partner_golfer__espn_number=self.golfer.espn_number).exclude(withdrawn=True).exclude(partner_golfer__espn_number__isnull=True).exists():
                    sd = ScoreDict.objects.get(tournament=t)
                    f = Field.objects.get(tournament=t, partner_golfer__espn_number=self.golfer.espn_number)
                    x = [v.get('rank') for k, v in sd.data.items() if k !='info' and v.get('pga_num') in [self.golfer.espn_number, self.golfer.golfer_pga_num]]
                    if len(x) > 0:
                        data.update({t.pk:{'name': t.name, 'rank': x[0]}})
                    else:
                        data.update({t.pk:{'name': t.name, 'rank': 'DNP'}})    
                else:
                    data.update({t.pk:{'name': t.name, 'rank': 'DNP'}})
            except Exception as e:
                print ('recent results exception', e, t, self, self.golfer.golfer_pga_num)
                data.update({t.pk:{'name': t.name, 'rank': 'error'}})
        #print ('recent results: ', self, datetime.now() - start)
        return data

    def get_mp_result(self, t):
        #for PGA score file/dict.  new function for espn

        sd = ScoreDict.objects.get(tournament=t)

        if {k:v for k, v in sd.data.items() if k == 'Finals' and {num:match for num, match in v.items() if match.get('winner') == self.playerName}}:
            return 1 
        elif {k:v for k, v in sd.data.items() if k == 'Finals' and {num:match for num, match in v.items() if match.get('loser') == self.playerName}}:
            return 2
        elif {k:v for k, v in sd.data.items() if k == '3rd Place' and {num:match for num, match in v.items() if match.get('winner') == self.playerName}}:
            return 3
        elif {k:v for k, v in sd.data.items() if k == '3rd Place' and {num:match for num, match in v.items() if match.get('loser') == self.playerName}}:
            return 4
        elif {k:v for k, v in sd.data.items() if k == 'Quarterfinals' and {num:match for num, match in v.items() if match.get('loser') == self.playerName}}:
            return 5
        elif {k:v for k, v in sd.data.items() if k == 'Round of 16' and {num:match for num, match in v.items() if match.get('loser') == self.playerName}}:
            return 9
        elif Field.objects.filter(tournament=t, golfer=self.golfer).exists():
            return 17
        else:
            return 'n/a'

    
    def p1_owgr(self):
        return self.currentWGR - self.partner_owgr

    def started(self, score_dict=None):
        from golf_app import espn_api

        if not score_dict:
           sd = espn_api.ESPNData().player_started(self.golfer.espn_number)
        else:
           sd = score_dict
        
        return sd

        #if sd.get('info').get('round') > 1:
        #    return True
        
        #if sd.get('info').get('round') == 1 and self.playing(sd):
        #    return True
        #else:
        #    return False
        
    def playing(self, score_dict=None):
        from golf_app import scrape_espn

        if self.tournament.pga_tournament_num == '468' and not self.tournament.started():
            return False
        elif self.tournament.pga_tournament_num == '468' and self.tournament.started():
            return True


        if not score_dict:
           sd = scrape_espn.ScrapeESPN().get_data()
        else:
           sd = score_dict

        if sd.get('info').get('round') == 1 and sd.get('info').get('round_status') == 'Not Started':
            return False

        data = {v.get('thru') for k,v in sd.items() if v.get('pga_num') == self.golfer.espn_number}

        if len(data) == 0:
            return False

        x = ['AM', 'PM']
        for status in self.tournament.not_playing_list():
            x.append(status)
        #print (x) 
        if any(c in data for c in x):
            return False
        return True

    def fedex_pick(self, user):
        if FedExPicks.objects.filter(user=user, pick__golfer=self.golfer):
            return True
        return False 

    def calc_score(self, sd=None, api_data=None):
        start = datetime.now()
        if not sd and not api_data:
            raise Exception('field calc score requires either a score dict or api data')
        
        if self.handi:  #need this check for fields before handi logic
            handi = self.handi
        else: 
            handi = 0

        cut = False
        
        if sd: 
            rank = [v.get('rank') for k,v in sd.items() if k != 'info' and v.get('pga_num') == self.golfer.espn_number][0]

            if rank in self.tournament.not_playing_list():
                cut = True
                post_cut_wd_count = utils.post_cut_wd_count(self.tournament, sd)
                if post_cut_wd_count > 0 and self.post_cut_wd():
                    score = len(v for k,v in sd.items() if k != 'info' and v.get(rank) not in self.tournament.not_playing_list())
                else:                
                    score = (int(sd.get('info').get('cut_num')) + self.group.cut_penalty_score(sd) + post_cut_wd_count) - handi
            else:
                score = [v.get('rank') - handi for v in sd.values() if v.get('espn_num') == self.golfer.espn_number][0]
        
        
        if api_data:
            #print ('models calc score: ', self, api_data.get_rank(self.golfer.espn_number), int(api_data.cut_num()))
            if api_data.golfer_data(self.golfer.espn_number):
                if api_data.golfer_data(self.golfer.espn_number).get('status').get('type').get('id') == "3":
                    if self.post_cut_wd(api_data=api_data):
                        cut = False
                        score = int(api_data.post_cut_wd_score()) - int(self.handi)
                    else:
                        cut = True
                        score = (int(api_data.cut_num()) - int(self.handi)) + api_data.cut_penalty(self)
                elif self.tournament.has_cut and int(api_data.get_round()) <= int(self.tournament.saved_cut_round) \
                     and int(api_data.get_rank(self.golfer.espn_number)) >= int(api_data.cut_num()):
                    cut = True
                    score = (api_data.cut_num() - int(self.handi)) + api_data.cut_penalty(self)
                else: 
                    score = int(api_data.get_rank(self.golfer.espn_number)) - int(self.handi)

            else:
                print ('WD? not found in espn: ',  self.playerName, self.golfer.espn_number) 
                cut = True
                score = (int(api_data.cut_num()) - int(self.handi)) + api_data.cut_penalty(self)
        #print ('golfer:', self.playerName, 'calc SCORE ', score, 'cut: ', cut)
        #print ('calc score dur: ', self, datetime.now() - start)
        return {'score': score, 'cut': cut}


    def post_cut_wd(self, sd=None, api_data=None):
        if not sd and not api_data:
            raise Exception('field post cut wd requires either a score dict or api data')
        
        if sd and len([v for k,v in sd.items() if k!= 'info' and v.get('pga_num')  == self.golfer.espn_number and \
            v.get('r3') != '--']) > 0:
            return True
        elif sd:
            return False

        if api_data:
            l = self.tournament.not_playing_list()
            l.remove('CUT')
            if api_data.golfer_data(self.golfer.espn_number).get('status').get('type').get('id')  == '3' and \
               api_data.get_round_score(self.golfer.espn_number, 3) not in [None, '--', '0', 0] and \
               api_data.golfer_data(self.golfer.espn_number).get('status').get('type').get('shortDetail') in l:
                return True
            else:
                return False

        return False 

    def mp_calc_score(self, round_data, espn_data=None):
        '''used with espn api data'''
        from golf_app import espn_api
        if not round_data.get('Rd of 16'):
            sd = ScoreDict.objects.get(tournament=self.tournament)
            if not espn_data:
                espn_data = espn_api.ESPNData(t=self.tournament, data=sd.espn_api_data)
            data = espn_data.mp_group_rank(self)
            return data.get(self.pk)
            #return 0
        elif self.golfer.espn_number not in round_data.get('Rd of 16'):
            return 17
        elif round_data.get('Quarterfinals') and self.golfer.espn_number not in round_data.get('Quarterfinals'):
            return 9
        elif round_data.get('Semifinals') and self.golfer.espn_number not in round_data.get('Semifinals'):
            return 5
        elif round_data.get('fourth') and self.golfer.espn_number in round_data.get('fourth'):
            return 4
        elif round_data.get('third') and self.golfer.espn_number in round_data.get('third'):
            return 3
        elif round_data.get('second') and self.golfer.espn_number in round_data.get('second'):
            return 2
        elif round_data.get('first') and self.golfer.espn_number in round_data.get('first'):
            return 1

        return 0


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
    CHOICES = (('1', 'player'), ('2', 'random'), ('3', 'auto'), ('4', 'fixed_auto'))

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
    BONUS_CHOICES = (('1', 'winning golfer'), ('2', 'no cuts'), ('3', 'weekly winner'), 
                     ('4', 'playoff'), ('5', 'best in group'), ('6', 'trifecta'), ('7', 'manual'),
                     ('9', 'Ryder Cup winner'), ('10', 'Ryder Cup Score'))

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, null=True)
    winner_bonus = models.IntegerField(default=0)
    cut_bonus = models.IntegerField(default=0)
    major_bonus = models.IntegerField(default=0)
    playoff_bonus = models.BigIntegerField(default=0)
    best_in_group_bonus = models.BigIntegerField(default=0)
    bonus_type = models.CharField(max_length=100, choices=BONUS_CHOICES, null=True)
    bonus_points = models.IntegerField(default=0)


    def __str__(self):
        return str(self.user)

    class Meta():
        unique_together = ('tournament', 'user', 'bonus_type')


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

    def rank(self):
        pass


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


class RyderCupMatch(models.Model):
    play_format  = models.CharField(max_length=50)
    match_num = models.CharField(max_length=50)
    data_links = models.JSONField(null=True, blank=True)
    usa_golfer = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='usa_golfer')
    euro_golfer = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='euro_golfer')
    winner = models.ForeignKey(Field, on_delete=models.CASCADE, null=True, blank=True, related_name='winner')
    loser = models.ForeignKey(Field, on_delete=models.CASCADE, null=True, blank=True, related_name='loser')
    result = models.CharField(max_length=10, null=True, blank=True)
    winner_score = models.CharField(max_length=10, null=True)
    loser_score = models.CharField(max_length=10, null=True)
    

    def __str__(self):
        return str(self.play_format) + str(self.usa_golfer.playerName) + str(self.euro_golfer.playerName)


class ScoreDict(models.Model):
    tournament = models.ForeignKey(Tournament, null=True, on_delete=models.CASCADE, related_name='score_dict')
    data = models.JSONField(null=True)
    pick_data = models.JSONField(null=True)
    cbs_data = models.JSONField(null=True)
    espn_api_data = models.JSONField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)



    def __str__(self):
        return (self.tournament.name)

    def sorted_dict(self):
        d = self.data
        for k, v in d.items():
            v.update({'sort_rank': utils.formatRank(v.get('rank'))})
        
        sorted_score_dict = {k:v for k, v in sorted(d.items(), key=lambda item: item[1].get('sort_rank'))}
        
        return sorted_score_dict

    def clean_dict(self):
        return  {key.replace('(a)', '').strip(): v for key, v in self.data.items()}
    
    
    def data_valid(self):
        
        if self.tournament.special_field() and self.tournament.pga_tournament_num != '018':
            return True

        if not self.data: return False
        good = True
        field_len = Field.objects.filter(tournament=self.tournament).count()
        sd_len = len(self.data) - 1  #minus 1 for the info entry

        if sd_len - field_len == 0:
            pass
        elif abs(sd_len - field_len) < 5:
            print ("SD Match with diffs less than 5", self.tournament)
        else:
            #good = False
            print ("BAD SD based on counts: ", self.tournament, ' SD Len: ', sd_len, ' Field Len: ', field_len)
            return False

        #if self.data.get('info').get('complete') == "False" or self.data.get('info').get('round_status') != 'Final':
        if self.data.get('info').get('round_status') != 'Final':
            print ("T not complete", self.tournament, self.data.get('info'))
            return False

        best = ScoreDetails.objects.filter(pick__playerName__tournament=self.tournament).exclude(gross_score__isnull=True).order_by('gross_score').first()
        print (best)
        
        match = {k:v for k,v in self.data.items() if k != 'info' and v.get('pga_num') == \
            best.pick.playerName.golfer.espn_number and utils.formatRank(v.get('rank'), self.tournament) == best.gross_score}
        
        if not match:
            print ('not match match: ', match)
            good = False
        
        return good


    def update_sd_data(self):
        from golf_app import scrape_espn
        sd = {}
        try:
            if self.tournament.pga_tournament_num == '018':
                data = build_zurich_data(self)
                self.data = data
                self.save()
            else:
                espn = scrape_espn.ScrapeESPN(tournament=self.tournament, url='https://www.espn.com/golf/leaderboard?tournamentId=' + self.tournament.espn_t_num, setup=True)
                sd = espn.get_data()
                self.data = sd
                self.save()        
        except Exception as e:
            print ('update sd data exception: ', e)
        return (sd)


def build_zurich_data(sd):
    from golf_app import espn_api 
    d = {}
    espn = espn_api.ESPNData(t=sd.tournament, data=sd.espn_api_data)

    d['info'] = {'round': espn.get_round(),
                'source': 'espn',
                'cut_num': espn.cut_num(),
                'playoff': espn.playoff(),
                'complete': espn.tournament_complete(),
                'cut_line': espn.cut_line().get('cut_core'),
                'round_status': espn.get_round_status()
                }

    for data in espn.field_data:
        for r in data.get('roster'):
 
            try:
 
                print ('build zurich data for espn_num: {}, {}'.format(r.get('playerID'), r.get('athlete').get('displayName')))
                f = Field.objects.get(Q(golfer__espn_number=str(r.get('playerId'))) | Q(partner_golfer__espn_number=str(r.get('playerId'))), tournament=sd.tournament)
                id = r.get('playerId')
                d[r.get('athlete').get('displayName')] = {'pga_num': str(id),
                                                        'r1': espn.get_round_score(id, 1),
                                                        'r2': espn.get_round_score(id, 2),
                                                        'r3': espn.get_round_score(id, 3),
                                                        'r4': espn.get_round_score(id, 4),
                                                        'rank': espn.get_rank(id),
                                                        'thru': espn.get_thru(id),
                                                        'group': f.group.number,
                                                        'change': '',
                                                        'handicap': f.handi,
                                                        'round_score': '',
                                                        'total_strokes': '',
                                                        'total_score': espn.to_par(id)

                
                }
            except Exception as e:
                print ('Issue wiht Zurich sd {}'.format(e))
                try:
                    d[r.get('athlete').get('displayName')] = {'pga_num': str(id),
                                                        'r1': espn.get_round_score(id, 1),
                                                        'r2': espn.get_round_score(id, 2),
                                                        'r3': espn.get_round_score(id, 3),
                                                        'r4': espn.get_round_score(id, 4),
                                                        'rank': espn.get_rank(id),
                                                        'thru': espn.get_thru(id),
                                                        'group': 'none',
                                                        'change': '',
                                                        'handicap': '',
                                                        'round_score': '',
                                                        'total_strokes': '',
                                                        'total_score': espn.to_par(id)

                
                                                             }
                except Exception as f:
                    print ('Zurich SD execpt exception {}'.format(f))
                    continue


    return d




    


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email_picks = models.BooleanField(default=False)

class AccessLog(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    page = models.CharField(max_length=100, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    tournament = models.ForeignKey(Tournament, blank=True, null=True, on_delete=models.CASCADE)
    device_type = models.CharField(max_length=100, blank=True, null=True)
    views = models.PositiveBigIntegerField(default=0, null=True)

    def __str__(self):
        return str(self.user.username) + '  ' + str(self.page)


class AuctionPick(models.Model):
    playerName = models.ForeignKey(Field, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    bid = models.CharField(max_length=100, null=True, blank=True)
    score = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return str(self.user.username) + ' - ' + str(self.playerName.playerName)

class StatLinks(models.Model):
    name = models.CharField(max_length=100)
    link = models.URLField()

class CountryPicks(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    country = models.CharField(max_length=30)
    gender = models.CharField(max_length=30)
    score = models.PositiveBigIntegerField(default=0)
    ryder_cup_score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return str(self.user) + str(self.tournament) + str(self.country)

    def get_flag(self):
        c = self.country.lower()
        return "https://a.espncdn.com/combiner/i?img=/i/teamlogos/countries/500/" + c + ".png&w=40&h=40&scale=crop"


class FedExSeason(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    allow_picks = models.BooleanField(default=True)
    prior_season_data = models.JSONField(default=dict)

    def __str__(self):
        return str(self.season.season)

    def picks_by_golfer(self):

        d = {}
        fedex = self.current_fedex_data()

        for p in FedExPicks.objects.filter(pick__season=self).values('pick__golfer__golfer_name').distinct():
            rank_data = utils.fix_name(p.get('pick__golfer__golfer_name'), fedex)
            if rank_data[0]:
                rank = rank_data[1].get('rank')
                points = rank_data[1].get('points')

            else:
                rank = None
                points = None

            pick = FedExPicks.objects.filter(pick__season=self, pick__golfer__golfer_name=p.get('pick__golfer__golfer_name')).first()
            #score = pick.score(fedex)
            users = list(FedExPicks.objects.filter(pick__season=self, pick__golfer__golfer_name=p.get('pick__golfer__golfer_name')).values_list('user__username', flat=True))

            d[pick.pick.golfer.espn_number] = {'golfer': pick.pick.golfer.golfer_name,
                                                'rank': rank,
                                                'points': points,
                                                'picked_by': users,
                                                'num_picks': len(users),
                                                'score': pick.score, 
                                                'soy_owgr': pick.pick.soy_owgr}
        
        return d

    def player_points(self, user=None, t=None):
        '''takes a fedex season and optional user, tournamanet objects. returns a dict'''
        ### add the correct logic to return points as of a specific tournament
        start = datetime.now()
        user_list = []
        if user:
            user_list.append(user)
        else:
            user_list = self.season.get_users('obj')
        d = {}

        if t:  #need to set up player points here
            fedex = t.fedex_data
            for u in user_list:
                total_score = 0
                for pick in FedExPicks.objects.filter(user=u, pick__season=self):
                    total_score += pick.calc_score(fedex)
                d[u.username] = {'score': total_score}
        else:
            fedex = self.current_fedex_data()
        
        for u in user_list:
            total_score = 0
            for pick in FedExPicks.objects.filter(user=u, pick__season=self):
                total_score += pick.score
            d[u.username] = {'score': total_score}
        
        #ranks = rankdata([x.get('score') for x in d.values()], method='min'))
        ranks = sorted([x.get('score') for x in d.values()])
        #print (ranks)
        
        for k, v in d.items():
            d.get(k).update({'rank': ranks.index(v.get('score')) + 1}) 
        
        print ('fedex points calc Dur: ', datetime.now() - start)

        return d


    def current_fedex_data(self):
        t = Tournament.objects.get(current=True)
        if t.fedex_data:
            fedex = t.fedex_data
        else:
            from golf_app import populateField
            fedex = populateField.get_fedex_data(t)
        
        return fedex
        

    def update_player_points(self):
        for t in Tournament.objects.filter(season=self.season):
            if t.fedex_data and not t.fedex_data.get('player_points'):
                fedex = FedExSeason.objects.get(season__current=True).player_points(t=t)
                t.fedex_data['player_points'] = fedex
            t.save()
        
        return

    def above_below_line(self, user, t=None):
        '''takes a user obj, returns dict'''
        #start = datetime.now()
        d = {}
        if not t:
            t = Tournament.objects.get(current=True)

        picks = list(FedExPicks.objects.filter(pick__season__season__current=True, user=user).values_list('pick__golfer__golfer_name', flat=True))
        not_in_fedex = len([x for x in picks if x not in t.fedex_data.keys()]) 
        in_top30 = len([x.get('rank') for k, x in t.fedex_data.items() if k in picks and int(x.get('rank')) < 31])
        above_top30 = len([x.get('rank') for k, x in t.fedex_data.items() if k in picks and int(x.get('rank')) >= 31])

        d['in_top30'] = in_top30
        d['outside_top30'] = above_top30 + not_in_fedex
       
        #print (datetime.now() - start)
        return d

    def picks_at_risk(self, user, t=None):
        d = {}
        if not t:
            t = Tournament.objects.get(current=True)

        picks = list(FedExPicks.objects.filter(pick__season__season__current=True, user=user).values_list('pick__golfer__golfer_name', flat=True))
        #at_risk = len([x.get('rank') for k, x in t.fedex_data.items() if k in picks and int(x.get('rank')) >= 20 and int(x.get('rank')) < 31])
        at_risk = {k:x.get('rank') for k, x in t.fedex_data.items() if k in picks and int(x.get('rank')) >= 20 and int(x.get('rank')) < 31}
        #onthe_verge = len([x.get('rank') for k, x in t.fedex_data.items() if k in picks and int(x.get('rank')) >= 31 and int(x.get('rank')) < 51])
        otv_data = {k:v for k, v in t.fedex_data.items() if k in picks and int(v.get('rank')) >= 31 and int(v.get('rank')) < 51}
        top_70 = {k:x.get('rank') for k, x in t.fedex_data.items() if k in picks and int(x.get('rank')) >= 51 and int(x.get('rank')) < 71}

        d['at_risk'] = len(at_risk)
        d['onthe_verge'] = len(otv_data)
        d['top_70'] = len(top_70)


        at_risk_potential_score = 0
        for k,v in at_risk.items():
            p = FedExPicks.objects.get(user=user, pick__golfer__golfer_name=k, pick__season__season__current=True)
            if p.pick.soy_owgr > 30:
                at_risk_potential_score += 80
            elif p.pick.soy_owgr < 30:
                at_risk_potential_score += 30

        d['at_risk_potential'] = at_risk_potential_score


        potential_score = 0
        for k,v in otv_data.items():
            p = FedExPicks.objects.get(user=user, pick__golfer__golfer_name=k, pick__season__season__current=True)
            if p.pick.soy_owgr > 30:
                potential_score += 80
            elif p.pick.soy_owgr < 30:
                potential_score += 30

        d['otv_potential'] = potential_score

        top70_potential_score = 0
        for k,v in top_70.items():
            p = FedExPicks.objects.get(user=user, pick__golfer__golfer_name=k, pick__season__season__current=True)
            if p.pick.soy_owgr > 30:
                top70_potential_score += 80
            elif p.pick.soy_owgr < 30:
                top70_potential_score += 30

        d['otv_potential'] = potential_score
        d['top70_potential'] = top70_potential_score


        #print (datetime.now() - start)
        return d


    def picks_by_score(self, user, t=None):
        if not t:
            t = Tournament.objects.get(current=True)
        
        d = {'minus_80': 0,
            'plus_20': 0}
        for p in FedExPicks.objects.filter(pick__season__season__current=True, user=user):
            score = p.calc_score(t.fedex_data)
            if score == -80:
                d.update({'minus_80': d.get('minus_80') + 1})
            elif score == 20:
                d.update({'plus_20': d.get('plus_20') + 1})
        return d


    def top_3(self, t=None):
        if not t:
            t = Tournament.objects.get(current=True)
        
        if t.fedex_data:
            return {k:v for k,v in t.fedex_data.items() if v.get('rank') in [1, 2, 3, '1', '2', '3']}
        else:
            return {}

        

class FedExField(models.Model):
    season = models.ForeignKey(FedExSeason, on_delete=models.CASCADE)
    golfer = models.ForeignKey(Golfer, on_delete=models.CASCADE)
    soy_owgr = models.IntegerField(null=True)
    rank = models.IntegerField(null=True)
    prior_season_data = models.JSONField(null=True)
    current_season_data = models.JSONField(null=True)

    def __str__(self):
        return str(self.season.season.season) + ' ' + str(self.golfer.golfer_name)


class FedExPicks(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pick = models.ForeignKey(FedExField, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    top_3 = models.BooleanField(null=True, default=False)

    def __str__(self):
        return str(self.user.username) + ' ' + str(self.pick.golfer.golfer_name)


    def all_picks_view(self):
        print (FedExPicks.objects.filter(season__current=True).values('user__username').annotate('pick__golfer__golfer_name'))


    def calc_score(self, fedex=None):
        '''takes a picks returns an int'''
        if not fedex:
            fedex = self.pick.season.current_fedex_data()
        rank_data = utils.fix_name(self.pick.golfer.golfer_name, fedex)
        score = 0 
        if rank_data[0]:
            rank = int(rank_data[1].get('rank'))
            if rank < 31 and self.pick.soy_owgr < 31:
                score = -30
            elif rank < 31 and self.pick.soy_owgr > 30:
                score = -80
            elif rank >= 31 and self.pick.soy_owgr <= 30:
                score = 20
            else:
                score = 0
        else:
            if self.pick.soy_owgr < 30:
                score = 20
            #else:
            #    score = 0
        
        self.score = score
        self.save()
        return score


    def potential_score(self, fedex=None):
        '''takes a picks returns an int'''
        if not fedex:
            fedex = self.pick.season.current_fedex_data()
        #rank_data = utils.fix_name(self.pick.golfer.golfer_name, fedex)
        score = 0
        #print (rank_data) 
        # if rank_data[0]:
        #     rank = int(rank_data[1].get('rank'))
        #     if rank < 31 and self.pick.soy_owgr < 31:
        #         score = -30
        #     elif rank < 31 and self.pick.soy_owgr > 30:
        #         score = -80
        #     elif rank >= 31 and self.pick.soy_owgr <= 30:
        #         score = 20
        #     else:
        #         score = 0
        # else:
        #     if self.pick.soy_owgr < 30:
        #         score = 20
        #     #else:
        #     #    score = 0
        
        # self.score = score
        # self.save()
        return score



class Round(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    round_num = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True) 
    espn_api_data = models.JSONField(null=True, blank=True)