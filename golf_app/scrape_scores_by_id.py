#import os
#os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

from golf_app.models import Tournament, TotalScore, ScoreDetails, Field, Picks, PickMethod, BonusDetails, ScoreDict
from django.contrib.auth.models import User
from datetime import datetime, timedelta

from django.db.models import Min, Q, Count, Sum, Max
from requests import get
from selenium import webdriver
import urllib
from selenium.webdriver import Chrome, ChromeOptions
import json
from golf_app import calc_score
from bs4 import BeautifulSoup




class ScrapeScores(object):

    def __init__(self, tournament, url=None):
        self.tournament = tournament
        if url != None:
            self.url = url
        elif self.tournament.current:
            self.url = "https://www.pgatour.com/leaderboard.html"
            #self.url = "https://www.pgatour.com/competition/2020/sentry-tournament-of-champions/leaderboard.html"
        else:
            t_name = self.tournament.name.replace(' ', '-').lower()
            self.url = "https://www.pgatour.com/competition/2020/" + t_name + "/leaderboard.html"
        print (self.url)


    def scrape(self):
        score_dict = {}
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        driver = Chrome(options=options)
      
        driver.get(self.url)
        t = self.tournament
        t_ok = False
        
        try:
            field = []
            name = driver.find_element_by_id("stroke-play-container")
                
            for row in name.find_elements_by_class_name('line-row'):
                
                #print ('pos', row.find_element_by_class_name('position').text)
                field.append(row.text)

            print (field)
            
        
        except Exception as e:
            print (e)
            return {}

        finally:
            driver.quit()



