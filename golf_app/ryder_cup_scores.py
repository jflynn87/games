import urllib.request
import json
from golf_app.models import Picks, Tournament, TotalScore, BonusDetails, ScoreDetails, PickMethod, \
    Group, Field, CountryPicks, Golfer
from django.contrib.auth.models import User
import csv
#from golf_app import calc_score
from golf_app import utils
from datetime import datetime
from django.db.models import Count, Max, Min, Sum
from django.db import transaction
import random
from unidecode import unidecode
from django.utils import timezone
from django.db.models import Q
from golf_app import golf_serializers
from django.http import JsonResponse

class Score(object):
    
    def __init__(self, score_dict, tournament=None):
        if not tournament:
            #self.tournament = Tournament.objects.get(season__current=True, pga_tournament_num='500  ')
            self.tournament = Tournament.objects.get(current=True)
        else:
            self.tournament = tournament
        
        if self.tournament.pga_tournament_num not in ['468', '500']:
            raise Exception('Wrong Tournament, only for RC or Pres Cup')
        self.score_dict = score_dict


    def update_scores(self):
        start =  datetime.now()

        #if self.tournament.complete:
        #    return

        for p in Picks.objects.filter(playerName__tournament=self.tournament).values('playerName').distinct():
            pick_loop_start = datetime.now()
            
            pick = Picks.objects.filter(playerName__pk=p.get('playerName')).first()

            sd, sd_created = ScoreDetails.objects.get_or_create(user=pick.user, pick=pick)
            score = 0
            for session, match in self.score_dict.items():
                if session == 'overall':
                    continue
                else:
                    data = {k:v for k,v in match.items() if v.get(pick.playerName.golfer.espn_number)}
                    status = [v.get('status') for k,v in data.items()]
                    #print (pick, session, status, score)
                    if len(status) == 0:
                        score += 5
                        continue
                    if status[0] in ['1', '2']:
                        print ('not complete ', data)
                        continue
                    else:
                        #print (match)
                        match_score = [v.get(pick.playerName.golfer.espn_number).get('score') for k, v in match.items() if v.get(pick.playerName.golfer.espn_number)]
                        #for k, v in data.items():
                        m_data = [v for k,v in data.items()][0]
                        #print (m_data)
                        winning_holes = [v.get('score').get('value') for k,v in m_data.items() if k != 'status' and v.get('score').get('winner')]
                        #print ('winning holes', winning_holes)

                        #winning_holes = [v.get('score').get('value') for k,v in match.items() if k !='status' and v.get('score').get('winner') == True]
                        
                        #print ('winning holes', winning_holes)
                        if len(match_score) == 0:
                            score += 5    
                        elif match_score[0].get('draw'):
                            score -= 5
                        elif match_score[0].get('winner'):
                            score -= 10
                            #score -= int(match_score[0].get('value'))
                            score -= int(winning_holes[0])
                        else:
                            score += 10
                            print ('loss penalty: ', int(match_score[0].get('value')))
                            score += int(winning_holes[0])
            
                print (pick, score)    
            print ('pre  save ', pick, score)
            sd = ScoreDetails.objects.filter(pick__playerName__tournament=self.tournament, pick__playerName=pick.playerName).update(score=score)
            
    def total_scores(self):
        
        start = datetime.now()

        TotalScore.objects.filter(tournament=self.tournament).delete()
        ts_dict = {}

        
        for player in self.tournament.season.get_users():
            if not Picks.objects.filter(playerName__tournament=self.tournament, user__pk=player.get('user')).exists():
                continue
            ts_loop_start = datetime.now()
            user = User.objects.get(pk=player.get('user'))
            sd = ScoreDetails.objects.filter(pick__playerName__tournament=self.tournament, user=user)
            score = sd.aggregate(Sum('score'))

            ts, created = TotalScore.objects.get_or_create(user=user, tournament=self.tournament)
            ts.score = score.get('score__sum')
            if not ts.score:
                ts.score = 0

            ts.save()

            ts_dict[ts.user.username] = {'total_score': ts.score}
            print ('ts loop duration', datetime.now() - ts_loop_start)
        
        if self.score_dict.get('overall').get('complete'):
            print ('RYDER Cup complete: ', self.score_dict.get('overall').get('complete'))
            overall = [v for k, v in self.score_dict.items() if k =='overall']
            #print (overall)
            winning_team = [k for k, v in overall[0].items() if k not in ['status', 'complete'] and v.get('score').get('value') > 10]
            winning_score = [v.get('score').get('value') for k, v in overall[0].items() if k not in ['status', 'complete'] and v.get('score').get('value') > 10]
            print ('winning team: ', winning_team[0], winning_score[0])
            
            #need this as model and dict have different euro/EUR
            #fixed for pres cup, shouldn't need this anymore  Confirn
            if winning_team[0] == "USA":
                winning_team = 'USA'
            elif winning_team[0] == 'EUR':
                winning_team = 'euro'
            elif winning_team[0] == 'INTL':
                winning_team = 'INTL'

            
            for cp in CountryPicks.objects.filter(tournament=self.tournament, country=winning_team):
                #if cp.county == winning_team:
                bd, created = BonusDetails.objects.get_or_create(user=cp.user, tournament=self.tournament, bonus_type=9, bonus_points=25)
                bd.save()

            if CountryPicks.objects.filter(tournament=self.tournament, country=winning_team).exists():
                if CountryPicks.objects.filter(tournament=self.tournament, ryder_cup_score=winning_score[0], country=winning_team).exists():
                    bonus_scores = [winning_score[0]] 
                else:
                    rc_totals = CountryPicks.objects.filter(tournament=self.tournament, country=winning_team).order_by('ryder_cup_score').values_list('ryder_cup_score', flat=True)
                    print ('ryder cup total score list: ', rc_totals)
                    diff = 28  #set to max 
                    for score in rc_totals:
                        if abs(score-winning_score[0]) < diff:
                            diff = abs(score-winning_score[0])
                    print ('score guess diff: ', diff)
                    bonus_scores = [score for score in rc_totals if abs(winning_score[0]-score) == diff]
                print ('bonus scores: ', bonus_scores)
                for cp in CountryPicks.objects.filter(tournament=self.tournament, country=winning_team, ryder_cup_score__in=bonus_scores):
                    bd, created = BonusDetails.objects.get_or_create(user=cp.user, tournament=self.tournament, bonus_type=10, bonus_points=25)
                    bd.save()
