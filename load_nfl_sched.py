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



def load_sched(year):

    #changing weeks to load preseason weeks (make week 0 and cnt 1)
    week_cnt = 17
    season = Season.objects.get(season=year)
    while week_cnt < 18:
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



if __name__ == '__main__':
    print ('populating script!')
    #clean_db()
    load_sched(2019)
    print ("Populating Complete!")
    curr_week = Week.objects.get(current=True)
    print (Games.objects.filter(week__season_model__current=True, week__week__gt=curr_week.week).values('week__week').annotate(Count('week')))

