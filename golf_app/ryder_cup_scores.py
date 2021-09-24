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
            #print (p)
            pick = Picks.objects.filter(playerName__pk=p.get('playerName')).first()
            sd, sd_created = ScoreDetails.objects.get_or_create(user=pick.user, pick=pick)

            if  sd.pick.playerName.golfer.country() == 'USA':
                country = 'USA'
            else:
                country = "EURO"

            data = {k:v for k,v in self.score_dict.items() if k != 'overall' and v.get('country')}
            print (data)
        return
        
