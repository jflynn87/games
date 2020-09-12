from golf_app.models import Picks, ScoreDict
#from django.contrib.auth.models import User
from datetime import datetime, timedelta

#from django.db.models import Min, Q, Count, Sum, Max
from requests import get
from selenium import webdriver
#import urllib
from selenium.webdriver import Chrome, ChromeOptions
import json
from golf_app import utils




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
            name = driver.find_elements_by_class_name("name")
            for n in name:
                if n.text == t.name:
                    #print ('name', n.text)
                    t_ok = True
        
            if t_ok:
                cut_line = driver.find_elements_by_class_name("cut-line")
                for c in cut_line:
                    cut_score  = c.text.rsplit(' ', 1)[1]
                    #print ('full cutt text: ', c.text, 'cut score: ', c.text.rsplit(' ', 1)[1])
                    if "Projected" in c.text:
                        t.cut_score = "Projected cut score: " + c.text.rsplit(' ', 1)[1]
                        t.save()
                    else:
                        t.cut_score = "Cut Score: " + c.text.rsplit(' ', 1)[1]
                        t.save()
                        

                #find playoff data
                playoff = driver.find_elements_by_class_name("playoff-module")
                print (t.name, '-------playoff--------')
                print ('length', len(playoff))
                for p in playoff:
                    print (p.text)
                print (t.name, '-------end playoff------')

                if len(playoff) > 0:
                    t.playoff = True

                table = driver.find_element_by_id("stroke-play-container")

                for pick in Picks.objects.filter(playerName__tournament=self.tournament).values('playerName__playerID').distinct():
                    print (pick.get('playerName__playerID'))

                    for row in table.find_elements_by_class_name('line-row-' + str(pick.get('playerName__playerID'))):
                        n = row.find_element_by_class_name('player-name-col').text 
                        rank = row.find_element_by_class_name('position').text 
                        for e in row.find_elements_by_class_name('position-movement'): c = e.get_attribute('innerHTML')
                        thru = row.find_element_by_class_name('thru').text 
                        total_score = row.find_element_by_class_name('total').text 
                        round_score = row.find_element_by_class_name('round').text 
                        round_list = []
                        for i in range(len(row.find_elements_by_class_name('round-x'))):
                            round_list.append(row.find_elements_by_class_name('round-x')[i].text)
                        
                        score_dict[n] =  {'rank': rank, 'change': c, \
                                    'thru': thru, 'round_score': round_score, 'total_score': total_score , 'r1': round_list[0], 'r2': round_list[1], 'r3': round_list[2], 'r4': round_list[3]}
                        
                sd, creates = ScoreDict.objects.get_or_create(tournament=self.tournament)
                sd.pick_data = score_dict
                sd.save()
                #f = open("score_dict.json", "w")

                #f.write(json.dumps(score_dict))
                #f.close()
                
                print (score_dict)
                return (score_dict)                
            else:
                print ('scrape scores t mismatch', t, name)
                return {}
        
        except Exception as e:
            print (e)
            return {}

        finally:
            driver.quit()

