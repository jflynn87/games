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

    def get_sd(self):
        score_dict = {}
        mens_field = scrape_espn.ScrapeESPN(tournament=self.t, url=self.mens_url, setup=True).get_data() 
        womens_field = scrape_espn.ScrapeESPN(tournament=self.t, url=self.womens_url, setup=True).get_data()  #needs set up mode or only retuns mens

        mens_info = mens_field.get('info')
        womens_info = womens_field.get('info')
        #print ('MI: ', mens_info)
        #print ('WI: ', womens_info)
        score_dict = {**mens_field, **womens_field}
        
        #score_dict['info'].update({'mens_info': mens_info})
        #print ('PU: ', womens_field.get('info'))
        #score_dict['info'].update({'womens_info': womens_field.get('info')})
        #print ('AM: ', score_dict.get('info'))

        
        #score_dict['info']['mens_info'].update(mens_info)
        #print ('PM: ', score_dict.get('info'))
        
        #score_dict['info']['womens_info'].update(womens_info)
        #print ('PW: ', score_dict.get('info'))
        print ('PW: ', score_dict.get('info').get('womens_info'))

        #assume mens starts first and womans second. 
        if not mens_field.get('info').get('complete'):
            if mens_field.get('info').get('round') > 1:
                #score_dict['info'] = mens_field.get('info')
                score_dict['info']['round_status'] = mens_field.get('info').get('round_status') + " - Mens"
        else:
            #score_dict['info'] = womens_field.get('info')
            score_dict['info']['round_status'] = mens_field.get('info').get('round_status') + " - Womens.  Men Complete"

        return score_dict



 



    