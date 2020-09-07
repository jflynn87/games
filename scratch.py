import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
#from golf_app.models import Tournament, TotalScore, ScoreDetails, Field, Picks, PickMethod
from fb_app.models import Season, Week, Games, Teams, Picks, League, Player, calc_scores, MikeScore, WeekScore
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.db.models import Min, Q, Count, Sum, Max
from django.db.models.functions import ExtractWeek, ExtractYear
import time
import urllib
from urllib import request
import json
#from fb_app.scores import Scores
#from urllib.request import Request, urlopen
from selenium.webdriver import Chrome, ChromeOptions
#

#
import requests
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError


for game in Games.objects.filter(week__season_model__current=True):
    print (game.date)

exit()

try:
    url = "https://www.nfl.com/schedules/2020/reg15/"

    game_dict = {}
    options = ChromeOptions()
    #options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = Chrome(options=options)
        
    driver.get(url)
    name = driver.find_elements_by_class_name("nfl-c-matchup-strip")
                
    for n in name:
        print ('name', n.text)
except Exception as e:
    print ('exception', e)
finally:
    driver.quit()


