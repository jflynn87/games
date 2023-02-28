from datetime import datetime
from urllib import request
from bs4 import BeautifulSoup
from wc_app.models import Event, Stage, Group, Team, Data
import json
import ssl
from urllib.request import urlopen



class TeamData(object):
    '''takes an optinal dict and provides funcitons to retrieve espn golf data,
        all_data is a list of dicts
        event_data is the data for the event but most is in competition
        competition_data varoius datat about  the tournament
        field_data is the actual golfers in the tournament'''

    #only use event_data for match play events, other data not reliable.
    def __init__(self, url=None, stage=None):
        start = datetime.now()

        if url:
            self.url = url
        else:
            self.url = 'https://en.wikipedia.org/wiki/2023_World_Baseball_Classic'
         
        e = Event.objects.get(current=True)

        if not stage:
            self.stage = Stage.objects.get(current=True, event=e)
        else:
            self.stage = stage

        context = ssl._create_unverified_context()
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}

        html = urlopen(self.url, context=context)
        soup = BeautifulSoup(html, 'html.parser')

        tables = soup.find_all('table', {'class': 'wikitable'})

        table = tables[4]
        data = {}
        for i, row in enumerate(table.find_all('tr')):
            if i == 0:
                for j, th in enumerate(row.find_all('th')):
                    t = th.text.split('(')[0].strip()
                    data[t] = {}
                    if j == 0:
                        a = t
                    elif j == 1: 
                        b = t
                    elif j == 2:
                        c = t
                    elif j == 3:
                        d = t
                    else:
                        raise Exception('I index error, why are we here')
            else:
                for k, td in enumerate(row.find_all('td')):
                    country = td.text.split('(')[0].strip()
                    rank = td.text.split('(')[1].split(')')[0].strip()
                    flag = 'https:' + td.img.get('src')
                    if k == 0:
                        data[a].update({country: {'rank': rank, 'flag': flag}})
                    elif k == 1:
                        data[b].update({country: {'rank': rank, 'flag': flag}})
                    elif k == 2:
                        data[c].update({country: {'rank': rank, 'flag': flag}})
                    elif k == 3:
                        data[d].update({country: {'rank': rank, 'flag': flag}})
                    else:
                        raise Exception('J index issue, why here')

        self.data = data

    def create_teams(self):
        Group.objects.filter(stage=self.stage).delete()
        for group, teams in self.data.items():
            g = Group()
            g.stage = self.stage
            g.group= group
            g.save()
            for team, data in teams.items():
                t = Team()
                t.group = g
                t.name = team
                t.rank = data.get('rank')
                t.flag_link = data.get('flag')
                t.full_name = team
                t.save()
        return Team.objects.filter(group__stage=self.stage)