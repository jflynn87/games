from datetime import datetime, timedelta

from requests import get
import json

from golf_app import utils
from golf_app.models import Tournament, ScoreDict, Group, Field


class ESPNData(object):
    '''takes an optinal dict and provides funcitons to retrieve espn golf data,
        all_data is a list of dicts
        event_data is the data for the event but most is in competition
        competition_data varoius datat about  the tournament
        field_data is the actual golfers in the tournament'''

    def __init__(self, t=None, data=None, force_refresh=None):
        if t:
            self.t = t 
        else:
            self.t = Tournament.objects.get(current=True)
        

        if data:
            self.all_data = data 
        elif self.t.complete and not force_refresh:
            sd = ScoreDict.objects.get(tournament=self.t)
            self.all_data = sd.espn_api_data
        else:
            headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
            #print (espn_t_num)
            #if espn_t_num:
            #    url = 'http://sports.core.api.espn.com/v2/sports/golf/leagues/pga/events/' + espn_t_num 
            #else:
            url =  "https://site.web.api.espn.com/apis/site/v2/sports/golf/leaderboard?league=pga"
               
            
            self.all_data = get(url, headers=headers).json()

            #f = open('espn_api.json', "w")
            #f.write(json.dumps(self.all_data))
            #f.close()

            #print (self.all_data)

        self.event_data = {}
        self.field_data = {}
        event_found = False
        for event in self.all_data.get('events'):
            if event.get('id') == self.t.espn_t_num:
                event_found = True
                if utils.check_t_names(event.get('name'), self.t) or self.t.ignore_name_mismatch: 
                    self.event_data = event
                    sd, created = ScoreDict.objects.get_or_create(tournament=self.t)
                    sd.espn_api_data = self.all_data
                    sd.save()
                    if self.t.pga_tournament_num not in ['468', '999', '470']:
                       for c in self.event_data.get('competitions'):
                            self.competition_data = c
                            self.field_data = c.get('competitors')
                else:
                    print ('tournament mismatch: espn name: ', event.get('name'), 'DB name: ', self.t.name)
                break 
        
        if not event_found:
            print ('ESPN API didnt find event, PGA T num: ', self.t.pga_tournament_num)

        print ('espn API Init complete, field len: ', len(self.field_data))



    def get_round(self):
        
        return self.competition_data.get('status').get('period')

    def get_round_status(self):
        return self.competition_data.get('status').get('type').get('state')


    def started(self):
        if self.event_data.get('status').get('type').get('state') != 'pre':
           return True
            
        return False

    def tournament_complete(self):
        #print (self.event_data.get('status'))
        return self.event_data.get('status').get('type').get('completed')

    def playoff(self):
        #print ('playoff :', self.event_data.get('playoffType'))
        if self.event_data.get('playoffType').get('id') == -1:
            return False
        else:
            return True

    def player_started(self, espn_num):
        if self.t.complete:  #required as api data may not exist between tournaments
            return True
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
        try:
            if espn_num:
                return [x for x in self.field_data if x.get('id') == espn_num][0]
            else:
                return None
        except Exception as e:
            print ('espnApi golfer_data issue, espn_num: ', espn_num, e)
            return None

        ## fix this to have more options, all or other extracts?
        #golfers = list(Picks.objects.filter(playerName__tournament=self.t).values_list('playerName__golfer__espn_number', flat=True))
        
        #return [x.get('athlete').get('displayName') for x in self.field_data if x.get('id') in golfers]

    
    def get_all_data(self):
        return self.all_data

    def cut_num(self):
        '''gives cut num wihtout group penalty.  returns an int and need to add group penalty seperately'''
        if not self.started():
            return self.t.saved_cut_num
        
        if self.event_data.get('tournament').get('cutRound') == 0:
            print ('no cut')
            return len([x for x in self.field_data if x.get('status').get('type').get('id') != '3']) +1
        
        if self.event_data.get('tournament').get('cutCount') != 0:
            return self.event_data.get('tournament').get('cutCount') + 1
        elif self.t.has_cut and int(self.get_round()) <= int(self.t.saved_cut_round):
            return  min(int(x.get('status').get('position').get('id')) for x in self.field_data \
                     if int(x.get('status').get('position').get('id')) > int(self.t.saved_cut_num)) + 1
        else:
            cuts = [v for v in self.field_data if v.get('status').get('type').get('id') == '3']
            return len(cuts) + 1  

        

    def get_rank(self, espn_number):
        golfer_data = self.golfer_data(espn_number)
        if not golfer_data:
            return "WD"
        if golfer_data.get('status').get('type').get('id') in ['3']:
           return golfer_data.get('status').get('type').get('shortDetail')
        else:
           return golfer_data.get('status').get('position').get('id')

    def group_stats(self):
        '''takes a espn api obj, returns a dict with best in group and group cut counts'''
        d = {}
        
        for g in Group.objects.filter(tournament=self.t):
            golfers = g.get_golfers()
            min_score = min([int(x.get('status').get('position').get('id')) - Field.objects.values('handi').get(tournament=self.t, golfer__espn_number=x.get('id')).get('handi') for x in self.field_data if x.get('id') in golfers])
            #print (g, golfers, min_score)
            best = [x.get('athlete').get('id') for x in self.field_data if x.get('id') in golfers and int(x.get('status').get('position').get('id')) - Field.objects.values('handi').get(tournament=self.t, golfer__espn_number=x.get('id')).get('handi') == min_score]
            cuts = len([x.get('athlete').get('id') for x in self.field_data if x.get('id') in golfers and x.get('status').get('type').get('id') == '3'])
            #print (g.number, best)
            
            golfer_list = []
            golfer_espn_num_list = []
            
            for b in best:
                golfer_list.append(self.golfer_data(b).get('athlete').get('displayName'))
                golfer_espn_num_list.append(b)
                 
            d[str(g.number)] = {'golfers': golfer_list,
                                    'golfer_espn_nums': golfer_espn_num_list,
                                    'cuts': cuts,
                                    'total_golfers': g.playerCnt
                 }

            g.cutCount = cuts
            g.save()

        return d
           
    def cut_penalty(self, p):
        '''takes a pick obj and a score obj, returns an int'''
        if not p.playerName.group.cut_penalty():
            return 0

        #golfers = Field.objects.filter(group=p.playerName.group).values_list('golfer__espn_number', flat=True)
        #golfers = p.playerName.group.get_golfers()
        #cuts = len([x for x in self.field_data if x.get('id') in golfers and x.get('status').get('type').get('id') == '3'])
        cuts = p.playerName.group.cut_count(espn_api_data=self.field_data)
        if cuts == 0:
            return 0
        else:
            return p.playerName.group.playerCnt - cuts

        
    def get_movement(self, golfer_data):
        return golfer_data.get('movement')

    def get_player_hole():
        pass

    def pre_cut_wd(self):
        return len([x.get('athlete').get('id') for x in self.field_data if x.get('status').get('type').get('id') == '3' and \
             int(x.get('status').get('period')) <= self.t.saved_cut_round]) 
    
    def post_cut_wd(self):
        l = self.t.not_playing_list()
        l.remove('CUT')
        return len([x.get('athlete').get('id') for x in self.field_data if x.get('status').get('type').get('id') == '3' \
                and x.get('status').get('type').get('shortDetail') in l and int(x.get('status').get('period')) > self.t.saved_cut_round]) 

    def first_tee_time(self):
        #if self.get_round() in [1, 0]:
        try:  #for pre-start and before round 1 completes
            times = [datetime.strptime(x.get('linescores')[0].get('teeTime')[:-1], '%Y-%m-%dT%H:%M') for x in self.field() if x.get('status').get('period') == 1]
            print ('times len: ', len(times))
            return min(times)
        except Exception as e:  # after round 1 completes
            print ('first tee time exception logic')
            times = [[datetime.strptime(t.get('teeTime')[:-1], '%Y-%m-%dT%H:%M') for t in x.get('linescores') if t.get('period') == 1][0] for x in self.field()]
            print ('times len: ', len(times))
            
            return min(times)


    def winner(self):
        '''takes an espn api and returns a list'''
        #return [x.get('id') for x in self.field_data if x.get('status').get('position').get('id') == '1']
        return [x.get('id') for x in self.field_data if self.get_rank(x.get('id')) == '1']  #change the rest if this works

    def second_place(self):
        '''takes an espn api and returns a list'''
        return [x.get('id') for x in self.field_data if x.get('status').get('position').get('id') == '2']

    def third_place(self):
        '''takes an espn api and returns a list'''
        return [x.get('id') for x in self.field_data if x.get('status').get('position').get('id') == '3']

    def get_leaderboard(self):
        d = {}
        #print (self.golfer_data('9780'))
        for data in self.field_data:
            golfer_data = self.golfer_data(data.get('id'))
            d[golfer_data.get('sortOrder')] = {
                                    'rank': self.get_rank(data.get('id')),
                                    'r1': self.get_round_score(data.get('id'), 1),
                                    'r2': self.get_round_score(data.get('id'), 2),
                                    'r3': self.get_round_score(data.get('id'), 3),
                                    'r4': self.get_round_score(data.get('id'), 4),
                                    'total_score': golfer_data.get('score').get('displayValue'),
                                    'change': golfer_data.get('movement'),
                                    'thru': golfer_data.get('status').get('type').get('shortDetail'),
                                    'curr_round_score': '',
                                    'golfer_name': golfer_data.get('athlete').get('displayName'),
                                    'espn_num': data.get('id') 

            }
        
        return d


    def get_round_score(self, espn_num, r):
        return [int(x.get('value')) for x in self.golfer_data(espn_num).get('linescores') if x.get('period') == r][0]