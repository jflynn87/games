import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from fb_app.models import Games, Week, Teams, Season
from django.db.models import Count
import urllib3
from bs4 import BeautifulSoup
import urllib.request
from datetime import datetime, timezone
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytz



def load_sched(year):

    #changing weeks to load preseason weeks (make week 0 and cnt 1)
    week_cnt = 3
    season = Season.objects.get(current=True)
    while week_cnt < 4:
            try:
                week, created = Week.objects.get_or_create(season_model=season, week=week_cnt)
                #week.season = season.season
                if not week.current:
                    week.current = False
                #week.current = True
                week.season = season.season
                #week.week = week_cnt
                week.game_cnt = 0
                week.save()

                url = "https://www.nfl.com/schedules/2020/reg" + str(week_cnt) + "/"

                game_dict = {}
                options = ChromeOptions()
                options.add_argument("--headless")
                options.add_argument("--disable-gpu")
                driver = Chrome(options=options)
                    
                driver.get(url)
                #sleep.sleep(10)
                #g = driver.find_elements_by_class_name("nfl-c-matchup-strip__left-area")
                main = driver.find_element_by_id("main-content")
                for section in main.find_elements_by_class_name('nfl-o-matchup-group'):
                    date_t = section.find_element_by_class_name('d3-o-section-title').text.split(',')[1]
                    month = date_t.split(' ')[1]
                    day = date_t.split(' ')[2].strip('TH').strip('ND').strip('ST').strip('RD')
                    game_dow = section.find_element_by_class_name('d3-o-section-title').text.split(',')[0]
                    web_game_date = (str(month) + ' ' + str(day) + ', ' + str(season.season))

                    for game_info in section.find_elements_by_class_name('nfl-c-matchup-strip__left-area'):
                        teams = game_info.find_elements_by_class_name('nfl-c-matchup-strip__team-fullname')
                        
                        away = Teams.objects.get(long_name=(teams[0].get_attribute('innerHTML').lstrip().rstrip()))
                        home = Teams.objects.get(long_name=(teams[1].get_attribute('innerHTML').lstrip().rstrip()))
                        game_time = game_info.find_element_by_css_selector('p.nfl-c-matchup-strip__date-info')
                        #tz = game_info.find_element_by_class_name('nfl-c-matchup-strip__date=timezone')
                        print ('GI', game_info.text.split(' ')[1][3:])
                        print ('GI', game_info.text.split(' ')[2])
                        print ('GI', game_info.text.split(' ')[3])
                        tz = game_time.text.split(' ')[1][3] + game_time.text.split(' ')[2][0] + game_time.text.split(' ')[3][0]
                        print ('tz', tz)
                        
                        print ('teams ', home, away)
                        #print (len(game_time.text), game_time.text)

                        game, created = Games.objects.get_or_create(week=week, home=home, away=away)
                        game.week = week
                        game.eid = str (season.season) + str(week) + str(home) + str(away)
                        game.away = away
                        game.home = home
                        game_time = str(game_time.text.split(' ')[0] + ' ' + game_time.text.split(' ')[1][:2]) 
                        print ('game tiem', game_time)

                        if tz == 'JST':
                            diff = '+00:00'
                        else:
                            diff = '+00:00'
                        web_time = datetime.strptime(web_game_date + ' ' + game_time + ' ' + diff, '%B %d, %Y %H:%M %p %z')
                        game.game_time = web_time
                        game.day = game_dow

                        game.save()

                week.game_cnt = Games.objects.filter(week=week).count()
                week.save()
                
            except Exception as e:
                print ('exception with scrape', e)
            finally:
                week_cnt +=1
                driver.quit()

if __name__ == '__main__':
    print ('populating script!')
    #clean_db()
    load_sched(2020)
    print ("Populating Complete!")
    #curr_week = Week.objects.get(current=True)
    #print (Games.objects.filter(week__season_model__current=True, week__week__gt=curr_week.week).values('week__week').annotate(Count('week')))
    print (Games.objects.filter(week__season_model__current=True).values('week__week').annotate(Count('week')))

