import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from fb_app.models import Games, Week, Teams, Season
from django.db.models import Count
import urllib3
from bs4 import BeautifulSoup
#import urllib.request
import requests
from datetime import datetime, timezone
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytz



def load_sched(year):

    #changing weeks to load preseason weeks (make week 0 and cnt 1)
    season = Season.objects.get(current=True)
    if Week.objects.filter(current=True).exists():
        current_week = Week.objects.get(current=True)
        week_cnt = current_week.week + 1
    elif Week.objects.filter(season_model=season).exists():  #figure out if this is best way , especially for playoffs
        w = Week.objects.filter(season_model=season).last()
        week_cnt = w.week + 1
    else:
        week_cnt = 1
    
    #week_cnt = current_week.week + 1
    
    while week_cnt < 20:
            try:
                week, created = Week.objects.get_or_create(season_model=season, week=week_cnt)
                #week.season = season.season
                if not week.current and week.week != 1:
                    week.current = False
                else:
                    week.current = True
                week.season = season.season
                #week.week = week_cnt
                week.game_cnt = 0
                week.save()

                #if week_cnt > 17:
                #    url_week = 'post' + str(week_cnt - 17)
                #else:
                #    url_week = 'reg' + str(week_cnt)

                headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
                url = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
                
                if week.week < 19:
                
                    payload = {'week': str(week_cnt)}
                    print ('payload ', payload)
                    #payload = {}  #works for pre season/current week?
                else:
                    payload = {}  #works for preseason and post season
                json_data = requests.get(url, headers=headers, params=payload).json()
                print (json_data)
                print (json_data.keys())
                print ('espn week: ', json_data.get('week'))
                for l in json_data.get('events'):
                    print (l.get('name'))
                    for competition in l.get('competitions'):
                        for c in competition.get('competitors'):
                            print (c.get('homeAway'), c.get('team').get('name'))
                            if c.get('team').get('name'):
                                t_name = c.get('team').get('name')
                            elif c.get('team').get('displayName') == "Washington":
                                t_name = "Football Team"
                            else:
                                raise Exception('uknown team: ', c.get('team'))                        
                                
                            if c.get('homeAway') == 'home':
                                home = Teams.objects.get(long_name=t_name)
                            elif c.get('homeAway') == "away":
                                away = Teams.objects.get(long_name=t_name)
                            else:
                                raise Exception('uknown value in home/away: ', c.get('homeAway'))                        

                        #game_time = competition.get('date')

                        game, created = Games.objects.get_or_create(week=week, home=home, away=away)
                        game.week = week
                        game.eid = competition.get('id')
                        game.away = away
                        game.home = home
                        #game_time = competition.get('date')
                        #print ('game tiem', game_time)

                        game.game_time = competition.get('date')
                        #game.day = game_dow
                        game.qtr = 'pregame'

                        game.save()

                week.game_cnt = Games.objects.filter(week=week).count()
                week.save()
                
            except Exception as e:
                print ('exception with scrape', e)
            finally:
                week_cnt +=1
            #    driver.quit()

if __name__ == '__main__':
    print ('populating script!')
    #clean_db()
    load_sched(2021)
    print ("Populating Complete!")
    #curr_week = Week.objects.get(current=True)
    #print (Games.objects.filter(week__season_model__current=True, week__week__gt=curr_week.week).values('week__week').annotate(Count('week')))
    print (Games.objects.filter(week__season_model__current=True).values('week__week').annotate(Count('week')))

