from datetime import datetime, timedelta
import requests 
#import json



class ESPNData(object):
    '''takes an optinal dict and provides funcitons to retrieve espn golf data'''

    def __init__(self, week=None):
        from fb_app.models import Week
        if week:
            self.week = week
        else:
            week = Week.objects.get(current=True)

        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
        url = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
        #payload = {'week':'1'}
        payload = {}  #works for pre season/current week?
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
                    
                    if c.get('team').get('name'):
                        t_name = c.get('team').get('name')

                    elif c.get('team').get('displayName') == "Washington":
                        t_name = "Football Team"
                        t_abbr = c.get('team').get('abbreviation')
                    else:
                        raise Exception('uknown team: ', c.get('team'))                        
                        
                    if c.get('homeAway') == 'home':
                        home = Teams.objects.get(long_name=t_name)
                        if c.get('team').get('abbreviation') == "WSH":
                            home_abbr = "WAS"
                        else:
                            home_abbr = c.get('team').get('abbreviation')
                        home_score = c.get('score')
                        if c.get('winner'): 
                            winner = home_abbr

                    elif c.get('homeAway') == "away":
                        away = Teams.objects.get(long_name=t_name)
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
                                  'winner': winner}
        return d


    

            