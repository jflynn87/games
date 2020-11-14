from golf_app.models import Picks, ScoreDict, Field, Golfer
#from django.contrib.auth.models import User
from datetime import datetime, timedelta

#from django.db.models import Min, Q, Count, Sum, Max
from requests import get
from selenium import webdriver
import urllib
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import json
from golf_app import utils
from bs4 import BeautifulSoup
import time



class ScrapeScores(object):

    def __init__(self, tournament):
        self.tournament = tournament
        self.url = "https://www.masters.com/en_US/scores/index.html"
        print (self.url)

    def scrape(self):
        start = datetime.now()

        score_dict = {}
        options = ChromeOptions()
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'

        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument(f'user-agent={user_agent}')

        driver = Chrome(options=options)

        print ('driver pre url: ', datetime.now() - start)
        driver.get(self.url)
        print ('driver after url: ', datetime.now() - start)
        
        #soup = BeautifulSoup(driver.page_source, 'html.parser')
        try:
            #print (driver.page_source)
            lb = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "leaderBoardPlayersTraditionalContent")))
            print ('a')
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            print ('b')
            table = (soup.find("div", {'id':'leaderBoardPlayersTraditionalContent'}))
            print ('c')
            leaderboard = soup.find('div', {'id': 'leaderBoardPlayersTraditionalContent'})
            player_rows = soup.find_all('div', {'class': 'playerRow'})            
            
            score_dict = {}

            for row in player_rows:
                masters_name = row.find('div', {'class': 'playerName'}).find('div', {'class': 'data'}).text
                for c in row['class']:
                    if c[:2] == 'pr':
                        player_num = c[2:]
                    else:
                        pass
                
                try:

                    try:
                        golfer = Golfer.objects.get(golfer_pga_num=player_num)
                        field = Field.objects.get(tournament=self.tournament, golfer=golfer)
                        player_name = field.playerName
                    except Exception:
                        if Field.objects.filter(tournament=self.tournament, playerName__contains=masters_name.split(',')[0].split(' ')[0].capitalize()).exists():
                            o = Field.objects.get(tournament=self.tournament, playerName__contains=masters_name.split(',')[0].split(' ')[0].capitalize())
                            player_name = o.playerName
                        else:
                            print ('cant find player', masters_player)
                    stats = row.find('div', {'class': 'playerStatContainer'})
                    
                        
                    pos = row.find('div', {'class': 'pos'}).find('div', {'class': 'data'}).text

                    if pos != "WD":

                        total = row.find('div', {'class': 'playerStatContainer'}).find('div', {'attr': 'topar'}).find('div', {'class': 'data'}).text
                        today = row.find('div', {'class': 'playerStatContainer'}).find('div', {'attr': 'today3'}).find('div', {'class': 'data'}).text
                        thru = row.find('div', {'class': 'playerStatContainer'}).find('div', {'class': 'thru'}).find('div', {'class': 'data'}).text
                        r1 = row.find('div', {'class': 'playerStatContainer'}).find('div', {'class': 'r1'}).find('div', {'class': 'data'}).text
                        if r1 == '':
                            r1 = '--'
                        r2 = row.find('div', {'class': 'playerStatContainer'}).find('div', {'class': 'r2'}).find('div', {'class': 'data'}).text
                        if r2 == '':
                            r2 = '--'

                        r3 = row.find('div', {'class': 'playerStatContainer'}).find('div', {'class': 'r3'}).find('div', {'class': 'data'}).text
                        if r3 == '':
                            r3 = '--'

                        r4 = row.find('div', {'class': 'playerStatContainer'}).find('div', {'class': 'r4'}).find('div', {'class': 'data'}).text
                        if r4 == '':
                            r4 = '--'
                    else:
                        total = ''
                        today = ''
                        thru = ''
                        r1 = row.find('div', {'class': 'playerStatContainer'}).find('div', {'class': 'r1'}).find('div', {'class': 'data'}).text
                        if r1 == '':
                            r1 = '--'
                        r2 = row.find('div', {'class': 'playerStatContainer'}).find('div', {'class': 'r2'}).find('div', {'class': 'data'}).text
                        if r2 == '':
                            r2 = '--'

                        r3 = row.find('div', {'class': 'playerStatContainer'}).find('div', {'class': 'r3'}).find('div', {'class': 'data'}).text
                        if r3 == '':
                            r3 = '--'

                        r4 = row.find('div', {'class': 'playerStatContainer'}).find('div', {'class': 'r4'}).find('div', {'class': 'data'}).text
                        if r4 == '':
                            r4 = '--'
                        


                    score_dict[player_name] = {
                        'rank': pos, 'change': 'n/a', \
                        'thru': thru, 'round_score': today, 'total_score': total , 'r1': r1, 'r2': r2, 'r3': r3, 'r4': r4
                    }

                        
                except Exception as e:
                    print ('row execptino', e)
            
            cut_num = len([x for x in score_dict.values() if int(utils.formatRank(x['rank'])) <= 50 and x['rank'] not in self.tournament.not_playing_list()]) + 1 
            cut_score = [x for x in score_dict.values() if int(utils.formatRank(x['rank'])) <= 50 and x['rank'] not in self.tournament.not_playing_list()]) + 1 
            self.tournament.cut_score = 'Cut Number ' + str(cut)
            self.tournament.save()

            return (score_dict)
                



        except Exception as e:
            print ('scrape issues', e)


