import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from golf_app.models import Tournament, TotalScore, ScoreDetails, Field, Picks, PickMethod
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
import urllib
import json

def check():
    json_url = 'https://www.pgatour.com/players.html'
    html = urllib.request.urlopen("https://www.pgatour.com/players.html")
    soup = BeautifulSoup(html, 'html.parser')


    players =  (soup.find("div", {'class': 'directory-select'}))
    for p in players:
        print (p.find('option'))
        if '08793' in p:
            print (p)



check()
