import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","fb_proj.settings")

import django
django.setup()
from fb_app.models import Games, Week, Teams
import urllib3
from bs4 import BeautifulSoup
import urllib.request
from datetime import datetime



def load_sched(year):

    #changing weeks to load preseason weeks (make week 0 and cnt 1)
    week_cnt = 1
    while week_cnt < 18:
        #html = urllib.request.urlopen("http://www.nfl.com/ajax/scorestrip?season=2018&seasonType=PRE&week=4")
        html = urllib.request.urlopen("http://www.nfl.com/ajax/scorestrip?season=2018&seasonType=REG&week=" + str(week_cnt))
        soup = BeautifulSoup(html, 'html.parser')


        week = Week()
        week.season = soup.find('gms').attrs['y']
        week.week = soup.find('gms').attrs['w']
        #week.week = 0
        week.game_cnt = gm_cnt = len(soup.findAll('g'))
        week.current = False
        #week.current = True
        week.save()

        for NFLgame in soup.findAll('g'):

            game=Games()

            game.week = week
            game.eid = NFLgame.attrs['eid']
            game.home = Teams.objects.get(nfl_abbr=NFLgame.attrs['h'])
            game.away = Teams.objects.get(nfl_abbr=NFLgame.attrs['v'])

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
    load_sched(2018)
    print ("Populating Complete!")
