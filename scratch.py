import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
#from golf_app.models import Tournament, TotalScore, ScoreDetails, Field, Picks, PickMethod
from fb_app.models import Season, Week, Games, Teams, Picks, League, Player, calc_scores, MikeScore, WeekScore
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import sqlite3
from django.db.models import Min, Q, Count, Sum, Max
from django.db.models.functions import ExtractWeek, ExtractYear
import time
#from f_app import populateField
import urllib
from urllib import request
import json
from fb_app.scores import Scores
#from requests import get
#from random import randint
import sys
import nflgame
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
import requests
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

# #line_bot_api = LineBotApi('1SNDGPl6v0qGjmpYAJCltd9ZKp8E1fH7oMptv6zbeDO')
# line_bot_api = LineBotApi('rxzGYUly9D/SXfvPDbMF96HmQ+mfWPldanfcNefi5QYFZyWXqb2gUw0Z7XcvKL0V+vt9zqFVA1mT3UhlUgyIn+pHjDMlEZYn9oWmW5gU/wBdu7N65dN3lPl/5yPjUluOv2nxiqbK7DF2o1RWjR+HfAdB04t89/1O/w1cDnyilFU=')
# #line_bot_api = LineBotApi('27c068c78541d986c8499b92d2096f6a')



# try:
#     line_bot_api.push_message('U35c3031e4ee32db1c1b19690935b1d4c', TextSendMessage(text='disregard, just John trying something'))
#     profile = line_bot_api.get_profile('U35c3031e4ee32db1c1b19690935b1d4c')
    
#     print (profile)
# except LineBotApiError as e:
#     print (e)


# URL = 'https://notify-api.line.me/api/notify'

# def send_message(token, msg):
#     headers = {'Authorization': 'Bearer ' + token}
#     payload = {'message': msg}
#     r = requests.post(URL, headers=headers, params=payload)
#     return r.status_code

# def main():
#     import sys
#     import argparse

#     token = '1SNDGPl6v0qGjmpYAJCltd9ZKp8E1fH7oMptv6zbeDO'
#     parser = argparse.ArgumentParser(description='This is a test message, does it work?')
#     parser.add_argument('--message')
#     args = parser.parse_args()
#     print (args.message)
#     print ('main')
#     status_code = send_message(token, args.message)
#     print ('status_code = {}'.format(status_code))

# if __name__ == '__main__':
#     main()

print (nflgames.games(2020, week=1))
