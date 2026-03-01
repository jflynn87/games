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
            self.url = 'https://en.wikipedia.org/wiki/2026_World_Baseball_Classic'
         
        e = Event.objects.get(current=True)

        if not stage:
            self.stage = Stage.objects.get(current=True, event=e)
        else:
            self.stage = stage

        context = ssl._create_unverified_context()
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}

        req = request.Request(self.url, headers=headers)
        html = urlopen(req, context=context)

        soup = BeautifulSoup(html, 'html.parser')

        tables = soup.find_all('table', {'class': 'wikitable'})

        table = tables[0]
        #print (table)
        teams = {}

        for i, row in enumerate(table.find_all('tr')[1:]):
            th = row.find('th')
            if th:
                # Extract flag URL
                img = th.find('img')
                flag = 'https:' + img.get('src') if img else None
                
                # Extract team name from the link
                link = th.find('a')
                team_name = link.text.strip() if link else None
                rank = row.find_all('td')[-1].text.strip()   
                teams[team_name] = {
                    'flag': flag,
                    'rank': rank
                }

        pool = tables[2]
        data = {'A': [], 'B': [], 'C': [], 'D': []}
        groups = ['A', 'B', 'C', 'D']

        for row in pool.find_all('tr')[1:]:
            cells = row.find_all('td')
            for i, cell in enumerate(cells):
                if i < 4:  # Only process first 4 columns (A, B, C, D)
                    team_link = cell.find('a')
                    if team_link:
                        team_name = team_link.text.strip()
                        data[groups[i]].append({'team_name': team_name, 'flag': teams[team_name]['flag'], 'rank': teams[team_name]['rank']})


        self.data = data

    def create_teams(self, group_prefix=None):
        Group.objects.filter(stage=self.stage).delete()
        for group, teams in self.data.items():
            g = Group()
            g.stage = self.stage
            g.group= group_prefix + group if group_prefix else group
            g.save()
            for team in teams:
                t = Team()
                t.group = g
                t.name = team.get('team_name')
                t.rank = team.get('rank')
                t.flag_link = team.get('flag')
                t.full_name = team.get('team_name')
                t.save()
        return Team.objects.filter(group__stage=self.stage)


