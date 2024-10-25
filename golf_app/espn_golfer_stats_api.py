from datetime import datetime, timedelta

from requests import get
import json

from golf_app import utils
from golf_app.models import Season


class ESPNGolfer(object):
    '''takes an espn golfer number, creates object with golfer info'''

    def __init__(self, espn_num):
        start = datetime.now()

        s = Season.objects.get(current=True)
        self.espn_num = espn_num

        if espn_num:
            headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
            #url =  "http://sports.core.api.espn.com/v2/sports/golf/leagues/pga/seasons/" + str(s.season) + "/types/2/athletes/" + espn_num + "/statistics/0?lang=en&region=us"
            url =  "http://sports.core.api.espn.com/v2/sports/golf/leagues/pga/seasons/2024/types/2/athletes/" + espn_num + "/statistics/0?lang=en&region=us"
            self.data = get(url, headers=headers).json()
            try:
                self.all_stats = [x for x in self.data.get('splits').get('categories')[0].get('stats')]
            except Exception as e:
                print ('ESPNGolfer fails no stats', espn_num)
                self.all_stats = []
                self.data = []

        else:
            self.all_stats = []
            self.data = []


        
    def fedex_rank(self):
        #if self.data.get('splits'):
        try:
            return [x for x in self.all_stats if x.get('name') == 'cupPoints'][0].get('rank')
        except Exception as e:
            print ('no fedexrank: ', self.espn_num)
            return None

    def fedex_points(self):
        #if self.data.get('splits'):
        try:
            return [x for x in self.all_stats if x.get('name') == 'cupPoints'][0].get('value')
        except Exception as e:
            print ('no fedexrank: ', self.espn_num)
            return None

