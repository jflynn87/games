import os
#os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

#import django
#django.setup()
from run_app.models import Schedule, Plan, Run
from datetime import timedelta, datetime
import time
from django.db.models import Max
import urllib3
import requests
from pprint import pprint
import json


class StravaData(object):

    def __init__(self, start_date=None):
        self.auth_url = "https://www.strava.com/oauth/token"

        payload = {
            'client_id': os.environ['strava_client_id'],
            'client_secret': os.environ['strava_client_secret'],
            'refresh_token': os.environ['strava_refresh_token'],
            'grant_type': 'refresh_token',
            'f': 'json'
                    }

        #print ("Requesting Token... n")
        res = requests.post(self.auth_url, data=payload, verify=True)
        self.access_token = res.json()['access_token']
        
        print (self.access_token)

        if start_date == None:
            run = Run.objects.latest('date')
            self.start_date = run.date
        else:
            self.start_date  = start_date 


    def get_runs(self):
        
        try:
            run_list = []
            
            #last_run = Run.objects.latest('date')
            print ('sd', self.start_date)
            last_run = self.start_date

            end = time.time()

            #start = int(time.mktime(last_run.date.timetuple()))
            start = int(time.mktime(last_run.timetuple()))
            now = int(time.time())
            
            activities_url = "https://www.strava.com/api/v3/athlete/activities"
            header = {'Authorization': 'Bearer ' + self.access_token}
            param = {'per_page': 100, 'page': 1, 'after': start, 'before': now}

            dataset = requests.get(activities_url, headers=header, params=param).json()


            for activity in dataset:
                #print ('activity loop')
                activity_url = 'https://www.strava.com/api/v3/activities/' + str(activity['id'])
                a_header = {'Authorization': 'Bearer ' + self.access_token, 'client_id': "46693",
                'client_secret': '5a55efcff63411fa6cac5bf4e2fc2d43114eb7bc'}
                
                act = requests.get(activity_url, headers=header)    
                
                run_list.append({
                 'date': act.json()['start_date_local'],
                 'activity': act.json()['type'], 
                 'distance': act.json()['distance'], 
                 'time': act.json()['moving_time'], 
                 'calories': act.json()['calories'] })
            print ('strava', run_list)
            return json.dumps(run_list)
            
        except Exception as e:
            print ('strava api exception', e)
            return {}

        return {}            
    

