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
            url =  "https://sports.core.api.espn.com/v2/sports/golf/leagues/pga/athletes/" + str(espn_num)
            self.data = get(url, headers=headers).json()
        #     try:
        #         self.all_stats = [x for x in self.data.get('splits').get('categories')[0].get('stats')]
        #     except Exception as e:
        #         print ('ESPNGolfer fails no stats', espn_num)
        #         self.all_stats = []
        #         self.data = []

        # else:
        #     self.all_stats = []
        #     self.data = []


        
    def get_flag(self):
        try:
            return self.data.get('flag').get('href')
        except Exception as e:
            print ('no espn flag: ', self.espn_num, str(e))
            return ''
