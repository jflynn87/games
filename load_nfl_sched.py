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
    current_week = Week.objects.get(current=True)
    week_cnt = current_week.week + 1
    season = Season.objects.get(current=True)
    while week_cnt < 22:
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

                if week_cnt > 17:
                    url_week = 'post' + str(week_cnt - 17)
                else:
                    url_week = 'reg' + str(week_cnt)


                #url = "https://www.nfl.com/schedules/2020/" + str(week_cnt) + "/"
                url = "https://www.nfl.com/schedules/2020/" + url_week + "/"
                print (url)

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
                    date_t = section.find_element_by_class_name('d3-o-section-title').text.split(',')[1].lstrip()
                    month = date_t.split(' ')[0]
                    day = date_t.split(' ')[1].strip('TH').strip('ND').strip('ST').strip('RD')
                    game_dow = section.find_element_by_class_name('d3-o-section-title').text.split(',')[0]
                    #fix the year for Jan games
                    print ('month', month, len(month))
                    if month in ['JANUARY', 'FEBRUARY']:
                        year = int(season.season) + 1
                    else:
                        year = season.season
                    web_game_date = (str(month) + ' ' + str(day) + ', ' + str(year))

                    for game_info in section.find_elements_by_class_name('nfl-c-matchup-strip__left-area'):
                        teams = game_info.find_elements_by_class_name('nfl-c-matchup-strip__team-fullname')
                        
                        away = Teams.objects.get(long_name=(teams[0].get_attribute('innerHTML').lstrip().rstrip()))
                        home = Teams.objects.get(long_name=(teams[1].get_attribute('innerHTML').lstrip().rstrip()))
                        game_time = game_info.find_element_by_css_selector('p.nfl-c-matchup-strip__date-info')
                        print ('--------------')
                        print (game_time.text)
                        print ('--------------')
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
                        game_time = game_time.text.split(' ')[0] + ' ' + game_time.text.split(' ')[1][:2] 
                        print ('game tiem', game_time)



                        if tz == 'JST':
                            jst = pytz.timezone('Asia/Tokyo')
                            orig_time = jst.localize(datetime.strptime(web_game_date + ' ' + game_time, '%B %d, %Y %I:%M %p'))
                            web_time = orig_time.astimezone(pytz.utc)
                        #elif tz == 'UST':
                        #    ust = pytz.timezone('America/New_York')
                        #    orig_time = ust.localize(datetime.strptime(web_game_date + ' ' + game_time, '%B %d, %Y %H:%M %p'))
                        #    web_time = orig_time.astimezone(pytz.utc)
                        else:
                            print ('in time else')
                            utc = pytz.timezone('UTC')
                            #web_time = datetime.strptime(web_game_date + ' ' + game_time, '%B %d, %Y %H:%M %p')
                            web_time = utc.localize(datetime.strptime(web_game_date + ' ' + game_time, '%B %d, %Y %I:%M %p'))
                        
                        game.game_time = web_time
                        game.day = game_dow
                        game.qtr = 'pregame'

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

