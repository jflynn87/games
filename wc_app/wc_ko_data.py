from datetime import datetime
from urllib import request
from bs4 import BeautifulSoup
from wc_app.models import Event, Stage, Group, Team, Data
import json
from requests import get
from urllib.request import urlopen
from bs4 import BeautifulSoup

class ESPNData(object):
    '''takes an optinal dict and provides funcitons to retrieve espn golf data,
        all_data is a list of dicts
        event_data is the data for the event but most is in competition
        competition_data varoius datat about  the tournament
        field_data is the actual golfers in the tournament'''

    #only use event_data for match play events, other data not reliable.
    def __init__(self, stage=None, source=None):
        start = datetime.now()

        if source == 'web':
            data = {'stage_1': [],
                    'stage_2': [],
                    'stage_3': [],
                    'stage_4': [],
                    'stage_5': [],
            }
            url = 'https://www.espn.com/soccer/bracket'
            html = urlopen(url)
            #html = get(web_url)
            soup = BeautifulSoup(html, 'html.parser')
            bracket = soup.find('div', {'class': 'BracketLayout'})
            breaks = [7, 11, 13]
            stage_num = 1
            for i, game in enumerate(bracket.find_all('div', {'class': 'BracketCell__Competitors'})):
                for team in game.find_all('div', {'class': 'BracketCell__Name'}):
                    data.get('stage_' + str(stage_num)).append(team.text)
                    #data.get('stage_' + str(stage_num)).update({team.text})
                    #data[team.text] = {}
                if i in breaks:
                   print ('ii', stage_num)
                   #stage_num = 'stage_' + str(breaks.index(i) + 1)
                   stage_num = int(stage_num) + 1

            self.data = data
        else:
            #url = 'https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard'
            url = 'https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard?limit=950&dates=20221203-20221227'
            headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
            self.api_data = get(url, headers=headers).json()

            self.data = {}
            
            if self.api_data.get('leagues')[0].get('id') == '606':
                self.data = self.api_data.get('events')
            

        if stage:
            self.stage = stage
        elif Stage.objects.filter(current=True).count() ==1:
            self.stage = Stage.objects.get(current=True)

        else:
            self.stage = Stage.objects.get(name="Knockout Stage",event__current=True)

        self.rounds = ['round-of-16','quarterfinals', 'semifinals', '3rd-place', 'final']

        print ('WC KO Init duration: ', datetime.now() - start)

        # is this updated as games start?  https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard



    def web_get_data(self, create=False):

        return self.data


    def api_winners_losers(self):
        d = {}
        for r in self.rounds:
            d[r] = {'winners': [], 'losers': []}
        for match in self.data:
            for competition in match.get('competitions'):
                if competition.get('status').get('type').get('completed'):
                    for team in competition.get('competitors'):
                        if team.get('winner'):
                            d.get(match.get('season').get('slug')).get('winners').append(team.get('team').get('abbreviation')) 
                        else:
                            d.get(match.get('season').get('slug')).get('losers').append(team.get('team').get('abbreviation')) 
        return d
                            

    def stage_complete(self):
        for match in self.data:
            for competition in match.get('competitions'):
                if not competition.get('status').get('type').get('completed'):
                    return False
        return True
        

