import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from golf_app.models import Tournament, TotalScore, ScoreDetails, Field, Picks, PickMethod, BonusDetails
from django.contrib.auth.models import User
from datetime import datetime, timedelta

from django.db.models import Min, Q, Count, Sum, Max
from requests import get
from selenium import webdriver
import urllib
from selenium.webdriver import Chrome



class ScrapeScores(object):

    def scrape(self):
        driver = Chrome()
        url = "https://www.pgatour.com/leaderboard.html"
        driver.get(url)
        score_dict = {}

        try:
            table = driver.find_elements_by_class_name("leaderboard-table")
            for t in table[1:]:
                for tr in t.find_elements_by_tag_name('tr'):
                    if len(tr.find_elements_by_tag_name('td')) != 4:
                        row = tr.find_elements_by_tag_name('td')
                        score_dict[row[3].text] =  {'total': row[1].text, 'status': row[5].text, 'score': row[4].text, 'r1': row[7].text, 'r2': row[8].text, 'r3': row[9].text, 'r4': row[10].text}
            
            return (score_dict)                

        except Exception as e:
            print (e)

        finally:
            driver.quit()



