import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from golf_app.models import Tournament, TotalScore, ScoreDetails, Field, Picks, PickMethod
#from fb_app.models import Season, Week, Games, Teams, Picks, League, Player
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
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QUrl
#from PyQt5.QtWebEngineWidgets import QWebPage
#from PyQt5.QtWebEngine import QtWebEngine as QWebPage

from PyQt5.QtWebEngineWidgets import QWebEngineView
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from selenium import webdriver
#

#

def check():

    week = Week.objects.get(current=True)

    old_c = 0
    new_c = 0
    for player in Player.objects.filter(league__league="Football Fools"):
        if player.name.username[-4:] == '2018':
            if Picks.objects.filter(player=player, week__season_model__current=True).exists():
                print ('deleting picks', player)
                Picks.objects.filter(player=player, week__season_model__current=True).delete()
            player.active=False
            player.save()
            old_c += 1
        else:
            print ('current', player.name)
            new_c += 1
    print (old_c, new_c)

    #picks = Picks.objects.filter(week=week).values('player__name__username').annotate(count=Count('pick_num'))
    #for p in picks:
    #    print (p)

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
    
    t = Tournament.objects.filter(season__current=True).earliest('pk')
    print (t)
    c=  len(Picks.objects.filter(playerName__tournament=t).values('user').annotate(unum=Count('user')))
    print (c)    

#check()
#picks()
#weeks()
count()