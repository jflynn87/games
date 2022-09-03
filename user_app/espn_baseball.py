from datetime import datetime, timedelta
from tkinter import N

import requests
import json


class ESPNData(object):
    '''take an optional espn team id and provides funcitons to retrieve espn baseball data'''

    def __init__(self, team=None):
        start = datetime.now()

        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
        url = 'https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard'
        self.data = requests.get(url, headers=headers).json() 


    def get_score(self, team_list=None):
        
        if not team_list:
            team_list = ['21', ]
        

        all_games = [competition for event in self.data.get('events') for competition in event.get('competitions')]

        focused_games =  [
                competition
                for competition in all_games
                for c in competition.get('competitors')
                if c.get('team').get('id') in team_list
                    ]
        d = {}
        for g in focused_games:
            d[g.get('id')] = {'final': g.get('status').get('type').get('completed'), 'inning': g.get('status').get('period')}
            d.get(g.get('id')).update({'team_' + str(team.get('team').get('id')): {'name': team.get('team').get('name'), 'score': team.get('score'), 'winner': team.get('winner')} for team in g.get('competitors')})
                
        return d       