#
                for u in self.tournament.season.get_users():
                    if self.tournament.winning_picks(User.objects.get(pk=u.get('user'))):
                        print ('weekly winner ', User.objects.get(pk=u.get('user')))
                        bd, created = BonusDetails.objects.get_or_create(user=User.objects.get(pk=u.get('user')), tournament=self.tournament, bonus_type='3')
                        field_type = self.tournament.field_quality()
                        if field_type == 'weak':
                            bd.bonus_points = 50 / self.tournament.num_of_winners()
                        elif field_type == 'strong':
                            bd.bonus_points = 100 / self.tournament.num_of_winners()
                        elif field_type == 'major':
                            bd.bonus_points = 150 / self.tournament.num_of_winners()
                        elif field_type == 'special':
                            bd.bonus_points = 125 / self.tournament.num_of_winners()
                        else:
                            print ('no winner ', self.tournament.field_quality())
                        bd.save()
   
            for ts in TotalScore.objects.filter(tournament=self.tournament):
                for bd in BonusDetails.objects.filter(tournament=ts.tournament, user=ts.user):
                    ts.score -= bd.bonus_points
                    ts.save()
                    ts_dict[ts.user.username].update({bd.get_bonus_type_display(): bd.bonus_points, 'total_score': ts.score})
                #ts_dict[ts.user.username].update({'handicap': ts.total_handicap()})

            self.tournament.complete = True
            self.tournament.save()

        sorted_ts_dict = sorted(ts_dict.items(), key=lambda v: v[1].get('total_score'))
        print ('total score dict: ', ts_dict)
        print ('total_scores duration', datetime.now() - start)
        return dict(sorted_ts_dict)
    
