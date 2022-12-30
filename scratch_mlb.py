import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")
import django
django.setup()

from django.contrib.auth.models import User
from django.db.models import Min, Q, Count, Sum, Max
from datetime import datetime
from requests import get
import json
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from datetime import datetime

start = datetime.now()




class MLBTeams(object):

    def __init__(self):
        
        all_teams_url = 'http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams'
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}

        all_data = get(all_teams_url, headers=headers).json()
        d  = {}
        for sport in all_data.get('sports'):
            for league in sport.get('leagues'):
                for team in league.get('teams'): 
                    a = team.get('team').get('abbreviation')
                    d[a] = 'http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/' + str(a)
        self.data = d
            
    def team_data(self):
        return self.data


class TeamData(object):

    def __init__(self, team):
        url = 'http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams/' + team
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
        self.all_data = get(url, headers=headers).json()
        




print (MLBTeams().team_data())
print (TeamData('NYM').all_data.get('team').get('franchise').get('team').keys())
exit()

