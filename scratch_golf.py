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
   

pk_list = []
for t in Tournament.objects.filter(season__current=True):
    pk_list.append(t.pk)


#scrape = scrape_scores.ScrapeScores(t)
#scrape.scrape()

x = 0

for key in pk_list:
    try:
        t = Tournament.objects.get(pk=key)
        name = t.name.replace(' ', '-').lower()
        print ('name', name)
        scrape = scrape_scores.ScrapeScores(t, 'https://www.pgatour.com/competition/2020/' + name + '/leaderboard.html')
        scrape.scrape()
    except Exception as e:
        print ('exceptoin', e)

#for golfer in Field.objects.filter(tournament=t):
#    print (golfer, 'owgr: ', golfer.currentWGR, ',  ', golfer.handicap())