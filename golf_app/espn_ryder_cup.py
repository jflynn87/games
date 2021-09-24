from datetime import datetime, timedelta
#import pytz
#import urllib
from requests import get
import json
#from bs4 import BeautifulSoup
from golf_app import utils
from golf_app.models import Tournament, Field, Golfer, ScoreDict, Picks
import urllib
from bs4 import BeautifulSoup


class ESPNData(object):
    '''takes an optinal dict and provides funcitons to retrieve espn golf data'''

    def __init__(self, t=None, data=None, mode='none', espn_t_num=None):
        if t:
            self.t = t 
        else:
            self.t = Tournament.objects.get(current=True)
        
        if data:
            self.all_data = data 
        else:
            headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
            print (espn_t_num)
            if espn_t_num:
                url = 'http://sports.core.api.espn.com/v2/sports/golf/leagues/pga/events/' + espn_t_num 
            else:
                url =  "https://site.web.api.espn.com/apis/site/v2/sports/golf/leaderboard?league=pga"
               
            
            self.all_data = get(url, headers=headers).json()
         
        
            
    def started(self):
        pass        
        #if self.event_data.get('status').get('type').get('state') != 'pre':
        #    return True
            
        #return False


    def player_started(self, espn_num):
        pass
        # if Field.objects.filter(tournament=self.t, golfer__espn_number=espn_num, withdrawn=True).exists():
        #     return False
        # player = [x for x in self.field_data if x.get('id') == espn_num]

        # if len(player) == 0:
        #     return False

        # if player[0].get('status').get('period') > 1:
        #     return True
        # elif player[0].get('status').get('period') == 1 and \
        #     player[0].get('status').get('type').get('name') == "STATUS_SCHEDULED":
        #     return False
        # elif player[0].get('status').get('period') == 1 and \
        #     player[0].get('status').get('type').get('name') in ["STATUS_IN_PROGRESS", "STATUS_PLAY_COMPLETE", "STATUS_CUT"]:
        #     return True
        # print ('cant tell if started, return False: ', espn_num, player)
        # return False


    def field(self):

        field = {}
        for c in self.all_data.get('competitions'):
            #print (c)
            if c.get('type').get('id') == '1':
                field['overall'] = {}
                for team in c.get('competitors'):
                    if team.get('homeAway') == 'home':
                        field['overall'].update({'USA': {'score_link': team.get('score').get('$ref')}})
                    elif team.get('homeAway') == 'away':
                        field['overall'].update({'EURO': {'score_link': team.get('score').get('$ref')}})
            elif c.get('type').get('id') != '3':
                match = c.get('id')
                field[match] = {'type': c.get('type').get('text')}
                for team in c.get('competitors'):
                    if team.get('homeAway') == 'away':
                        team_name = 'EURO'
                        golfers_link = team.get('roster').get('$ref')
                        score_link = team.get('score').get('$ref')
                    elif team.get('homeAway') == 'home':
                        team_name = 'USA'
                        golfers_link = team.get('roster').get('$ref')
                        score_link = team.get('score').get('$ref')

                    field[match].update({team_name: { 
                                            'score_link': score_link, 
                                            'golfers_link': golfers_link}})
            elif c.get('type').get('id') == '3':
                match = c.get('id')
                field[match] = {'type': c.get('type').get('text')}

                for team in c.get('competitors'):
                    if team.get('homeAway') == 'away':
                        team_name = 'EURO'
                        golfers_link = team.get('athlete').get('$ref')
                        score_link = team.get('score').get('$ref')
                    elif team.get('homeAway') == 'home':
                        team_name = 'USA'
                        golfers_link = team.get('athlete').get('$ref')
                        score_link = team.get('score').get('$ref')

                    field[match].update({team_name: { 
                                         'score_link': score_link,
                                         'golfers_link': golfers_link}})

        return field

    def score_dict(self):
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
        score_dict = {}
        for match, info in self.field().items():
            score_dict[match] = {}
            if match != 'overall':
                if info.get('type') != 'singles':
                    for t in ['USA', 'EURO']:
                        url =  info.get(t).get('golfers_link')
                        golfers = get(url, headers=headers).json()
                        for entry in golfers.get('entries'):
                            golfer_obj = Golfer.objects.get(espn_number=entry.get('playerId'))
                            score_url = info.get(t).get('score_link')
                            score_data = get(score_url, headers=headers).json()
                            #print (t, info.get('type'), golfer_obj, score_data.get('winner'), score_data.get('value'), score_data.get('holesRemaining'), score_data.get('displayValue'), score_data.get('draw'))
                            score_dict[match].update({t: {'type': info.get('type'),
                                                        'golfer_pk': golfer_obj.pk, 
                                                        'winner': score_data.get('winner'),
                                                        'value': score_data.get('value'),
                                                        'holes_remaining': score_data.get('holesRemaining'),
                                                        'display_value': score_data.get('displayValue'),
                                                        'draw': score_data.get('draw')
                                                        }})
                elif info.get('type') == 'singles':
                    for t in ['USA', 'EURO']:
                        url =  info.get(t).get('golfers_link')
                        golfer = get(url, headers=headers).json()
                        #print (golfer)
                        golfer_obj = Golfer.objects.get(espn_number=golfer.get('id'))
                        score_url = info.get(t).get('score_link')
                        score_data = get(score_url, headers=headers).json()
                        #print (t, info.get('type'), golfer_obj, score_data.get('winner'), score_data.get('value'), score_data.get('holesRemaining'), score_data.get('displayValue'), score_data.get('draw'))
                        score_dict[match].update({t: {'type': info.get('type'),
                                    'golfer_pk': golfer_obj.pk, 
                                    'winner': score_data.get('winner'),
                                    'value': score_data.get('value'),
                                    'holes_remaining': score_data.get('holesRemaining'),
                                    'display_value': score_data.get('displayValue'),
                                    'draw': score_data.get('draw')
                                    }})

            
        return score_dict





