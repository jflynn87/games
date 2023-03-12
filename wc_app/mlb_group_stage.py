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

        if url:
            self.url = url
        else:
            self.url = 'https://www.mlb.com/world-baseball-classic/2023-bracket-standings'
        
        #context = ssl._create_unverified_context()
        #headers = {'User-Agent': 'Mozilla/5.0 (Linux; A
        # ndroid 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
        
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
        req = Request(url=self.url, headers=headers)
        html = urlopen(req).read()
        #html = get(self.url, headers=headers)
        self.soup = BeautifulSoup(html, 'html.parser')

        if stage:
            self.stage = stage
        elif Stage.objects.filter(current=True).count() ==1:
            self.stage = Stage.objects.get(current=True)
        else:
            self.stage = Stage.objects.get(name="Group Stage",event__current=True)

        #self.api_data = html
        
        print ('WC Init duration: ', datetime.now() - start)


    def get_team_data(self, create=False):
        start = datetime.now()
        tables = self.soup.find_all('div', {'class': 'l-grid__content l-grid__content--flat-card'})
        print (len(tables))
        d = {}
        for t in tables[0:4]:
            pool = t.find('div', {'class': 'p-table__title'}).text[0:6]
            d[pool] = {}
            for i, row in enumerate(t.find_all('tr')[1:]):
                tds = row.find_all('td')
                d[pool].update({tds[1].text.strip('*'): {'wins': tds[2].text, 'loss': tds[3].text, 'pct': tds[4].text, 'rank': i+1}})
        
        print ('group d create dur: ', datetime.now() - start)
        
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
        
