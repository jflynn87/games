import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from fb_app.models import Week, WeekScore, Player, League
from datetime import datetime, timedelta
import sqlite3
from django.db.models import Min, Q, Count

def get_schedule():

    import urllib3.request
    import urllib
    import urllib3
    from bs4 import BeautifulSoup

    import urllib3.request
    from bs4 import BeautifulSoup

    html = urllib.request.urlopen("https://nypost.com/odds/")
    soup = BeautifulSoup(html, 'html.parser')
    #print (soup)
    #find nfl section within the html

    nfl_sect = (soup.find("div", {'class':'odds__table-inner'}))
    #nfl_sect = (soup.find("tbody", {'id': 'primary'}))
    #print (nfl_sect)
    #nfl_sect = (soup.find("div", {'id': 'line-mlb'}))


    #pull out the games and spreads from the NFL section

    # spreads = {}
    # sep = ' '
    #
    for row in nfl_sect.find_all('tr')[1:]:
          col = row.find_all('td')
    #      print (col[0].text)
          #home = col[0].text.split()[0][10:20]
          #print (home)
          teams = col[0].text.split()
          #print (teams)
          line = col[5].text.split()
          #print (line)
          if line[0][0] == '-':
              print ('fav', teams[0])
              print ('dog', teams[1])
              print ('line', line[0])
              print ('o/a', line[1])
          else:
              print ('fav', teams[1])
              print ('dog', teams[0])
              print ('line', line [1])
              print ('o/a', line[0])
              


          #col[5].text)
    #      fav = col[0].string
    #      opening = col[1].string
    #      spread = col[2].string.split(sep, 1)[0]
    #      dog =  col[3].string
    #
    #      fav_obj = Teams.objects.get(long_name__iexact=fav)
    #      dog_obj = Teams.objects.get(long_name__iexact=dog)
    #
    #      week = Week.objects.get(current=True)
    #
    #      try:
    #         Games.objects.get(week=week, home=fav_obj)
    #         Games.objects.filter(week=week, home=fav_obj).update(fav=fav_obj, dog=dog_obj, opening=opening, spread=spread)
    #
    #      except ObjectDoesNotExist:
    #         Games.objects.filter(week=week,away=fav_obj).update(fav=fav_obj, dog=dog_obj, opening=opening, spread=spread)
    #
    # return




    # connection  = sqlite3.connect("db.sqlite3")
    #
    # cursor = connection.cursor()
    #
    # dropTableStatement = "DROP TABLE golf_app_tournament"
    #
    # cursor.execute(dropTableStatement)
    #
    # connection.close()


    #BonusDetails.objects.all().delete()
    #Group.objects.all().delete()
    #find nfl section within the html
    #
    # nfl_sect = (soup.find("div", {'id': 'line-nfl'}))
    # #nfl_sect = (soup.find("div", {'id': 'line-mlb'}))
    #
    #
    # #pull out the games and spreads from the NFL section
    #
    # spreads = {}
    # sep = ' '
    #
    # for row in nfl_sect.find_all('tr')[1:]:
    #      col = row.find_all('td')
    #      fav = col[0].string
    #      opening = col[1].string
    #      spread = col[2].string.split(sep, 1)[0]
    #      dog =  col[3].string
    #
    #      fav_obj = Teams.objects.get(long_name__iexact=fav)
    #      dog_obj = Teams.objects.get(long_name__iexact=dog)
    #
    #      week = Week.objects.get(current=True)
    #



get_schedule()
