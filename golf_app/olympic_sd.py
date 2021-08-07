import urllib.request
import json
from golf_app.models import Picks, Tournament, TotalScore, BonusDetails, ScoreDetails, PickMethod, \
    Group, Field
from django.contrib.auth.models import User
import csv
#from golf_app import calc_score
from golf_app import scrape_espn
from datetime import datetime
from django.db.models import Count, Max, Min, Sum
from django.db import transaction
import random
from unidecode import unidecode
from django.utils import timezone
from django.db.models import Q
from golf_app import golf_serializers
from django.http import JsonResponse

class OlympicScores(object):
    
    def __init__(self, mens_url=None, womens_url=None):
        if not mens_url:
            self.mens_url = 'https://www.espn.com/golf/leaderboard?tournamentId=401285309'
        else:
            self.mens_url = url
        
        if not womens_url:
            self.womens_url = 'https://www.espn.com/golf/leaderboard/_/tour/womens-olympics-golf'
        else:
            self.womens_url = url

        self.t = Tournament.objects.get(season__current=True, pga_tournament_num='999')

    def get_mens_field(self):
        mens_field = scrape_espn.ScrapeESPN(tournament=self.t, url=self.mens_url, setup=True).get_data() 
        return mens_field

    def get_womens_field(self):
        womens_field = scrape_espn.ScrapeESPN(tournament=self.t, url=self.womens_url, setup=True).get_data()  #needs set up mode or only retuns mens
        return womens_field

    def get_sd(self):
        score_dict = {}
        mens_field = self.get_mens_field()
        womens_field = self.get_womens_field()
        print ('MENS INFO: ', mens_field.get('info'))

        mens_info = mens_field.get('info')
        for k, v in mens_field.items():
            v.update({'gender': 'men'})
        womens_info = womens_field.get('info')
        for k, v in womens_field.items():
            v.update({'gender': 'women'})

        score_dict = {**mens_field, **womens_field}

        #assume mens starts first and womans second. 
        if not mens_field.get('info').get('complete'):
            if mens_field.get('info').get('round') > 1:
                score_dict['info']['round_status'] = mens_field.get('info').get('round_status') + " - Mens"
                score_dict['info']['mens_complete'] = mens_field.get('info').get('complete')
                score_dict['info']['womens_complete'] = womens_field.get('info').get('complete')
        else:
            score_dict['info']['round_status'] = womens_field.get('info').get('round_status') + " - Womens.  Men Complete"
            score_dict['info']['mens_complete'] = mens_field.get('info').get('complete')
            score_dict['info']['womens_complete'] = womens_field.get('info').get('complete')

        return score_dict

    def get_mens_info(self):
        return (self.get_mens_field().get('info'))


    def get_womens_info(self):
        return (self.get_womens_field().get('info'))

 



    