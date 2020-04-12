import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
#from golf_app.models import Tournament, TotalScore, ScoreDetails, Field, Picks, PickMethod
#from fb_app.models import Season, Week, Games, Teams, Picks, League, Player, calc_scores, MikeScore, WeekScore
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import sqlite3
from django.db.models import Min, Q, Count, Sum, Max
from django.db.models.functions import ExtractWeek, ExtractYear
import time
from golf_app import populateField
import urllib
from urllib import request
import json
from fb_app.scores import Scores
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

f =  open('gs_stock.txt', 'r')
d = {}
for line in f:
    date = line[1:].split('$')[0].split('Us')[1][1:]
    d[date] = line.split('$')[1].split(' ')[0], \
    line.split('$')[1].split(' ')[1], \
    line.split('$')[1].split(' ')[2], \
    line.split('$')[1].split(' ')[3]

    print(date, ',', line.split('$')[1].split(' ')[0], ',', line.split('$')[1].split(' ')[1], ',', line.split('$')[1].split(' ')[2], ',', line.split('$')[1].split(' ')[3])

print (d)