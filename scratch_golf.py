import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from golf_app.models import Tournament, TotalScore, ScoreDetails, Picks, PickMethod, BonusDetails, Season, Golfer, Group, Field, ScoreDict
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import sqlite3
from django.db.models import Min, Q, Count, Sum, Max
from django.db.models.functions import ExtractWeek, ExtractYear
import time
from requests import get
from random import randint
import sys
# pip install PyQt5 and PyQtWebEngine
#from PyQt5.QtWidgets import QApplication, QWidget
#from PyQt5.QtCore import QUrl
#from PyQt5.QtWebEngineWidgets import QWebPage
#from PyQt5.QtWebEngine import QtWebEngine as QWebPage

#from PyQt5.QtWebEngineWidgets import QWebEngineView
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from selenium import webdriver
import urllib
import json
from golf_app import views, manual_score, populateField, withdraw, scrape_scores_picks, utils, scrape_cbs_golf, scrape_masters, scrape_espn, update_favs
from unidecode import unidecode
from django.core import serializers
from golf_app.utils import formatRank, format_name, fix_name
from golf_app import golf_serializers
import pytz
from collections import OrderedDict
import math

start = datetime.now()

#with open('owgr.json') as f:
#  owgr = json.load(f)
for sd in ScoreDict.objects.all():
    #print (sd.tournament)
    solo_2 = {k:v for k,v in sd.data.items() if v.get('rank') =='2'}
    solo_3 = {k:v for k,v in sd.data.items() if v.get('rank') =='3'}
    if len(solo_2) > 0 and len(solo_3) > 0:
        print (sd.tournament, sd.tournament.season)
        print (solo_2)
        print (solo_3)
        print ('-----------------------')
exit()
sds = ScoreDetails.objects.filter(pick__playerName__tournament=t)
print (sd)

exit()
for t in Tournament.objects.all():
    sd = ScoreDetails.objects.filter(pick__playerName__tournament=t).values('user').annotate('score')
    print (sd)
    if len(sd) < 0:
        print (sd)

exit()
t = Tournament.objects.get(current=True)
with open('owgr.json') as f:
  owgr = json.load(f)
#owgr = populateField.get_worldrank()
#owgr = {}
field  = populateField.get_field(t, owgr)
sorted_field = {k:v for k,v in sorted(field.items(), key=lambda item: item[1].get('curr_owgr'))}
print (sorted_field)
exit()
#print (Field.objects.filter(tournament__current=True).count())
f = Field.objects.get(tournament=t, playerName__startswith="By")
print (f, f.recent_results())
exit()


#cbs_web = scrape_cbs_golf.ScrapeCBS().get_data()
#pga_web = scrape_scores_picks.ScrapeScores().scrape_zurich()
#print (pga_web)
#print ('PGA: ', pga_web['info'])
#print ('PGA: ', pga_web['Cameron Smith'])
#print ('CBS: ', cbs_web['info'])
#print ('CBS: ', cbs_web['Cameron Smith'])
#t = Tournament.objects.get(current=True)
#f_start  = datetime.now()
#for pick in Picks.objects.filter(playerName__tournament=t):
    #print (pick)
#    web.get(unidecode(pick.playerName.playerName)).update({'group': pick.playerName.group.number})
    #print (web.get(pick.playerName.playerName))
#print ('duration: ', datetime.now() - start)
#print (web['info'])
exit()





#for player in data['Tournament']['Players']:
#for player in ['Ted Potter, Jr.', ]:
#    name = (' '.join(reversed(player["PlayerName"].rsplit(', ', 1))))
#    print (player.get('PlayerName'), player.get('TournamentPlayerId'), utils.fix_name(name, owgr))
print (utils.fix_name('Ted Potter, Jr.', owgr))


exit()




field = scrape_espn.ScrapeESPN().get_field()
#players = scrape_espn.ScrapeESPN().get_espn_players()
for k, v in field.items():
    print (k, v)
print (len(field))
print (Field.objects.filter(tournament__current=True).count())

exit()

f = Field.objects.get(tournament__current=True, playerName='Matt Kuchar')
print (f.recent_results())
print (datetime.now() - start)
print (f.prior_year_finish())
print (datetime.now() - start)
exit()
def get_mp_result(f, sd):
    #winner = {k:v for k, v in sd.data.items() if k == 'Finals' and {num:match for num, match in v.items() if match.get('winner') == f.playerName}}
    if {k:v for k, v in sd.data.items() if k == 'Finals' and {num:match for num, match in v.items() if match.get('winner') == f.playerName}}:
        return 1 
    elif {k:v for k, v in sd.data.items() if k == 'Finals' and {num:match for num, match in v.items() if match.get('loser') == f.playerName}}:
        return 2
    elif {k:v for k, v in sd.data.items() if k == '3rd Place' and {num:match for num, match in v.items() if match.get('winner') == f.playerName}}:
        return 3
    elif {k:v for k, v in sd.data.items() if k == '3rd Place' and {num:match for num, match in v.items() if match.get('loser') == f.playerName}}:
        return 4
    elif {k:v for k, v in sd.data.items() if k == 'Quaterfinals' and {num:match for num, match in v.items() if match.get('loser') == f.playerName}}:
        return 5
    elif {k:v for k, v in sd.data.items() if k == 'Round of 16' and {num:match for num, match in v.items() if match.get('loser') == f.playerName}}:
        return 9
    else:
        return 17



t = Tournament.objects.get(season__current=True, pga_tournament_num='470')
sd = ScoreDict.objects.get(tournament=t)



for f in Field.objects.filter(tournament=t):
    print (f.playerName, get_mp_result(f, sd))

print (datetime.now() - start)
