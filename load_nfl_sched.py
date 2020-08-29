import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from fb_app.models import Games, Week, Teams, Season
from django.db.models import Count
import urllib3
from bs4 import BeautifulSoup
import urllib.request
from datetime import datetime
from selenium.webdriver import Chrome, ChromeOptions



def load_sched(year):

    #changing weeks to load preseason weeks (make week 0 and cnt 1)
    week_cnt = 1
    season = Season.objects.get(current=True)
    while week_cnt < 2:
        try:
            #html = urllib.request.urlopen("http://www.nfl.com/ajax/scorestrip?season=2019&seasonType=PRE&week=4")
            html = urllib.request.urlopen("http://www.nfl.com/ajax/scorestrip?season=" + str(year) + "&seasonType=REG&week=" + str(week_cnt))
            soup = BeautifulSoup(html, 'html.parser')


            week = Week()
            week.season = soup.find('gms').attrs['y']
            week.week = soup.find('gms').attrs['w']
            #week.week = 0
            week.game_cnt = gm_cnt = len(soup.findAll('g'))
            week.current = False
            #week.current = True
            week.season_model = season
            week.save()

            for NFLgame in soup.findAll('g'):

                game=Games()

                game.week = week
                game.eid = NFLgame.attrs['eid']
                try:
                    game.home = Teams.objects.get(nfl_abbr=NFLgame.attrs['h'])
                except Exception:
                    game.home = Teams.objects.get(mike_abbr=NFLgame.attrs['h'])

                try:
                    game.away = Teams.objects.get(nfl_abbr=NFLgame.attrs['v'])
                except Exception:
                    game.away = Teams.objects.get(mike_abbr=NFLgame.attrs['v'])

                date = NFLgame.attrs['eid'][0:4] + '-' + NFLgame.attrs['eid'][4:6] + '-' + NFLgame.attrs['eid'][6:8]

                game.date = datetime.strptime(date, '%Y-%m-%d')
                game.time = NFLgame.attrs['t']
                game.day = NFLgame.attrs['d']

                print (game.home, game.away)
                game.save()

            week_cnt +=1
        except Exception as e:
            print ('exception with nfl json', e)
                
            try:
                url = "https://www.nfl.com/schedules/2020/reg" + str(week_cnt) + "/"

                game_dict = {}
                options = ChromeOptions()
                #options.add_argument("--headless")
                options.add_argument("--disable-gpu")
                driver = Chrome(options=options)
                    
                driver.get(url)
                game = driver.find_elements_by_class_name("nfl-c-matchup-strip")
                            
                for data in game:
                    print ('--------------------------')
                    teams = data.find_elements_by_class_name('nfl-c-matchup-strip__team-fullname')
                    away = teams[0].text
                    home = teams[1].text
                    print (Teams.objects.get(long_name=away))
                    print (Teams.objects.get(long_name=home))
                    time = data.find_elements_by_class_name('nfl-c-matchup-strip__date-time')
                    for t in time:
                        print ('x', t.text)

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
    curr_week = Week.objects.get(current=True)
    print (Games.objects.filter(week__season_model__current=True, week__week__gt=curr_week.week).values('week__week').annotate(Count('week')))

