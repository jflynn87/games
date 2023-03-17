from datetime import datetime
from urllib import request
from bs4 import BeautifulSoup
from wc_app.models import Event, Stage, Group, Team, Data
import json
from requests import get
from urllib.request import urlopen
from bs4 import BeautifulSoup

class ESPNData(object):
    '''espn data and function for WBC.  Takes an optional list of dates for the espn payload and optional stage'''

    #only use event_data for match play events, other data not reliable.
    def __init__(self, stage=None, dates=None):
        start = datetime.now()


        if stage:
            self.stage = stage
        elif Stage.objects.filter(current=True).count() ==1:
            self.stage = Stage.objects.get(current=True)
        if not dates:
            dates = self.stage.event.data.get('ko_dates')

        if len(dates) != 2:
            raise Exception ('must have a list of 2 dates for espn api payload')
        
        url = 'https://site.web.api.espn.com/apis/v2/scoreboard/header?sport=baseball&league=world-baseball-classic&dates=' \
                 + str(dates[0]) + '-' + str(dates[1])

        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
        self.api_data = get(url, headers=headers).json()

        self.data = {}

        if self.api_data.get('sports')[0].get('leagues')[0].get('id') == '3454':
            self.data = self.api_data.get('sports')[0].get('leagues')[0].get('events')
            
        self.rounds = ['2nd Round', 'Semi-Finals', 'Finals']

        print ('WC KO Init duration: ', datetime.now() - start)

        # is this updated as games start?  https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard



    def web_get_data(self, create=False):

        return self.data


    def winners(self):
        d = {}
        for r in self.rounds:
            d[r] = {'winners': [], 'losers': []}
        for game in self.data:
            if game.get('group').get('name') in self.rounds:
                winner = [team for team in game.get('competitors') if team.get('winner')]
                loser = [team for team in game.get('competitors') if not team.get('winner')]
                if winner and len(winner) ==1:
                    l  = d.get(game.get('group').get('name')).get('winners')
                    l.append(winner[0].get('name'))
                if loser and len(loser) ==1:
                    l  = d.get(game.get('group').get('name')).get('losers')
                    l.append(loser[0].get('name'))

        return d

    def stage_complete(self):
        status = [game.get('status') for game in self.data if game.get('group').get('name') == 'Finals'][0]
        if status == 'post':
            return True
        return False

    def new_data(self):
        return True
