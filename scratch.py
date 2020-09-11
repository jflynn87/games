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
from bs4 import BeautifulSoup

#try:

games_dict = {}

html = urllib.request.urlopen("https://nypost.com/sports/")
soup = BeautifulSoup(html, 'html.parser')

score_board = (soup.find("div", {'class':'widget_nypost_scoreboard_widget'}))

nfl_sect = (soup.find("div", {'id':'MLB'}))

games = (nfl_sect.find_all("div", {'class': 'sport-score'}))

for row in games:
    #print ('-------------------------------------------')
    print (row)
    teams = row.find_all("div", {"class": "sport-score-team"})
    scores = row.find_all('div', {'class': 'sport-score-total'})
    for t in teams:
        print ('row', t)
        if 'home' in t.get('class'):
            home = t.text
            #print (row.get("div", {"class": "sport-score-total home"}))
            #home_score = row.find("div", {"class": "sport-score-total home"}).text
            #print (home, home_score)
        elif 'visiting' in t.get('class'):
            away = t.text
            #print (row.find("div", {"class": "sport-score-total visiting"}))
            #away_score = row.find("div", {"class": "sport-score-total visiting"})
        else:
            print ('score data issue?', t) 
    for s in scores:
        print ('score', s)
        if 'home' in s.get('class'):
            home_score = s.text
        elif 'visiting' in s.get('class'):
            away_score = s.text
        else:
            print ('score data issue?', s) 
    qtr = row.find("div", {"class": "sport-score-status"}).text

    games_dict[home+away] = {'home': home, 'away': away, 'qtr': qtr, 'home_score': home_score, 'away_score': away_score}


print (games_dict)

#print (nfl_sect)

exit()

try:
    url = "https://www.nfl.com/scores/2019/REG1"

    game_dict = {}
    options = ChromeOptions()
    #options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = Chrome(options=options)
        
    driver.get(url)
    #sleep.sleep(10)
    #g = driver.find_elements_by_class_name("nfl-c-matchup-strip__left-area")
    main = driver.find_element_by_class_name("css-37urdo")
    print ('main', type(main))
    #data = main.find_elements_by_class_name('css-view-1dbjc4n')
    data = main.find_elements_by_xpath('//*[@id="main-content"]/div/div[2]/div/div[2]/div/div/div[1]/div[2]/div[3]/div[3]/div/div/div/div/div[1]/div[1]/div/div[1]/div[1]/div[2]/div')

    print (type(data), len(data))

    for d in data:
        print ('d', type(d))

except Exception as e:
    print ('exception with scrape', e)
finally:
    driver.quit()

exit()




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


