from golf_app.models import Picks, ScoreDict
#from django.contrib.auth.models import User
from datetime import datetime, timedelta

#from django.db.models import Min, Q, Count, Sum, Max
from requests import get
from selenium import webdriver
import urllib
from selenium.webdriver import Chrome, ChromeOptions
import json
from golf_app import utils
from bs4 import BeautifulSoup



class ScrapeScores(object):

    def __init__(self, tournament, url=None, mode=None):
        self.tournament = tournament
        if url != None:
            self.url = url
        elif self.tournament.current:
            self.url = "https://www.pgatour.com/leaderboard.html"
            #self.url = "https://www.pgatour.com/competition/2021/safeway-open/leaderboard.html"
        else:
            t_name = self.tournament.name.replace(' ', '-').lower()
            self.url = "https://www.pgatour.com/competition/2020/" + t_name + "/leaderboard.html"
        print (self.url)

        if mode == 'picks':
            self.mode = 'picks'
        else:
            self.mode = 'all'


    def scrape(self):

        # try:

        #     html = urllib.request.urlopen(self.url)
        #     soup = BeautifulSoup(html, 'html.parser')

        #     name = soup.find('h1', {'class': 'name'})
        #     print (name.text.replace(' - Leaderboard', '').lstrip().rstrip())
        
        # except Exception as e:
        #     print ('Scrape Error finding Tournament Name', e)

        score_dict = {}
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        driver = Chrome(options=options)
      
        driver.get(self.url)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        table = (soup.find("div", {'id':'stroke-play-container'}))

        t = self.tournament
        t_ok = False
        try:
            title = soup.find('h1', {'class', 'name'})
            name = title.text

            if t.name == name.lstrip().rstrip():
               t_ok = True
            elif t.name == name.replace(' - Leaderboard', '').lstrip().rstrip():
                t_ok = True
            else: 
                print ('scrape name issue', 'db: ', t.name, 'scrape: ', name)
        
            if t_ok:
                try:
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
                except Exception as e:
                    print ('issue scraping cut-info class from pga leaderboard', e)
                    

                #find playoff data
                playoff = driver.find_elements_by_class_name("playoff-module")
                print (t.name, '-------playoff--------')
                print ('length', len(playoff))
                for p in playoff:
                    print (p.text)
                print (t.name, '-------end playoff------')

                if len(playoff) > 0:
                    t.playoff = True

                #table = driver.find_element_by_id("stroke-play-container")
                
                sd, created = ScoreDict.objects.get_or_create(tournament=self.tournament)                
                
                if self.mode == 'picks':
                    for pick in Picks.objects.filter(playerName__tournament=self.tournament).values('playerName__playerID').distinct():
                        row =  table.find("tr", {'class': 'line-row-' + str(pick.get('playerName__playerID'))})
                        data = get_data(self, row)
                        score_dict[data[0]] =  data[1]
                    #sd.pick_data = score_dict
                else:  #doing for "all" or None 
                    for row in table.find_all("tr", {'class': 'line-row'}):
                        data = get_data(self, row)
                        score_dict[data[0]] =  data[1]
                    sd.data = score_dict
                
                sd.save()
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

def get_data(self, row):

        
        #print (row)
        n = row.find('td', {'class': 'player-name'}).text
        if n[-1] == ' ':
            n = n[:-1]
        
        rank = row.find('td', {'class': 'position'}).text 
        pos = row.find('td', {'class': 'position-movement'})
        
        movement = pos.find('div', {'class': 'position-movement'})

        try:
            if movement.span != None:
                c= str(movement.span) + movement.text
            else:
                c= movement.text
        except Exception as e:
            c = '--'
            print ('cant scrape poasition move span')
        if row.find('td', {'class': 'thru'}) != None:
            thru = row.find('td', {'class': 'thru'}).text 
            round_score = row.find('td', {'class': 'round'}).text 
        elif row.find('td', {'class': 'tee-time'}) != None: 
            thru = row.find('td', {'class': 'tee-time'}).text
            round_score = 'E'
        else: 
            thru = "no info"
            round_score = 'E'

        total_score = row.find('td', {'class': 'total'}).text 
        
        round_list = []
        for i in range(len(row.find_all('td', {'class': 'round-x'}))):
            round_list.append(row.find_all('td', {'class': 'round-x'})[i].text)

        return (n, {'rank': rank, 'change': c, \
             'thru': thru, 'round_score': round_score, 'total_score': total_score , 'r1': round_list[0], 'r2': round_list[1], 'r3': round_list[2], 'r4': round_list[3]})

        


