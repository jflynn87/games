from datetime import datetime
from urllib import request
from bs4 import BeautifulSoup
from wc_app.models import Event, Stage, Group, Team, Data
import json


class ESPNData(object):
    '''used for standings related fuctions for WBC'''

    #only use event_data for match play events, other data not reliable.
    def __init__(self, url=None, stage=None):
        start = datetime.now()

        if url:
            self.url = url
        else:
            self.url = 'https://www.espn.com/world-baseball-classic/standings'
        
        html = request.urlopen(self.url)
        self.soup = BeautifulSoup(html, 'html.parser')

        if stage:
            self.stage = stage
        elif Stage.objects.filter(current=True).count() ==1:
            self.stage = Stage.objects.get(current=True)
        else:
            self.stage = Stage.objects.get(name="Group Stage",event__current=True)

        print ('WC Init duration: ', datetime.now() - start)


    def get_team_data(self, create=False):
        start = datetime.now()
        t_body = self.soup.find_all('tbody', {'class': "Table__TBODY"})[0]
        d = {}
        for i, row in enumerate(t_body.find_all('tr')):
            if row.text[0:4] == 'Pool':
                pool = row.text
            else:
                d[row['data-idx']] = {
                        'full_name': row.find('span', {'class': 'hide-mobile'}).text,
                        'abbr': row.find('span', {'class': 'dn show-mobile'}).text,
                        'flag': 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/countries/500/' + row.find('span', {'class': 'dn show-mobile'}).text + '.png&h=40&w=40',
                        'row-index': row['data-idx'],
                        'pool': pool,
                        }
        
        records = self.soup.find_all('tbody', {'class': "Table__TBODY"})[1]

        for row in records.find_all('tr'):
            if d.get(row['data-idx']):
                d.get(row['data-idx']).update({'wins': row.find_all('td')[0].text,
                                           'loss': row.find_all('td')[1].text,
                                           'pct': row.find_all('td')[2].text,
                                           'gb': row.find_all('td')[3].text,
                                           'scored': row.find_all('td')[4].text,
                                           'against': row.find_all('td')[5].text,
                                           })
        
        print ('group d create dur: ', datetime.now() - start)
        return d 


    def teams_by_pool(self):
        data = self.get_team_data()
        d = {v.get('pool'): {} for k,v in data.items()}
        print ('DD ', d)
        pool_d = {d.get(v.get('pool')).update({k: v}) for k,v in data.items()}
        
        return d
    
    
    def get_pool_names(self):
        t_body = self.soup.find_all('tbody', {'class': "Table__TBODY"})[0]
        l = []
        for row in t_body.find_all('tr'):
            if row.text[0:4] == 'Pool':
                l.append(row.text)
        
        return l


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
        
        # sorted_pcts = sorted(pcts, key=lambda x:(x.get('pct'), x.get('scored')), reverse=True)
        # print ('sorted pcts: ', sorted_pcts)
        # print ('team data: ', t_data)
        # orig_idx = next((index for (index,d ) in enumerate(sorted_pcts) if d['abbr'] == team.name))
        
        # if len({k:v for k,v  in data.items() if v.get('pool') == team.group.group and v.get('pct') == t_data.get('pct')}) == 1:
        #     return  orig_idx + 1
        # elif len({k:v for k,v in data.items() if v.get('pool') == team.group.group and v.get('pct') == t_data.get('pct') and v.get('scored') == t_data.get('scored')}) == 1:
        #     return orig_idx + 1
               
        # same_win_pct = [{'abbr':v.get('abbr'), 'pct': v.get('pct'), 'scored': v.get('scored'), 'against': v.get('against')}  \
        #                 for k, v in data.items() if v.get('pool') == team.group.group and v.get('pct') == t_data.get('pct')]
        # sorted_against = sorted(same_win_pct, key=lambda x:int(x.get('against')))
        
        # same_win_pct_best = next((index for (index,d ) in enumerate(sorted_pcts) if d['pct'] == t_data.get('pct') and d['scored'] == t_data['scored']))
        # return same_win_pct_best +1          
        # idx = same_win_pct_best
        # while True:
        #     print (team, idx)
        #     if idx != 0:
        #         if float(sorted_pcts[same_win_pct_best].get('against')) == float(sorted_pcts[idx-1].get('against')): 
        #             idx -= 1
        #         else: 
        #             return idx +1
        #     else:
        #         if idx == 0:
        #             rank = 1
        #         else:
        #             rank = idx + 1
        #         return rank
        # print ('Team Rank after tie check: ', team, rank)
        # return rank
