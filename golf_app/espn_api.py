from datetime import datetime, timedelta
from requests import get
import json
from golf_app import utils
from golf_app.models import Tournament, Field, Golfer, ScoreDict, Picks


class ESPNData(object):
    '''takes an optinal dict and provides funcitons to retrieve espn golf data,
        all_data is a list of dicts
        event_data is the data for the event but most is in competition
        competition_data varoius datat about  the tournament
        field_data is the actual golfers in the tournament'''

    def __init__(self, t=None, data=None, mode='none', espn_t_num=None):
        if t:
            self.t = t 
        else:
            self.t = Tournament.objects.get(current=True)
        
        if data:
            self.all_data = data 
        else:
            headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
            #print (espn_t_num)
            #if espn_t_num:
            #    url = 'http://sports.core.api.espn.com/v2/sports/golf/leagues/pga/events/' + espn_t_num 
            #else:
            url =  "https://site.web.api.espn.com/apis/site/v2/sports/golf/leaderboard?league=pga"
               
            
            self.all_data = get(url, headers=headers).json()
            if self.t.pga_tournament_num != '999' and self.all_data.get('name') != self.t.name and not self.t.ignore_name_mismatch:
                match = utils.check_t_names(self.t.name, self.t)
                if not match:
                    print ('tournament mismatch: espn name: ', t.name, 'DB name: ', self.t.name)
                    return {}

            #f = open('espn_api.json', "w")
            #f.write(json.dumps(self.all_data))
            #f.close()

            #print (self.all_data)

        for event in self.all_data.get('events'):
            if event.get('id') == self.t.espn_t_num or mode == 'setup':
                self.event_data = event 
        
        if self.t.pga_tournament_num == '468':
            self.field_data = {}
        else:
            for c in self.event_data.get('competitions'):
                
                if c.get('id') == self.t.espn_t_num or mode == 'setup': 
                    self.competition_data = c
                    self.field_data = c.get('competitors')


    def get_round(self):
        
        return self.competition_data.get('status').get('period')

    def get_round_status(self):
        return self.competition_data.get('status').get('type').get('state')


    def started(self):
        #  Try to change this is a positive check
        if self.event_data.get('status').get('type').get('state') != 'pre':
            return True
            
        return False


    def player_started(self, espn_num):
        if Field.objects.filter(tournament=self.t, golfer__espn_number=espn_num, withdrawn=True).exists():
            return False
        player = [x for x in self.field_data if x.get('id') == espn_num]


        if len(player) == 0:
            return False

        if player[0].get('status').get('period') > 1:
            return True
        elif player[0].get('status').get('period') == 1 and \
            player[0].get('status').get('type').get('name') == "STATUS_SCHEDULED":
            return False
        elif player[0].get('status').get('period') == 1 and \
            player[0].get('status').get('type').get('name') in ["STATUS_IN_PROGRESS", "STATUS_PLAY_COMPLETE", "STATUS_CUT", "STATUS_FINISH"]:
            return True
        print ('cant tell if started, return False: ', espn_num, player[0].get('status'))
        return False


    def field(self):
        return self.field_data


    def golfer_data(self, espn_num=None):
        if espn_num:
            #print (espn_num, [x for x in self.field_data if x.get('id') == espn_num])
            return [x for x in self.field_data if x.get('id') == espn_num][0]
        else:
            return None

        ## fix this to have more options, all or other extracts?
        #golfers = list(Picks.objects.filter(playerName__tournament=self.t).values_list('playerName__golfer__espn_number', flat=True))
        
        #return [x.get('athlete').get('displayName') for x in self.field_data if x.get('id') in golfers]

    
    def get_all_data(self):
        return self.all_data

    def cut_num(self):
        if self.event_data.get('tournament').get('cutRound') == 0:
            print ('no cut')
            return len([x for x in self.field_data if x.get('status').get('type').get('id') != '3'])
        if self.event_data.get('tournament').get('cutCount'):
            return self.event_data.get('tournament').get('cutCount')
        else:
            cuts = [v for v in self.field_data if v.get('status').get('type').get('id') == '3']
            return len(cuts)

        #need to make this work pre-cut

    def get_rank(self, golfer_data):
        if golfer_data.get('status').get('type').get('id') in ['3']:
           return golfer_data.get('status').get('type').get('shortDetail')
        else:
           return golfer_data.get('status').get('position').get('id')
           
        
    def get_movement(self, golfer_data):
        return golfer_data.get('movement')

    def get_player_hole():
        pass