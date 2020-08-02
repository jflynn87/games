#import os
#os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

from golf_app.models import Tournament, TotalScore, ScoreDetails, Field, Picks, PickMethod, BonusDetails
from django.contrib.auth.models import User
from datetime import datetime, timedelta

from django.db.models import Min, Q, Count, Sum, Max
from requests import get
from selenium import webdriver
import urllib
from selenium.webdriver import Chrome, ChromeOptions
import json




class ScrapeScores(object):

    def __init__(self, tournament, url=None):
        self.tournament = tournament
        if url != None:
            self.url = url
        elif self.tournament.current:
            self.url = "https://www.pgatour.com/leaderboard.html"
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
            name = driver.find_elements_by_class_name("name")
            for n in name:
                if n.text == t.name:
                    print ('name', n.text)
                    t_ok = True
        
            if t_ok:
                cut_line = driver.find_elements_by_class_name("cut-line")
                for c in cut_line:
                    print ('cut update', c.text)
                    t.cut_score = c.text
                    t.save()

                #find playoff data
                playoff = driver.find_elements_by_class_name("playoff-module")
                print ('-------playoff--------')
                for p in playoff:
                    print (p.text)



                table = driver.find_elements_by_class_name("leaderboard-table")
                
                print (table)
                for t in table[1:]:
                    for tr in t.find_elements_by_tag_name('tr'):
                        #print(tr.text, 'len: ', len(tr.text))
                        if len(tr.find_elements_by_tag_name('td')) > 5:
                            row = tr.find_elements_by_tag_name('td')
                            for e in row[2].find_elements_by_class_name('position-movement'): c = e.get_attribute('innerHTML')
                            n = row[3].text.split('(')[0].split(',')[0]
                            if n[-1] == ' ':
                                n = n[:-1]
                            score_dict[n] =  {'rank': row[1].text, 'change': c, \
                                 'thru': row[5].text, 'round_score': row[6].text, 'total_score': row[4].text, 'r1': row[7].text, 'r2': row[8].text, 'r3': row[9].text, 'r4': row[10].text}
                #print ('scrape scores dict', score_dict)
                f = open("score_dict.json", "w")
                f.write(json.dumps(score_dict))
                f.close()
                
                return (score_dict)                
            else:
                print ('scrape scores t mismatch', t)
                return {}
        
        except Exception as e:
            print (e)
            return {}

        finally:
            driver.quit()



