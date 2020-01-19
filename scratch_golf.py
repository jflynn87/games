import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from golf_app.models import Tournament, TotalScore, ScoreDetails, Field, Picks, PickMethod, BonusDetails
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


def get_worldrank():
    '''Goes to OWGR web site takes no input, goes to web to get world golf rankings and returns a dictionary with player name as a string and key, ranking as a string in values'''

    #from bs4 import BeautifulSoup
    #import urllib.request

    html = urllib.request.urlopen("http://www.owgr.com/ranking?pageNo=1&pageSize=All&country=All")
    soup = BeautifulSoup(html, 'html.parser')


    rankslist = (soup.find("div", {'class': 'table_container'}))

    ranks = {}

    c = 0
    for row in rankslist.find_all('tr')[1:]:
        rank_data = row.find_all('td')
        i = 0
        rank_list = []
        for data in rank_data:
            rank_list.append(data.text)
            i += 1
            if i == 3:
                print (rank_list)
                break
        c += 1
        if c == 3:

            break
        try:
            player = (row.find('td', {'class': 'name'}).text).replace('(Am)','').replace(' Jr','').replace('(am)','')
            rank = row.find('td').text
            ranks[player.capitalize()] = int(rank)
        except Exception as e:
            print(e)

    return ranks


#t= Tournament.objects.get(current=True)
#print (t, t.started())
#sd = ScoreDetails.objects.filter(pick__playerName__tournament=t).exclude(Q(score__in=[0, None]) and Q(thru__in=["not started", None, " ", ""])) or Q(today_score="WD")
#for score in sd: #ScoreDetails.objects.filter(pick__playerName__tournament=t):
#    print (score.pick.playerName, score.score, score.thru, score.today_score)

#from golf_app import manual_score
#s = manual_score.Score('006')
#print (len([x for x in s.get_score_file().values() if x['total'] not in ['CUT', 'WD']]))
#print (s.score_dict)
#print (s.update_scores())


#from easyprocess import EasyProcess


# with Display():
#      # we can now start Firefox and it will run inside the virtual display
#      print ('11')
        
#      browser = webdriver.Firefox()

#      print ('22')
# #         # put the rest of our selenium code in a try/finally
# #         # to make sure we always clean up at the end
#      try:
#         browser.get('http://www.google.com')
#         print(browser.title) #this should print "Google"

#      finally:
#         browser.quit()

# # d()

t = Tournament.objects.get(current=True)
print (t.picks_complete())
if t.started() and not t.picks_complete():
    t.missing_picks()

