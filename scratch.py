import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from golf_app.models import Tournament, TotalScore, ScoreDetails, Field, Picks, PickMethod
#from fb_app.models import Season, Week, Games, Teams, Picks, League, Player, calc_scores, MikeScore, WeekScore
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import sqlite3
from django.db.models import Min, Q, Count, Sum, Max
from django.db.models.functions import ExtractWeek, ExtractYear
import time
from golf_app import populateField
#from requests import get
#from random import randint
import sys
# pip install PyQt5 and PyQtWebEngine
#from PyQt5.QtWidgets import QApplication, QWidget
#from PyQt5.QtCore import QUrl
#from PyQt5.QtWebEngineWidgets import QWebPage
#from PyQt5.QtWebEngine import QtWebEngine as QWebPage

#from PyQt5.QtWebEngineWidgets import QWebEngineView
#from bs4 import BeautifulSoup
#from urllib.request import Request, urlopen
#from selenium import webdriver
#

#

def check():
    p = Player.objects.get(name=User.objects.get(username='milt'))
    for s in MikeScore.objects.filter(week__season_model__current=True, player=p):
        print (s)
    
def picks():
    week = Week.objects.get(current=True)
    player = Player.objects.get(name=User.objects.get(username="JoeLong"))

    print(week, player)
    Picks.objects.filter(week=week, player=player).delete()
    print(Picks.objects.filter(week=week, player=player))

    pick_num = 16
    pick_list = ['LAC', 'LA', 'BAL', 'NE', 'IND', 'KC', 'SEA', 'GB', 'ATL', 'HOU', 'PIT', 'DAL', 'MIN', 'JAC', 'WAS']

    for p in pick_list:
        pick = Picks()
        pick.week = week
        pick.player = player
        pick.pick_num = pick_num
        pick.team = Teams.objects.get(nfl_abbr = p)
        pick.save()
        pick_num -= 1

    print (Picks.objects.filter(week=week, player=player))

    
   
def weeks():
    for week in Week.objects.all():
        print (week.season, week, week.pk)

def count():
    curr_week = Week.objects.get(current=True)
    print (Games.objects.filter(week__season_model__current=True, week__week__gt=curr_week.week).values('week__week').annotate(Count('week')))

def recalc(league):
    '''compares my scores to mike's scores'''
    l = League.objects.get(league=league)
    season = Season.objects.get(current=True)
    c_week = Week.objects.get(current=True)
    good_list = []
    bad_list = []
    
    for player in Player.objects.filter(league=l, active=True):
        user=User.objects.get(username=player.name)
        l_week = Week.objects.get(week=c_week.week-1, season_model__current=True)
        ms = MikeScore.objects.get(player__name=user, week=l_week)
        js = WeekScore.objects.filter(Q(player=player) & (Q(week__season_model__current=True) & Q(week__current=False))).aggregate(Sum('score'))
        #print (player, ms.total, js.get('score__sum'))
        if ms.total == js.get('score__sum'):
            good_list.append(player)
        else:
            w = Week.objects.get(season_model__current=True, week=1)
            while w.week < c_week.week:
                m_score = MikeScore.objects.get(week=w, player=player)
                #j_score = WeekScore.objects.get(week=w, player=player)
                j_score = WeekScore.objects.filter(Q(player=player) & (Q(week__season_model__current=True) & Q(week__week__lte=w.week))).aggregate(Sum('score'))
                if m_score.total != j_score.get('score__sum'):
                    print (player, w, 'mike', m_score.total, 'john', j_score.get('score__sum'))
                w = Week.objects.get(season_model__current=True, week=w.week+1)

    print (len(good_list))
    print (bad_list)
    


#check()
#picks()
#weeks()
#count()
#recalc('Football Fools')
populateField.create_groups(457)