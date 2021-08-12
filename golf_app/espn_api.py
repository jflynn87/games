from datetime import datetime, timedelta
#import pytz
#import urllib
from requests import get
import json
#from bs4 import BeautifulSoup
from golf_app import utils
from golf_app.models import Tournament, Field, Golfer, ScoreDict, Picks
#from collections import OrderedDict


class ESPNData(object):
    '''takes an optinal dict and provides funcitons to retrieve espn golf data'''

    def __init__(self, t=None, data=None):
        if t:
            self.t = t 
        else:
            self.t = Tournament.objects.get(current=True)
        
        if data:
            self.all_data = data 
        else:
            headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
            url =  "https://site.web.api.espn.com/apis/site/v2/sports/golf/leaderboard?league=pga"
            self.all_data = get(url, headers=headers).json()

        for event in self.all_data.get('events'):
            if event.get('id') == self.t.espn_t_num:
                self.event_data = event 
        #print (self.event_data)
        
        for f in self.event_data.get('competitions'):
            if f.get('id') == self.t.espn_t_num:
                self.field_data = f.get('competitors')
        

            
    def started(self):
        print (self.event_data.get('status').get('type').get('state'))
        #  Try to change this is a positive check
        if self.event_data.get('status').get('type').get('state') != 'pre':
            return True
            
        return False


    def player_started(self, espn_num):
        player = [x for x in self.field_data if x.get('id') == espn_num]
        if len(player) > 1:
            raise Exception('player lookup retured more than 1')
        return player[0].get('status').get('type').get('name')


    def field(self):
        return self.field_data


    def picked_golfers(self):
        golfers = list(Picks.objects.filter(playerName__tournament=self.t).values_list('playerName__golfer__espn_number', flat=True))
        
        return [x for x in self.field_data if x.get('id') in golfers]

    
