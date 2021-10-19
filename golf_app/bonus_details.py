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

class BonusDtl(object):
    
    def __init__(self, tournament=None):
    
        if self.tournament:
            self.tournament = tournament
        else:
            self.tournament = Tournament.objects.get(current=True)
        
        self.t_status = status

    
    def best_in_group(self, optimal_picks, pick):
        '''takes a dict of optimal picks and a pick object, updates DB, returns nothing'''
        if pick.playerName.golfer.espn_number in optimal_picks.keys():
            for best in Picks.objects.filter(playerName__golfer__espn_number=pick.playerName.golfer.espn_number, playerName__tournament=self.tournament):
                if not PickMethod.objects.filter(user=best.user, method=3, tournament=best.playerName.tournament).exists() \
                    and not pick.is_winner() \
                    and not pick.playoff_loser() \
                    and best.playerName.group.playerCnt > 4:
                        big_bd, created = BonusDetails.objects.get_or_create(user=best.user, tournament=self.tournament, bonus_type='5')
                        big_bd.bonus_points += 10
                        big_bd.save()
        return