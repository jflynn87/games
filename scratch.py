import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from run_app.models import Plan, Schedule
from datetime import datetime, timedelta

def get_schedule():

    import urllib3.request
    import urllib
    import urllib3
    from bs4 import BeautifulSoup

    html = urllib.request.urlopen("https://connect.garmin.com/modern/activities")
    soup = BeautifulSoup(html, 'html.parser')
    print (soup)
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
