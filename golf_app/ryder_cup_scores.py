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
            self.tournament = Tournament.objects.get(season__current=True, pga_tournament_num='468')
        else:
            self.tournament = tournament
        
        self.score_dict = score_dict


    def update_scores(self):
        start =  datetime.now()

        if self.tournament.complete:
            return


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
                    #print (session, pick, status)
                    if len(status) == 0:
                        score += 5
                    elif status[0] in ['1', '2']:
                        continue
                    else:
                        match_score = [v.get(pick.playerName.golfer.espn_number).get('score') for k, v in match.items() if v.get(pick.playerName.golfer.espn_number)]
                        
                        if match_score[0].get('draw'):
                            score -= 5
                        elif match_score[0].get('winner'):
                            score -= 10
                            score -= int(match_score[0].get('value'))
                        else:
                            score += 10
                            score += int(match_score[0].get('value'))
            
            print (pick, score)    

            sd = ScoreDetails.objects.filter(pick__playerName__tournament=self.tournament, pick__playerName=pick.playerName).update(score=score)
            
    def total_scores(self):
        
        start = datetime.now()

        TotalScore.objects.filter(tournament=self.tournament).delete()
        ts_dict = {}

        
        for player in self.tournament.season.get_users():
            ts_loop_start = datetime.now()
            user = User.objects.get(pk=player.get('user'))
            sd = ScoreDetails.objects.filter(pick__playerName__tournament=self.tournament, user=user)
            score = sd.aggregate(Sum('score'))
        
            ts, created = TotalScore.objects.get_or_create(user=user, tournament=self.tournament)
            ts.score = score.get('score__sum')
            
            ts.save()

            ts_dict[ts.user.username] = {'total_score': ts.score}
            print ('ts loop duration', datetime.now() - ts_loop_start)
        #print ('ts dict', ts_dict)
        #if self.tournament.complete:
        #add -100 for winner and country/total points bonuses
    
    # for ts in TotalScore.objects.filter(tournament=self.tournament):
    #     for bd in BonusDetails.objects.filter(tournament=ts.tournament, user=ts.user):
    #         ts.score -= bd.bonus_points
    #         ts.save()
    #         ts_dict[ts.user.username].update({bd.get_bonus_type_display(): bd.bonus_points, 'total_score': ts.score})
    #     ts_dict[ts.user.username].update({'handicap': ts.total_handicap()})

    
        sorted_ts_dict = sorted(ts_dict.items(), key=lambda v: v[1].get('total_score'))
        print ('total score dict: ', ts_dict)
        print ('total_scores duration', datetime.now() - start)
        return dict(sorted_ts_dict)
    
