import json
from golf_app.models import Picks, Tournament, TotalScore, BonusDetails, ScoreDetails, PickMethod, \
    Group, Field
from django.contrib.auth.models import User
from golf_app import utils
#from datetime import datetime
#from django.db.models import Count, Max, Min
from django.db import transaction
#import random


class Bonus(object):
    
    def __init__(self, tournament, user):
    
        self.tournament = tournament

        self.user == user
        
        self.not_playing_list = ['CUT', 'WD', 'DQ']


    def create_bd(self):
        pass
        #bd = BonusDetails()
        
