from datetime import datetime, timedelta
import requests 
import pytz
#import json



class ESPNData(object):
    '''takes an optinal dict and provides funcitons to retrieve espn FB data'''

    def __init__(self, week=None, payload=None, nfl_season_type=None):
        from fb_app.models import Week
        if week:
            self.week = week
        else:
            week = Week.objects.get(current=True)

        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
        url = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
        #payload = {'week':'1'}

        if not nfl_season_type:
            nfl_seaon_type = 'REG'

        if not payload:
            payload = {}
        else:
            payload = {'week': str(payload)}

        #payload = {}  #works for pre season/current week?
        self.data = requests.get(url, headers=headers, params=payload).json() 



    def get_orig_data(self):
        return self.data

    def get_data(self):
        from fb_app.models import Teams
        d = {}
        for l in self.data.get('events'):
            #print (l.get('name'))
            for competition in l.get('competitions'):
                winner = False
                for c in competition.get('competitors'):
                    #print (c.get('homeAway'), c.get('team').get('name'))
                    game_date = competition.get('date')

                    if c.get('team').get('name'):
                        t_name = c.get('team').get('name')

                    elif c.get('team').get('displayName') == "Washington":
                        t_name = "Commanders"  #do i need this?
                        t_abbr = c.get('team').get('abbreviation')
                    else:
                        raise Exception('uknown team: ', c.get('team'))                        
                        
                    if c.get('homeAway') == 'home':
                        #home = Teams.objects.get(long_name=t_name)
                        if c.get('team').get('abbreviation') == "WSH":
                            home_abbr = "WAS"
                        else:
                            home_abbr = c.get('team').get('abbreviation')
                        home_score = c.get('score')
                        if c.get('winner'): 
                            winner = home_abbr

                    elif c.get('homeAway') == "away":
                        #away = Teams.objects.get(long_name=t_name)
                        if c.get('team').get('abbreviation') == "WSH":
                            away_abbr = "WAS"
                        else:
                            away_abbr = c.get('team').get('abbreviation')
                        away_score = c.get('score')
        
                        if c.get('winner'): 
                            winner = away_abbr
                    

                    else:
                        raise Exception('uknown value in home/away: ', c.get('homeAway'))

                        
                d[competition.get('id')] = {'home': home_abbr, 
                                  'away': away_abbr,
                                  'game_time': competition.get('date'),
                                  'home_score': home_score, 
                                  'away_score': away_score,
                                  #'qtr': competition.get('status').get('type').get('description')}
                                  'qtr': competition.get('status').get('type').get('shortDetail'),
                                  'winner': winner,
                                  'game_date': game_date}
        return d


    def started(self, game_id):
        '''takes an espn game id and returns a bool'''
        state = [x.get('status').get('type').get('id') for x in [game for game in self.data.get('events')] if str(x.get('id')) == str(game_id)]
        #print (state)
        if state[0] == '1':
            return False
        else:
            return True


    def game_date_utc(self, game_id):
        return [x.get('date') for x in [game for game in self.data.get('events')] if str(x.get('id')) == str(game_id)][0]


    def game_date_est(self, game_id):
        est = pytz.timezone('US/Eastern')
        utc = pytz.utc
        d_utc = utc.localize(datetime.strptime(self.game_date_utc(game_id)[:-1], '%Y-%m-%dT%H:%M'))
        d_est = d_utc.astimezone(est)

        return d_est


    def game_dow(self, game_id):
        return self.game_date_est(game_id).strftime('%A')


    def first_game_of_week(self):
        '''returns a list as there may be multiple games starting at the same time'''
        est = pytz.timezone('US/Eastern')
        utc = pytz.utc
        d = utc.localize(min([datetime.strptime(x.get('date')[:-1], '%Y-%m-%dT%H:%M') for x in [game for game in self.data.get('events')]]))

        return ([x.get('id') for x in [game for game in self.data.get('events') if datetime.strptime(game.get('date')[:-1],'%Y-%m-%dT%H:%M').astimezone(est).date()  == d.astimezone(est).date()]]) 


    def regular_week(self):
        if len(self.first_game_of_week()) == 1 and \
            self.game_dow(self.first_game_of_week()[0]) == 'Thursday':
            return True
        
        return False


    def game_data(self, game_id):
        return [game for game in self.data.get('events') if str(game.get('id')) == str(game_id)][0]


    def get_team(self, game_id, type):
        
        game = self.game_data(game_id)
        for c in game.get('competitions'):
            return [t.get('team').get('abbreviation') for t in c.get('competitors') if t.get('homeAway') == type][0]


    def get_team_score(self, game_id, type):
        
        game = self.game_data(game_id)
        for c in game.get('competitions'):
            return [t.get('score') for t in c.get('competitors') if t.get('homeAway') == type][0]


    def game_winner(self, game_id):
        game = self.game_data(game_id)
        for c in game.get('competitions'):
            winner = [t.get('team').get('abbreviation') for t in c.get('competitors') if t.get('winner')]
            #print ('winner')
            if len(winner) == 1:
                return winner[0]
            else:
                return None


    def game_loser(self, game_id):
        game = self.game_data(game_id)
        loser = []
        for c in game.get('competitions'):
            #print (c.get('status'))
            if self.game_complete(game_id):
                loser = [t.get('team').get('abbreviation') for t in c.get('competitors') if not t.get('winner')]

        if len(loser) == 1:
            return loser[0]
        else:
            return None


    def game_complete(self, game_id):
        game = self.game_data(game_id)
        
        for c in game.get('competitions'):
            #print (c.get('status'))
            if c.get('status').get('type').get('id') == '3':
                return True
        return False

    #def game_score(self, game_id):
    #    return [competitor.get('home') for competitor in [competition for competition in [x.get('competitions') for x in [game for game in self.data.get('events')] if str(x.get('id')) == str(game_id)]]]

