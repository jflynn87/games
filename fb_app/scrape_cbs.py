#from django.db import models
#from django.contrib.auth.models import User
#from django.conf import settings
#from django.db.models import Q
#from django.core.exceptions import ObjectDoesNotExist

import datetime
#import urllib3
import urllib
import json
#import scipy.stats as ss
#from django.db.models import Q

from bs4 import BeautifulSoup


### before using need to sort out circular ref oof models #####


class ScrapeCBS(object):

    def __init__(self, week):
        self.week = week
        #self.teams


    def get_data(self):
        from fb_app.models import Week, Teams

        print ('scraping CBS com class')

        try:
            game_dict = {}
            week = Week.objects.get(current=True)

            html = urllib.request.urlopen("https://www.cbssports.com/nfl/scoreboard/all/2020/regular/" + str(week.week) + "/")
            #html = urllib.request.urlopen("https://www.cbssports.com/nfl/scoreboard/")
            soup = BeautifulSoup(html, 'html.parser')

            games = soup.find_all('div', {'class': 'single-score-card'})

            for game in games:
                
                teams = game.find_all('a', {'class': 'helper-team-name'})
                scores = game.find_all('td', {'class': 'total-score'})
            
                #print (teams)
                if teams != None and len(teams) == 2:
                #print(teams)
                    away_team = Teams.objects.get(long_name=teams[0].text)
                    home_team = Teams.objects.get(long_name=teams[1].text)
                
                    if len(scores) == 2:
                        away_score = scores[0].text
                        home_score = scores[1].text
                    else:
                        away_score = 0
                        home_score = 0

                    status = game.find('div', {'class': 'game-status'})
                    #print (len(status), type(status), status)
                    if len(status) == 1:
                        qtr = status.text
                    elif len(status) > 1 and 'pregame' in status['class']:
                        qtr = 'pregame'
                    else:
                        #print ('status parse issue ', status)
                        qtr = status.text.lstrip().rstrip()

                
                    #pregame = game.find('div', {'class': 'game-status pregame'})
                    #print ('pregame: ', pregame)
                    #if pregame.text != None: 
                    #    qtr = None
                    #else:
                    #    status = game.find('div', {'class': 'game-status'})
                    #    if status != None:
                    #        qtr = status.text.lstrip().rstrip()

                    game_dict[str(week.season_model.season) + str(week.week) + str(home_team.nfl_abbr) + str(away_team.nfl_abbr)]  = {
                        'home': home_team.nfl_abbr,
                        'home_score': home_score,
                        'away': away_team.nfl_abbr,
                        'away_score': away_score,
                        'qtr': qtr
                    }
            print ('updated data', game_dict)        
            return {'games': game_dict}
        except Exception as e:
            print ('issue scraping CBS', e)
            return {}   



        # print ('scraping CBS com')

        # try:
        #     game_dict = {}
        #     week = Week.objects.get(current=True)

        #     html = urllib.request.urlopen("https://www.cbssports.com/nfl/scoreboard/")
        #     soup = BeautifulSoup(html, 'html.parser')

        #     games = soup.find_all('div', {'class': 'single-score-card'})

        #     for game in games:
        #         teams = game.find_all('a', {'class': 'helper-team-name'})
        #         scores = game.find_all('td', {'class': 'total-score'})
            
        #         if teams != None and len(teams) == 2:
        #         #print(teams)
        #             away_team = Teams.objects.get(long_name=teams[0].text)
        #             home_team = Teams.objects.get(long_name=teams[1].text)
        #         if len(scores) == 2:
        #             away_score = scores[0].text
        #             home_score = scores[1].text
        #         else:
        #             away_score = 0
        #             home_score = 0
                
        #         status = game.find('div', {'class': 'game-status'})
        #         if status != None:
        #             qtr = status.text.lstrip().rstrip()

        #         game_dict[str(week.season_model.season) + str(week.week) + str(home_team.nfl_abbr) + str(away_team.nfl_abbr)]  = {
        #             'home': home_team.nfl_abbr,
        #             'home_score': home_score,
        #             'away': away_team.nfl_abbr,
        #             'away_score': away_score,
        #             'qtr': qtr
        #         }
        #     print ('updated data', game_dict)        
        #     return game_dict
        # except Exception as e:
        #     print ('issue scraping CBS', e)
        #     return {}   
