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
from golf_app import views, manual_score, scrape_scores, populateField, withdraw, scrape_scores_by_id


first_picks = {'Sam36': ['Sungjae Im', 'Tom Lewis', 'Charles Howell III', 'Dylan Frittelli', 'Harold Varner III', 'Mark Hubbard', 'Ryan Armour', 'Sam Ryder', 'Bronson Burgoon',
 'Peter Uihlein', 'Nelson Ledesma', 'John Senden'],
  'JoeLong': ['Shane Lowry', 'Sung Kang', 'J.T. Poston', 'Dylan Frittelli', 'Andrew Landry', 'Brian Stuard', 'Charl Schwartzel',
 'Kyoung-Hoon Lee', 
'Hank Lebioda',
'Kramer Hickok',
'Michael Gligic',
'Michael Kim'], 
'BigDipper': ['Webb Simpson',
'Tom Lewis',
'Jason Kokrak',
'Matt Jones',
'Ryan Moore',
'Tom Hoge',
'Russell Knox',
'Cameron Davis',
'Jason Dufner',
'Sebastian Cappelen',
'Rob Oppenheim',
'Arjun Atwal',],
'JL Choice':
['Paul Casey',
'Brendon Todd',
'Matthias Schwab',
'Dylan Frittelli',
'Si woo Kim',
'Sepp Straka', 
'Russell Henley', 
'Will Gordon', 
'Bronson Burgoon', 
'Matt Every', 
'Luke Donald',
'Ben Taylor']
}


t = Tournament.objects.get(current=True)

for k,v in first_picks.items():
    score = 0
    cuts = 0
    #print (k)
    for p in v:
    #    print (p)
        f = Field.objects.get(playerName=p, tournament=t)
        if f.rank_as_int() > 64:
            score += 78
            cuts += 1
        else:
            score += f.rank_as_int()
        #print(p, f.rank_as_int(), score)
    print ('orig picks: ', k, score, cuts)
    try:
        ts = TotalScore.objects.get(tournament=t, user__username=k)
        print ('game score: ', ts.user, ts.score, ts.cut_count)

    except Exception as e:
        continue



 



#season = Season.objects.get(current=True)
#users = season.get_users()
#print (users)

#pk_list = []
#for t in Tournament.objects.filter(season__current=True):
#    pk_list.append(t.pk)


#f = open('handicap.txt', 'wb')

#t = Tournament.objects.get(current=True)
#try:
#    scrape_scores_by_id.ScrapeScores(t).scrape()
#except Exception as e:
#    print ('Fail: ', t, e)

#from django.contrib.admin.models import LogEntry

#logs = LogEntry.objects.all() #or you can filter, etc.
#for l in logs:
#    print (l.action_time)
#    print (l.get_edited_object())






# score_dict = ScoreDict.objects.get(tournament=t)
# print (score_dict)
# score = manual_score.Score(score_dict.data, t)
# print (score.optimal_picks())

# exit()

# for key in pk_list:#pk_list[-15:]:
#     t = Tournament.objects.get(pk=key)
#     print (t)
#     min_list = []
#     max_list = []
#     for f6 in Field.objects.filter(tournament=t, group__number__gte=6):
#         min_list.append(f6.handicap())


#     f.write('handicap range in group 6: ', min(min_list), max(min_list))
#     handicap = 0

    


#     h_dict = {}
#     for u in users:
#         user_o = User.objects.get(pk=u.get('user'))
#         handicap = 0
#         for sd in ScoreDetails.objects.filter(pick__playerName__tournament=t, user=user_o):
#                 handicap = handicap + sd.pick.playerName.handicap()
#         score = TotalScore.objects.get(tournament=t, user=sd.user)
#         #print (score)
#         h_dict[user_o.username] = handicap, score.score, score.score - handicap


#     sorted_h = sorted(h_dict.items(), key=lambda x: x[1][2])

#     for k in sorted_h:
#         f.write(k)
#         print (str(k))

# f.close()



#for golfer in Field.objects.filter(tournament=t):
#    print (golfer, 'owgr: ', golfer.currentWGR, ',  ', golfer.handicap())