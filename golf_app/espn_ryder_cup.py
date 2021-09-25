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
            #print (self.all_data)
         
        
            
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
        for c in self.all_data.get('events')[0].get('competitions'):
            
            if len(c) == 1:
                field['overall'] = {}                
                for competitor in c[0].get('competitors'):
                    field.get('overall').update({competitor.get('team').get('abbreviation'): {'score': competitor.get('score'),
                                                                                            'flag': competitor.get('team').get('logos')[0].get('href')}})
                    
            else:
                for m in c:
                    #field[m.get('description')] = {}
                    #print (m)
                    session = m.get('description')
                    match_id = m.get('id')
                    if field.get(session):
                        field.get(session).update({match_id: {'status': m.get('status').get('type').get('id')}})    
                    else:
                        field[session] = {match_id: {'status': m.get('status').get('type').get('id')}}    

                    for competitors in m.get('competitors'):
                        score = competitors.get('score')
                        for golfer in competitors.get('roster'):
                            golfer_name = golfer.get('athlete').get('displayName')
                            espn_num = golfer.get('athlete').get('id')
                            field.get(session).get(match_id).update({espn_num: {'golfer': golfer_name, 
                                            'score': score}})
                            
                            #print (field)
        return field
                        
                    
                                    
                        

                        #    for k,v in golfer.items():
                        #        print (k,v)



            
            #if c.get('type').get('id') == '1':




