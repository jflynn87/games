import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from fb_app.models import Week, WeekScore, Player, League, Games, User, Picks, Player
from golf_app.models import BonusDetails, Tournament, Field, Picks, Group, TotalScore, Season
#from datetime import datetime, timedelta
import datetime
import sqlite3
from django.db.models import Min, Q, Count
from golf_app import calc_score
import golf_app.populateField
#import urllib

from django.db import transaction
from bs4 import BeautifulSoup
import urllib.request
import json

def get_data():

    json_url = "https://statdata.pgatour.com/r/470/2019/leaderboard_mp.json"

    with urllib.request.urlopen(json_url) as field_json_url:
        data = json.loads(field_json_url.read().decode())

    field = data['rounds']
    #print ((field[0]))
    for k,v in field[0].items():
        #print (k, type(v))
        if k == "brackets":
            i = 0
            j = 2
            while i <= 16:
                #print (i)
                for key, value in v[i].items():
                    if key == "groups":
                        #print ('Group: ', value[0])
                        print (value[1]['debug']['group'])
                        print (value[0]['players'][0]['lName'])
                        print (value[0]['players'][1]['lName'])
                        print (value[1]['players'][0]['lName'])
                        print (value[1]['players'][1]['lName'])
                if i == 3:
                    while j < 10:
                        print ('i=', i, "j=", j)
                        print (v[i]['groups'][j]['debug']['group'])
                        print (v[i]['groups'][j]['players'][0]['lName'])
                        print (v[i]['groups'][j]['players'][1]['lName'])
                        print (v[i]['groups'][j+1]['players'][0]['lName'])
                        print (v[i]['groups'][j+1]['players'][1]['lName'])
                        j += 1


                    #print ((v[i]['groups'][4]['players']))
                    #print ((v[i]['groups'][5]))
                i += 1

get_data()
