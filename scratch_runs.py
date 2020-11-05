import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from run_app.models import Schedule, Plan, Run, Shoes
from datetime import timedelta, datetime
import time
from django.db.models import Max

#from django.db.models import Min, Q, Count, Sum, Max
#from django.db.models.functions import ExtractWeek, ExtractYear



#import urllib
import urllib3
#from bs4 import BeautifulSoup
#import json

#import urllib3.request
#from bs4 import BeautifulSoup
#from run_app import scrape_runs

import requests
from pprint import pprint
from run_app import strava
import time
import json



start = datetime.now()
print ('starting.... ', datetime.now())
runs = strava.StravaData(datetime.strptime('Sep 1 2020', '%b %d %Y'))
run_dict =  runs.get_runs()

for row in json.loads(run_dict):
    day = row['date'].split('T')[0]
    if Run.objects.filter(date=day).exists() or row['activity'] != "Run":
        continue
    else:

        print ('missing:  ', "DATE: ", row['date'],  
        "DIST: ", round(row['distance']/1000, 2), 
        "TIME: ",  timedelta(seconds=row['time']), 
        "CALS: " , row['calories'])
        date = row['date'].split('T')[0]
        dist = round(row['distance']/1000, 2) 
        t =  timedelta(seconds=row['time']) 
        cals = row['calories']


        Run.objects.get_or_create(date=datetime.strptime(date, '%Y-%m-%d'), 
                    dist = dist, 
                    time = t,
                    cals = cals,
                    shoes = Shoes.objects.get(main_shoe=True),
                    location = 1
                     )





print ('finsihed.... ', datetime.now() - start)
  



# auth_url = "https://www.strava.com/oauth/token"

# payload = {
#     'client_id': "46693",
#     'client_secret': '5a55efcff63411fa6cac5bf4e2fc2d43114eb7bc',
#     'refresh_token': '4e0be9e1f0e57ce37ea03760e99110ebcea609b0',
#     'grant_type': 'refresh_token',
#     'f': 'json'
#             }

# print ("Requesting Token... n")
# res = requests.post(auth_url, data=payload, verify=False)
# access_token = res.json()['access_token']
# print (access_token)

# #start = datetime.strftime('2020-04-24', '%Y-%m-%d')
# last_run = Run.objects.latest('date')

# end = time.time()
# #start = time.mktime(last_run.date.timetuple())*1000
# start = int(time.mktime(last_run.date.timetuple()))
# now = int(time.time())
# #print (start)
# #print (now)

# activities_url = "https://www.strava.com/api/v3/athlete/activities"
# header = {'Authorization': 'Bearer ' + access_token}
# param = {'per_page': 100, 'page': 1, 'after': start, 'before': now}

# dataset = requests.get(activities_url, headers=header, params=param).json()

# #print (dataset)

# for activity in dataset:
#     id = activity['id']
#     #print (id)

#     activity_url = 'https://www.strava.com/api/v3/activities/' + str(id)
#     a_header = {'Authorization': 'Bearer ' + access_token, 'client_id': "46693",
#     'client_secret': '5a55efcff63411fa6cac5bf4e2fc2d43114eb7bc'}
#     #a_param = {id}
#     act = requests.get(activity_url, headers=header)    
#     #act = requests.get(activity_url + '/' + str(id) + '?' + access_token)
#     print ('----------------------------------------------------------------')
#     print (act.json()['id'])
#     print (act.json()['type'])
#     print (act.json()['start_date_local'])
#     print (act.json()['distance'])
#     print (act.json()['calories'])
    
    

