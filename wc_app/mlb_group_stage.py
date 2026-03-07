from datetime import datetime
#from urllib import request
from urllib.request import Request, urlopen
from requests import get 
from bs4 import BeautifulSoup
from wc_app.models import Event, Stage, Group, Team, Data
import json
import ssl


class MLBData(object):
    '''used for standings related fuctions for WBC'''

    #only use event_data for match play events, other data not reliable.
    def __init__(self, url=None, stage=None):
        start = datetime.now()

        if stage:
            self.stage = stage
        elif Stage.objects.filter(current=True).count() ==1:
            self.stage = Stage.objects.get(current=True)
        else:
            self.stage = Stage.objects.get(name="Group Stage",event__current=True)

        if url:
            self.url = url
        else:
            self.url = self.stage.score_url
        
        #context = ssl._create_unverified_context()
        #headers = {'User-Agent': 'Mozilla/5.0 (Linux; A
        # ndroid 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
        
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
        req = Request(url=self.url, headers=headers)
        html = urlopen(req).read()
        #html = get(self.url, headers=headers)
        self.soup = BeautifulSoup(html, 'html.parser')

        #self.api_data = html
        
        print ('WC Init duration: ', datetime.now() - start)


    def get_team_data(self, create=False):
        start = datetime.now()
        tables = self.soup.find_all('table', class_='p-table')
        print('Tables: ', len(tables))
        d = {}
        
        for table in tables:
            # Extract pool name from summary attribute or table title
            pool_name = table.get('summary', 'Unknown Pool').split('-')[0].strip().split()[1]  # Get first word as pool name
            print ('Pool name: ', pool_name)
            
            # Get headers from thead
            headers = []
            thead = table.find('thead')
            if thead:
                header_row = thead.find('tr')
                headers = [th.get_text().strip() for th in header_row.find_all('th')]
            
            d[pool_name] = {}
            
            # Process data rows from tbody
            tbody = table.find('tbody')
            if tbody:
                for i, row in enumerate(tbody.find_all('tr')):
                    cells = row.find_all('td')
                    if len(cells) >= len(headers):
                        # Extract team name (assuming it's in the second column after image)
                        team_name = cells[1].get_text().strip('*')
                        if team_name == 'USA':
                            team_name = 'United States'
                        elif team_name == 'Korea':
                            team_name = 'South Korea'
                        elif team_name == 'Dominican Rep.':
                            team_name = 'Dominican Republic'
                        
                        # Build data dict dynamically based on headers
                        team_data = {'rank': i + 1}
                        for j, header in enumerate(headers[2:], start=2):  # Skip first two columns (image, team)
                            if j < len(cells):
                                team_data[header.lower()] = cells[j].get_text().strip()
                        
                        d[pool_name][team_name] = team_data
        
        print('group d create dur: ', datetime.now() - start)
        return d 


    # def get_pool_names(self):
    #     t_body = self.soup.find_all('tbody', {'class': "Table__TBODY"})[0]
    #     l = []
    #     for row in t_body.find_all('tr'):
    #         if row.text[0:4] == 'Pool':
    #             l.append(row.text)
        
    #     return l


    def new_data(self):
        try:
            saved_d = Data.objects.get(stage=self.stage)
            if saved_d.force_refresh:
                return True
            if saved_d.group_data == self.get_team_data():
                print ('no new data')
                return False
            else:
                print ('new data')
                return True
        except Exception as e:
            print ('ESPN WC API new data check error: ', e)
            return True
        
    def get_rank(self, team, data):
        print ('team')
        if not data:
            data = self.get_team_data()
        #print (data)
        pcts = [{'key': k, 'abbr':v.get('abbr'), 'pct': v.get('pct'), 'scored': v.get('scored'), 'against': v.get('against'), 'pool': v.get('pool')} for k, v in data.items() if v.get('pool') == team.group.group]
        t_data = [{'key': k, 'abbr':v.get('abbr'), 'pct': v.get('pct'), 'scored': v.get('scored'), 'against': v.get('against'), 'pool': v.get('pool')} for k, v in data.items() if v.get('abbr') == team.name][0]
        print (t_data)
        if t_data.get('pool') == 'Pool A':
            return t_data.get('key')  
        elif t_data.get('pool') == 'Pool B':
            return int(t_data.get('key')) - 6 #('includes header rows)
        elif t_data.get('pool') == 'Pool C':
            return int(t_data.get('key')) - 12
        elif t_data.get('pool') == 'Pool D':
            return int(t_data.get('key')) - 18
        else:
            return 5
        
