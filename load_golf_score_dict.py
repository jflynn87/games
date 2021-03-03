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
from golf_app import views, manual_score, populateField, withdraw, scrape_scores_picks, utils, scrape_cbs_golf, scrape_masters, scrape_espn
from unidecode import unidecode
from django.core import serializers
from golf_app.utils import formatRank, format_name, fix_name


t= Tournament.objects.get(pga_tournament_num='009', season__season='2020')
print (Field.objects.filter(tournament=t).count())

web = scrape_espn.ScrapeESPN(t, 'https://www.espn.com/golf/leaderboard?tournamentId=401155427').get_data()
#print (web)

sd, created = ScoreDict.objects.get_or_create(tournament=t)

#sd.tournament = t
sd.data = web
sd.save()


exit()
