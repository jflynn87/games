from datetime import datetime, timedelta

from requests import get
import json

from golf_app import utils
from golf_app.models import Tournament, ScoreDict, Group, Field, Golfer


class ESPNData(object):
    '''takes an optinal dict and provides funcitons to retrieve espn golf data,
        all_data is a list of dicts
        event_data is the data for the event but most is in competition
        competition_data varoius datat about  the tournament
        field_data is the actual golfers in the tournament'''

    #only use event_data for match play events, other data not reliable.
    def __init__(self, t=None, data=None, force_refresh=False, setup=False, update_sd=True, t_num=None):
        start = datetime.now()

        if t:
            self.t = t 
        else:
            self.t = Tournament.objects.get(current=True)

        if data:
            self.all_data = data 
        elif self.t.complete and not force_refresh:
            sd = ScoreDict.objects.get(tournament=self.t)
            self.all_data = sd.espn_api_data
        elif t_num:
            headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
            url = 'https://site.web.api.espn.com/apis/site/v2/sports/golf/leaderboard?event=' + str(t_num)
            self.all_data = get(url, headers=headers).json()
        else:
            pre_data = datetime.now()
            headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
            url =  "https://site.web.api.espn.com/apis/site/v2/sports/golf/leaderboard?league=pga"
            #url = 'https://site.web.api.espn.com/apis/site/v2/sports/golf/leaderboard?event=401580621'  #match play 2021 for testing
            self.all_data = get(url, headers=headers).json()
            print ('post refresh data dur: ', datetime.now() - pre_data)

        if not setup:
            sd = ScoreDict.objects.get(tournament=self.t)
            self.saved_data = sd.espn_api_data
        else:
            sd = ScoreDict()

        data_start = datetime.now()

        self.event_data = {}
        self.competition_data = {}
        self.field_data = {}

        try:
            if self.t.pga_tournament_num == '999':
                self.event_data = [v for v in self.all_data.get('events') if v.get('id') in ['401580621', '401643692']][0] #  womens event id '401643692'
            else:
                self.event_data = [v for v in self.all_data.get('events') if v.get('id') == self.t.espn_t_num][0]
        except Exception as e:
            print ('ERROR espn api didnt find tournament, trying by espn num: ', self.t.name, self.t.espn_t_num)
            try: 
                url = 'https://site.web.api.espn.com/apis/site/v2/sports/golf/leaderboard?event=' + str(self.t.espn_t_num)
                self.all_data = get(url, headers=headers).json()

                print(url)
                self.event_data = [v for v in self.all_data.get('events') if v.get('id') == self.t.espn_t_num][0]
            except Exception as f:
                print (print ('ERROR espn api didnt find t twice: ', self.t.name, self.t.espn_t_num))
                raise Exception('ESPN API failed to initialize, tournamant number not in events')         
        
        self.competition_data = self.event_data.get('competitions')[0]
        
        if self.t.pga_tournament_num == '470':
            self.field_data = self.competition_data[0].get('competitors')
        else:
            self.field_data = self.competition_data.get('competitors')

        pre_sd = datetime.now()
        
        if len(self.field_data) >0 and update_sd and not data:
            print ('UPDATING SD DATA')
            sd, created = ScoreDict.objects.get_or_create(tournament=self.t)
            sd.espn_api_data = self.all_data
            sd.save()

        #print ('sd save dur: ', datetime.now() - pre_sd)
        #print ('data set up: ', datetime.now() - data_start)
        #print ('espn API Init complete, field len: ', len(self.field_data), ' dur: ', datetime.now() - start)


    def get_t_name(self):  #need to test this to confirm it works
        return self.event_data.get('name')
    
    def get_round(self):
        
        return self.competition_data.get('status').get('period')

    def get_round_status(self):
        #return self.competition_data.get('status').get('type').get('state')
        return self.competition_data.get('status').get('type').get('description')


    def started(self):
        if self.event_data and self.event_data.get('status').get('type').get('state') != 'pre':
           return True
            
        return False

    def tournament_complete(self):
        #print (self.event_data.get('status'))
        if self.t.pga_tournament_num == '470':
            completed = 0

            for c in self.event_data.get('competitions'):
                if c[0].get('description') in ["Third Place", "Championship", "Finals"]:
                    if c[0].get('competitors')[0].get('status').get('type').get('completed'): 
                        completed += 1

            if completed == 2:
                return True
            else:
                return False

        return self.event_data.get('status').get('type').get('completed')

    def playoff(self):
        playoff = [v for v in self.field_data if v.get('status').get('playoff')]
        if len(playoff) > 1:
            return True
        else:
            return False
        

    def player_started(self, espn_num):
        if self.t.complete:  #required as api data may not exist between tournaments
            return True
        if Field.objects.filter(tournament=self.t, golfer__espn_number=espn_num, withdrawn=True).exists():
            return False
        if self.get_round() > 1:
            return True
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

    def started_golfers_list(self):
        return [v.get('id') for v in self.field_data if self.player_started(v.get('id'))]
    
    
    def all_golfers_started(self):
        if not self.t.started():
            return False
        
        if self.get_round() > 1:
            return True
        elif len([v.get('id') for v in self.field_data if v.get('status').get('period') == 1 and v.get('status').get('type').get('name') == "STATUS_SCHEDULED"]) == 0:
            return True
        else:
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
            if self.t.pga_tournament_num == '018':
                return [x for x in self.field_data if str(espn_num) in [str(x.get('roster')[0].get('playerId')), str(x.get('roster')[1].get('playerId'))]][0]
            
            print ('espnApi golfer_data issue, espn_num: ', espn_num, e)
            return None

   
    def get_all_data(self):
        return self.all_data

    def cut_num(self):
        '''gives cut num wihtout group penalty.  returns an int and need to add group penalty seperately'''
        if not self.started():
            return self.t.saved_cut_num

        if self.t.cut_score and self.t.cut_score.isdigit():
            return int(self.t.cut_score) + 1

        #clean this up, added for round 1 based on espn not having a cut round or score.  they have cutRound == 0 
        if self.t.has_cut and int(self.get_round()) <= int(self.t.saved_cut_round) and self.event_data.get('tournament').get('cutRound') == 0:
            #move this to be the cut_line funciton
            try:
                return  min(int(x.get('status').get('position').get('id')) for x in self.field_data \
                     if int(x.get('status').get('position').get('id')) > int(self.t.saved_cut_num))
            except Exception as e1:
                print ('cut e1 : ', e1)
                return self.t.saved_cut_num 

        if self.event_data.get('tournament').get('cutCount') != 0:
            return self.event_data.get('tournament').get('cutCount') + 1
        elif self.t.has_cut and int(self.get_round()) <= int(self.t.saved_cut_round):
            try:
                return  min(int(x.get('status').get('position').get('id')) for x in self.field_data \
                        if int(x.get('status').get('position').get('id')) > int(self.t.saved_cut_num)) 
            except Exception as e:
                #print ('issue wiht cut num, returning saved model num', e)
                return self.t.saved_cut_num
        else:
            #changed to not cut - should only be here for no cut events
            cuts = [v for v in self.field_data if v.get('status').get('type').get('id') != '3']
            return len(cuts) + 1  
        

    def get_rank(self, espn_number):
        golfer_data = self.golfer_data(espn_number)
        
        if not golfer_data:
            return self.cut_num()
        if golfer_data.get('status').get('type').get('id') in ['3']:
           return self.cut_num()
           #return golfer_data.get('status').get('type').get('shortDetail')
        else:
           if golfer_data.get('status').get('position').get('id').isdigit():
               return golfer_data.get('status').get('position').get('id')
           else:
               return self.cut_num()


    def get_rank_display(self, espn_number):
        golfer_data = self.golfer_data(espn_number)
        if not golfer_data:
            return "WD"
        else:
           return golfer_data.get('status').get('position').get('displayName')


    def group_stats(self, groups=None):
        '''takes a espn api obj and queryset of groups, returns a dict with best in group and group cut counts'''
        d = {}

        if not groups:
            groups = Group.objects.filter(tournament=self.t)            
        
        #for g in Group.objects.filter(tournament=self.t):
        for g in groups:
            try:
                #golfers = g.get_golfers()
                golfers = self.made_cut_golfers(g.get_golfers())
                #print ('golfers: ', golfers)
                if self.t.pga_tournament_num == '018':
                    min_score = min([int(x.get('status').get('position').get('id')) for x in self.field_data if str(x.get('roster')[0].get('playerId')) in golfers or str(x.get('roster')[1].get('playerId')) in golfers])
                    best = []
                    best_0 = [x.get('roster')[0].get('playerId') for x in self.field_data if str(x.get('roster')[0].get('playerId')) in golfers and int(x.get('status').get('position').get('id')) == min_score]
                    best_1 = [x.get('roster')[1].get('playerId') for x in self.field_data if str(x.get('roster')[1].get('playerId')) in golfers and int(x.get('status').get('position').get('id')) == min_score]
                    for zero in best_0:
                        best.append(zero)
                    for one in best_1:
                        best.append(one)
                    cuts = self.cut_count(g)
                else:
                    try:
                        min_score = min([int(self.get_rank(x.get('id'))) - Field.objects.values('handi').get(tournament=self.t, golfer__espn_number=x.get('id')).get('handi') for x in self.field_data if x.get('id') in golfers])
                    except Exception as me:
                        print ('min score issue: ', me)
                        min_score = 0 
                    best = [x.get('athlete').get('id') for x in self.field_data if x.get('id') in golfers and int(self.get_rank(x.get('id'))) - Field.objects.values('handi').get(tournament=self.t, golfer__espn_number=x.get('id')).get('handi') == min_score]
                    cuts = len(self.regular_cut_golfers(g.get_golfers()))
                    #cuts = len([x.get('athlete').get('id') for x in self.field_data if x.get('id') in golfers and x.get('status').get('type').get('id') == '3'])
                    ## change cuts to use the function after testing
                golfer_list = []
                golfer_espn_num_list = []
                
                for b in best:
                    if self.t.pga_tournament_num == '018':
                        b_name = [x.get('roster')[0].get('athlete').get('displayName') for x in self.field_data if str(x.get('roster')[0].get('playerId')) == str(b)]
                        if len(b_name) == 0:
                            g_name = [x.get('roster')[1].get('athlete').get('displayName') for x in self.field_data if str(x.get('roster')[1].get('playerId')) == str(b)][0]
                        else:
                            g_name = b_name[0]
                        golfer_list.append(g_name)
                    else:
                        golfer_list.append(self.golfer_data(b).get('athlete').get('displayName'))
                    golfer_espn_num_list.append(str(b))
                    
                d[str(g.number)] = {'golfers': golfer_list,
                                        'golfer_espn_nums': golfer_espn_num_list,
                                        'cuts': cuts,
                                        'total_golfers': g.playerCnt
                            }

                g.cutCount = cuts
                g.save()
            except Exception as e:
                #for x in golfers:
                #    print (self.golfer_data(x))
                #    print (self.get_rank(x), Field.objects.values('handi').get(tournament=self.t, golfer__espn_number=x).get('handi'))
                print ('espn api group stats issue: ', g, e)
                d[str(g.number)] = {'golfers': [],
                                    'golfer_espn_nums': [],
                                    'cuts': 0,
                                    'total_golfers': g.playerCnt
                    }

        return d


    def cut_penalty(self, p):
        '''takes a field obj and a score obj, returns an int'''
        if not p.group.cut_penalty():
            return 0

        #cuts = p.group.cut_count(espn_api_data=self.field_data)
        cuts = p.group.cut_count(espn_api_data=self)
        if cuts == 0:
            return 0
        else:
            return p.group.playerCnt - cuts

        
    def get_movement(self, golfer_data):
        return golfer_data.get('movement')


    #def get_player_hole():
    #    pass


    def pre_cut_wd(self):
        return len([x.get('athlete').get('id') for x in self.field_data if x.get('status').get('type').get('id') == '3' and \
             int(x.get('status').get('period')) <= self.t.saved_cut_round]) 
    
    
    def post_cut_wd(self):
        l = self.t.not_playing_list()
        l.remove('CUT')
        return len([x.get('athlete').get('id') for x in self.field_data if x.get('status').get('type').get('id') == '3' \
                and x.get('status').get('type').get('shortDetail') in l and int(x.get('status').get('period')) > self.t.saved_cut_round]) 

    
    def golfers_post_cut_wd(self, espn_num):
        '''takes a list, returns a list'''
        l = self.t.not_playing_list()
        l.remove('CUT')
        #print ('espn_api golfers post cut wd', len(espn_num))
        return [x.get('athlete').get('id') for x in self.field_data if x.get('status').get('type').get('id') == '3' \
                and x.get('status').get('type').get('shortDetail') in l and int(x.get('status').get('period')) > self.t.saved_cut_round  \
                and x.get('athlete').get('id') in espn_num]


    def regular_cut_golfers(self, espn_num):
        '''takes a list, returns a list'''
                
        return [x.get('athlete').get('id') for x in self.field_data if x.get('status').get('type').get('id') == '3' \
                and x.get('athlete').get('id') in espn_num and x.get('athlete').get('id') not in self.golfers_post_cut_wd(espn_num)] 


    def made_cut_golfers(self, golfers):
        '''takes a list of golfers, returns a list'''
        post_cut_wd = self.golfers_post_cut_wd(golfers)
        regular_made = [x.get('athlete').get('id') for x in self.field_data if x.get('status').get('type').get('id') != '3' \
                and x.get('athlete').get('id') in golfers]

        return post_cut_wd + regular_made

    def post_cut_wd_score(self):
        return len([x for x in self.field_data if x.get('status').get('type').get('id') != '3']) + 1


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
        if self.t.pga_tournament_num == '018':
            for data in self.field_data:
                #golfer_data = self.golfer_data(data.get('roster')[0].get('athlete').get('id'))
                #thru = self.get_thru(data.get('roster')[0].get('athlete').get('id'))
               
                #print (golfer_data)
                #print ('data: ', data.get('status'))
                d[data.get('sortOrder')] = {
                                        'rank': data.get('status').get('position').get('displayName'),
                                        'r1': self.get_round_score(data.get('roster')[0].get('athlete').get('id'), 1),
                                        'r2': self.get_round_score(data.get('roster')[0].get('athlete').get('id'), 2),
                                        'r3': self.get_round_score(data.get('roster')[0].get('athlete').get('id'), 3),
                                        'r4': self.get_round_score(data.get('roster')[0].get('athlete').get('id'), 4),
                                        'total_score': self.to_par(data.get('roster')[0].get('athlete').get('id')),
                                        'change': '-', #golfer_data.get('movement'),
                                        'thru': '-', #thru,
                                        'curr_round_score': '-', #self.current_round_to_par(data.get('id')),
                                        'golfer_name': data.get('team').get('displayName'), #golfer_data.get('athlete').get('displayName'),
                                        'espn_num': '' #data.get('id') 
                    
                }            
        elif self.t.pga_tournament_num == '999':
            for i, data in enumerate(self.field_data):
                #print ('LB DATA: ', data.get('id'), self.get_thru(data.get('id')))
                golfer_data = self.golfer_data(data.get('id'))
                thru = self.get_thru(data.get('id'))
                if i <= 59: 
                    sort_order = golfer_data.get('sortOrder')
                else:
                    sort_order = 60 + golfer_data.get('sortOrder')
                d[sort_order] = {
                                        #'rank': self.get_rank(data.get('id')),
                                        'rank': self.get_rank_display(data.get('id')),
                                        'r1': self.get_round_score(data.get('id'), 1),
                                        'r2': self.get_round_score(data.get('id'), 2),
                                        'r3': self.get_round_score(data.get('id'), 3),
                                        'r4': self.get_round_score(data.get('id'), 4),
                                        #'total_score': golfer_data.get('score').get('displayValue'),
                                        'total_score': self.to_par(data.get('id')),
                                        'change': golfer_data.get('movement'),
                                        #'thru': golfer_data.get('status').get('type').get('shortDetail'),
                                        'thru': thru,
                                        'curr_round_score': self.current_round_to_par(data.get('id')),
                                        'golfer_name': golfer_data.get('athlete').get('displayName'),
                                        'espn_num': data.get('id') 

                }
        else:
            for data in self.field_data:
                #print ('LB DATA: ', data.get('id'), self.get_thru(data.get('id')))
                golfer_data = self.golfer_data(data.get('id'))
                thru = self.get_thru(data.get('id'))
                d[golfer_data.get('sortOrder')] = {
                                        #'rank': self.get_rank(data.get('id')),
                                        'rank': self.get_rank_display(data.get('id')),
                                        'r1': self.get_round_score(data.get('id'), 1),
                                        'r2': self.get_round_score(data.get('id'), 2),
                                        'r3': self.get_round_score(data.get('id'), 3),
                                        'r4': self.get_round_score(data.get('id'), 4),
                                        #'total_score': golfer_data.get('score').get('displayValue'),
                                        'total_score': self.to_par(data.get('id')),
                                        'change': golfer_data.get('movement'),
                                        #'thru': golfer_data.get('status').get('type').get('shortDetail'),
                                        'thru': thru,
                                        'curr_round_score': self.current_round_to_par(data.get('id')),
                                        'golfer_name': golfer_data.get('athlete').get('displayName'),
                                        'espn_num': data.get('id') 

                }
        #print ('leaderboard: ', d)
        return d


    def get_thru(self, espn_num):
        golfer_data = self.golfer_data(espn_num)
        if golfer_data:
            if str(golfer_data.get('status').get('type').get('id')) == '1':
                thru = golfer_data.get('status').get('displayThru')
            elif str(golfer_data.get('status').get('type').get('id')) == '0':
                thru = golfer_data.get('status').get('teeTime')
            else:
                thru = golfer_data.get('status').get('type').get('shortDetail')
        else:
            thru = "WD"
        return thru

    def to_par(self, espn_num):
        return self.golfer_data(espn_num).get('statistics')[0].get('displayValue')

    def get_round_score(self, espn_num, r):
        try:
            return [int(x.get('value')) for x in self.golfer_data(espn_num).get('linescores') if x.get('period') == r][0]
        except Exception as e:
            return '--'

    def leaders(self):
        try:
            print ('LEADERS ', [v.get('athlete').get('displayName') for v in self.field_data if self.get_rank(v.get('id')) == '1'])
            return [v.get('athlete').get('displayName') for v in self.field_data if self.get_rank(v.get('id')) == '1']
        except Exception as e:
            print ('espn api leaders exception: ', e)
            if self.t.pga_tournament_num == '018':
                return [v.get('team').get('displayName') for v in self.field_data if self.get_rank(v.get('id')) == '1']
            return ['No leaders available']

    def leader_score(self):
        try:
            return [self.to_par(v.get('id')) for v in self.field_data if self.get_rank(v.get('id')) == '1'][0]
            #return [v.get('score').get('displayValue') for v in self.field_data if self.get_rank(v.get('id')) == '1'][0]
        except Exception as e:
            print ('espn api leader score exception: ', e)
            return ''

    def post_cut(self):
        if not self.t.has_cut:
            return False
        
        if self.event_data.get('tournament').get('cutRound') == 0:
            return False

        if len([x.get('athlete').get('id') for x in self.field_data if x.get('status').get('type').get('id') == '3' \
                and x.get('status').get('type').get('shortDetail') == "CUT"]) > 0:
                return True

        return False

    def cut_line(self):
        cut_info = {'line_type': '',
                    'cut_score': 'No Cut Line'}

        if self.event_data.get('tournament').get('cutRound') and int(self.event_data.get('tournament').get('cutRound')) < int(self.get_round()):
            cut_info.update({'line_type': 'Actual',
                            'cut_score': self.event_data.get('tournament').get('cutScore')})

        elif self.event_data.get('tournament').get('cutRound') and int(self.event_data.get('tournament').get('cutRound')) == int(self.get_round()) \
            and self.competition_data.get('status').get('type').get('state') == "post":
            cut_info.update({'line_type': 'Actual',
                            'cut_score': self.event_data.get('tournament').get('cutScore')})

        elif self.t.has_cut and int(self.get_round()) <= int(self.t.saved_cut_round): #and self.event_data.get('tournament').get('cutRound') == 0:
            max_rank = max(int(x.get('status').get('position').get('id')) for x in self.field_data \
                     if int(x.get('status').get('position').get('id')) <= int(self.t.saved_cut_num)) 
            #cut_score = [x.get('score').get('displayValue') for x in self.field_data if self.get_rank(x.get('id')) == str(max_rank)][0]
            cut_score = [self.golfer_data(x.get('id')).get('statistics')[0].get('displayValue') for x in self.field_data if str(self.get_rank(x.get('id'))) == str(max_rank)][0]
            cut_info.update({'line_type': 'Projected', 'cut_score': cut_score})
            #print ('cut stuff: ', max_rank, cut_score)
            #print ([(self.golfer_data(x.get('id')).get('status').get('position').get('id'), x.get('score').get('displayValue'), self.golfer_data(x.get('id')).get('statistics')[0].get('displayValue')) for x in self.field_data if str(self.get_rank(x.get('id'))) == str(max_rank)])
        return cut_info

    def needs_update(self):
        #sd = ScoreDict.objects.get(tournament=self.t)
        saved_data = ESPNData(t=self.t, data=self.saved_data)

        c_data = self.event_data.get('competitions')[0].get('competitors')
        saved_c = saved_data.event_data.get('competitions')[0].get('competitors')

        if saved_data.event_data == self.event_data:
            print ('NO UPDATE required')
            return False
        
        if c_data == saved_c:
            print ("Competition data same but other diffs skipping calculating scores")
            return False

        return True

    def current_round_to_par(self, espn_num):
        data = self.golfer_data(espn_num)
        curr_round = self.get_round()
        try:
            return [x.get('displayValue') for x in self.golfer_data(espn_num).get('linescores') if x.get('period') == curr_round][0]
        except Exception as e:
            return '-'

    ## match play functions ##

    def mp_golfers_per_round(self):
        d = {}
        for matches in self.event_data.get('competitions'):
            for match in matches:
                if not d.get(match.get('description')):
                    d[match.get('description')] = []
                for golfer in match.get('competitors'):
                    d.get(match.get('description')).append(golfer.get('athlete').get('id'))
                    #if match.get('description') == 'Third Place':
                    #    print ('thrird: ', golfer.get('score').get('winner'))
                    if match.get('description') == 'Third Place' and golfer.get('score').get('winner'):
                        d['third'] = golfer.get('athlete').get('id')
                    elif match.get('description') == 'Third Place' and not golfer.get('score').get('winner'):
                        d['fourth'] = golfer.get('athlete').get('id')
                    #elif match.get('description') == 'Championship' and golfer.get('score').get('winner'):
                    elif match.get('description') == 'Finals' and golfer.get('score').get('winner'):
                        d['first'] = golfer.get('athlete').get('id')
                    #elif match.get('description') == 'Championship' and golfer.get('score').get('winner') == False:
                    elif match.get('description') == 'Finals' and golfer.get('score').get('winner') == False:
                        d['second'] = golfer.get('athlete').get('id')

        return d

    def get_mp_records(self):
        c  = self.event_data.get('competitions')
        d = {'Wednesday Group Play': {'winners': [], 'losers': [], 'draws': []},
            'Thursday Group Play': {'winners': [], 'losers': [], 'draws': []},
            'Friday Group Play': {'winners': [], 'losers': [], 'draws': []},
            }

        for s in c:
            for m in s:
                if d.get(m.get('description')):
                    if m.get('competitors')[0].get('status').get('type').get('id') == '2' and m.get('competitors')[0].get('score').get('draw'):
                        d.get(m.get('description')).get('draws').append(m.get('competitors')[0].get('athlete').get('id'))
                        d.get(m.get('description')).get('draws').append(m.get('competitors')[1].get('athlete').get('id'))
                    elif m.get('competitors')[0].get('score').get('winner'):
                        d.get(m.get('description')).get('winners').append(m.get('competitors')[0].get('athlete').get('id'))
                        d.get(m.get('description')).get('losers').append(m.get('competitors')[1].get('athlete').get('id'))
                    elif m.get('competitors')[1].get('score').get('winner'):
                        d.get(m.get('description')).get('winners').append(m.get('competitors')[1].get('athlete').get('id'))
                        d.get(m.get('description')).get('losers').append(m.get('competitors')[0].get('athlete').get('id'))
        return d

    def mp_golfer_results(self, golfer, records=None):
        '''takes a golfer object returns a list'''
        if not records:
            records = self.get_mp_records()
        wins = len([v.get('winners') for k,v in records.items() if golfer.espn_number in v.get('winners')])
        loss = len([v.get('losers') for k,v in records.items() if golfer.espn_number in v.get('losers')])
        draw = len([v.get('draws') for k,v in records.items() if golfer.espn_number in v.get('draws')])

        return [wins, loss, draw]


    def mp_group_rank(self, golfer, records=None):
        '''takes a field object'''
        if not records:
            records = self.get_mp_records()
        d = {}
        for f in Field.objects.filter(group=golfer.group):
            rec = self.mp_golfer_results(f.golfer, records)
            ranking = rec[0] + (rec[2] * .5) - rec[1]
            d[f.pk] = ranking

        r = {key: rank for rank, key in enumerate(sorted(set(d.values()), reverse=True), 1)}
        ranked_d = {k: r[v] for k,v in d.items()}

        return ranked_d

    def cut_count(self, group=None):
        '''gets cut golfers for a group'''
        golfers = group.get_golfers()

        if self.t.pga_tournament_num == '018':
            return len([x for x in self.field_data if (str(x.get('roster')[0].get('playerId')) in golfers or str(x.get('roster')[1].get('playerId')) in golfers) and x.get('status').get('type').get('id') == '3'])
        else:
            return len([x for x in self.field_data if x.get('id') in golfers and x.get('status').get('type').get('id') == '3'])

    def total_making_cut(self):
        return len([x for x in self.field_data if  x.get('status').get('type').get('id') != '3']) - self.post_cut_wd()
    
    def hole_by_hole(self, espn_num):
        r = self.get_round()

        print (self.golfer_data(espn_num))
        return 
    
    def zurich_golfer_rank(self, golfer):
        '''takes a golfer object returns a string'''
        pass

    def purse(self):
        return self.event_data.get('purse')
    
    def olympic_gold_winner(self):
        print ('GOLD BD ', self.tournament_complete(), self.event_data.get('name'))
        if self.tournament_complete():
            return [x.get('athlete').get('id') for x in self.field_data if x.get('status').get('position').get('id') == '1'][0]
        return False
    
    def olympic_silver_winner(self):
        if self.tournament_complete():
            return [x.get('athlete').get('id') for x in self.field_data if x.get('status').get('position').get('id') == '2'][0]
        return False
    
    def olympic_bronze_winner(self):
        if self.tournament_complete():
            return [x.get('athlete').get('id') for x in self.field_data if x.get('status').get('position').get('id') == '3'][0]
        return False