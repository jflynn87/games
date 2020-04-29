import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from run_app.models import Schedule, Plan, Run
from datetime import timedelta, datetime
import time
from django.db.models import Max
import urllib3
import requests
from pprint import pprint


class StravaData(object):

    def __init__(self):
        self.auth_url = "https://www.strava.com/oauth/token"

        payload = {
            'client_id': "46693",
            'client_secret': '5a55efcff63411fa6cac5bf4e2fc2d43114eb7bc',
            'refresh_token': '4e0be9e1f0e57ce37ea03760e99110ebcea609b0',
            'grant_type': 'refresh_token',
            'f': 'json'
                    }

        #print ("Requesting Token... n")
        res = requests.post(self.auth_url, data=payload, verify=False)
        self.access_token = res.json()['access_token']
        
        print (self.access_token)


    def get_runs(self):
        
        try:
            run_dict = {}
            last_run = Run.objects.latest('date')

            end = time.time()

            start = int(time.mktime(last_run.date.timetuple()))
            now = int(time.time())
            
            activities_url = "https://www.strava.com/api/v3/athlete/activities"
            header = {'Authorization': 'Bearer ' + self.access_token}
            param = {'per_page': 100, 'page': 1, 'after': start, 'before': now}

            dataset = requests.get(activities_url, headers=header, params=param).json()


            for activity in dataset:
                activity_url = 'https://www.strava.com/api/v3/activities/' + str(activity['id'])
                a_header = {'Authorization': 'Bearer ' + self.access_token, 'client_id': "46693",
                'client_secret': '5a55efcff63411fa6cac5bf4e2fc2d43114eb7bc'}
                
                act = requests.get(activity_url, headers=header)    
                
                run_dict[act.json()['start_date_local']] =  \
                    act.json()['type'], \
                    act.json()['distance'], \
                    act.json()['moving_time'], \
                    act.json()['calories']

            return run_dict
        except Exception as e:
            print ('strava api exception', e)
            return {}

        return {}            
    