#         print ('driver after soup: ', datetime.now() - start)
# #        time.sleep(10)
#         #print ('driver after table: ', datetime.now() - start)
#         print ('driver initialized: ', datetime.now() - start)
                
#             #find playoff data
#             playoff = driver.find_elements_by_class_name("playoff-module")
#             print (t.name, '-------playoff--------')
#             print ('length', len(playoff))
#             for p in playoff:
#                 print (p.text)
#             print (t.name, '-------end playoff------')

#             if len(playoff) > 0:
#                 t.playoff = True

#             #table = driver.find_element_by_id("stroke-play-container")
            
#             sd, created = ScoreDict.objects.get_or_create(tournament=self.tournament)                
            
#             if self.mode == 'picks':
#                 for pick in Picks.objects.filter(playerName__tournament=self.tournament).values('playerName__playerID').distinct():
#                     row =  table.find("tr", {'class': 'line-row-' + str(pick.get('playerName__playerID'))})
#                     data = get_data(self, row)
#                     data[1].update({'pga_num': pick.playerID})
#                     score_dict[data[0]] =  data[1]
#                 #sd.pick_data = score_dict
#             else:  #doing for "all" or None 
#                 for row in table.find_all("tr", {'class': 'line-row'}):
#                     ele_class = row['class'][1].split('-')[2]
#                     #print (ele_class, ele_class)
#                     data = self.get_data(row)
#                     data[1].update({'pga_num': ele_class})
#                     score_dict[data[0]] =  data[1]
#                 sd.data = score_dict
#                 print (len(sd.data))
            
#             sd.save()
#             #print (score_dict)
#             #self.tournament.saved_cut_num = self.tournament.cut_num()
#             #self.tournament.saved_round = self.tournament.get_round()
#             #self.tournament.saved_cut_round = self.tournament.get_cut_round() 
#             #self.tournament.save()

#             return (score_dict)                
        
#         except Exception as e:
#             print (e)
#             return {}

#         finally:
#             driver.quit()

#     def get_data(self, row):

            
#             #print (row)
#             n = row.find('td', {'class': 'player-name'}).text
#             if n[-1] == ' ':
#                 n = n[:-1]
            
#             rank = row.find('td', {'class': 'position'}).text 
#             pos = row.find('td', {'class': 'position-movement'})
            
#             movement = pos.find('div', {'class': 'position-movement'})

#             try:
#                 if movement.span != None:
#                     c= str(movement.span) + movement.text
#                 else:
#                     c= movement.text
#             except Exception as e:
#                 c = '--'
#                 print ('cant scrape poasition move span')
#             if row.find('td', {'class': 'thru'}) != None:
#                 thru = row.find('td', {'class': 'thru'}).text 
#                 round_score = row.find('td', {'class': 'round'}).text 
#             elif row.find('td', {'class': 'tee-time'}) != None: 
#                 thru = row.find('td', {'class': 'tee-time'}).text
#                 round_score = 'E'
#             else: 
#                 thru = "no info"
#                 round_score = 'E'

#             total_score = row.find('td', {'class': 'total'}).text 

#             if total_score == 'E':
#                 total_score = '0'
            
#             round_list = []
#             for i in range(len(row.find_all('td', {'class': 'round-x'}))):
#                 round_list.append(row.find_all('td', {'class': 'round-x'})[i].text)

#             return (n, {'rank': rank, 'change': c, \
#                 'thru': thru, 'round_score': round_score, 'total_score': total_score , 'r1': round_list[0], 'r2': round_list[1], 'r3': round_list[2], 'r4': round_list[3]})

        


