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
            url = 'https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard'
            headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
            self.data = get(url, headers=headers).json()


        if stage:
            self.stage = stage
        elif Stage.objects.filter(current=True).count() ==1:
            self.stage = Stage.objects.get(current=True)

        else:
            self.stage = Stage.objects.get(name="Knockout Stage",event__current=True)

        print ('WC KO Init duration: ', datetime.now() - start)

        # is this updated as games start?  https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard



    def web_get_data(self, create=False):

        return self.data

    def api_get_data(self):
        #for sport in self.data.get('sports'):
        #    print (sport.get('name'))
        print (self.data.keys())
        for event in self.data.get('events'):
            #print (event.keys())
            for competition in event.get('competitions'):
                print ('----------------------------------')
                print (competition.get('status'))
                print (competition.keys())
                for competitor in competition.get('competitors'):
                    print (competitor.get('team').get('displayName'))
                print ('----------------------------------')
        return []
