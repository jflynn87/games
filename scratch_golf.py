import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from golf_app.models import Tournament, TotalScore, ScoreDetails, Field, Picks, PickMethod, BonusDetails, Season, Golfer, Group
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
from golf_app import views, manual_score, scrape_scores, populateField, withdraw
   
season = Season.objects.get(current=True)
users = season.get_users()
print (users)

pk_list = []
for t in Tournament.objects.filter(season__current=True):
    pk_list.append(t.pk)


#scrape = scrape_scores.ScrapeScores(t)
#scrape.scrape()
f = open('handicap.txt', 'wb')

for key in pk_list:#pk_list[-15:]:
    t = Tournament.objects.get(pk=key)
    print (t)
    min_list = []
    max_list = []
    for f6 in Field.objects.filter(tournament=t, group__number=6):
        min_list.append(f6.handicap())
    max_group = Group.objects.filter(tournament=t).aggregate(Max('number'))
    for f_last in Field.objects.filter(tournament=t, group__number=max_group.get('number__max')):
        max_list.append(f_last.handicap())


    f.write('handicap range in group 6: ', min(min_list), max(max_list))
    handicap = 0

    h_dict = {}
    for u in users:
        user_o = User.objects.get(pk=u.get('user'))
        handicap = 0
        for sd in ScoreDetails.objects.filter(pick__playerName__tournament=t, user=user_o):
                handicap = handicap + sd.pick.playerName.handicap()
        score = TotalScore.objects.get(tournament=t, user=sd.user)
        #print (score)
        h_dict[user_o.username] = handicap, score.score, score.score - handicap


    sorted_h = sorted(h_dict.items(), key=lambda x: x[1][2])

    for k in sorted_h:
        f.write(k)
        print (str(k))

f.close()



#for golfer in Field.objects.filter(tournament=t):
#    print (golfer, 'owgr: ', golfer.currentWGR, ',  ', golfer.handicap())