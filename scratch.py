import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
import urllib3
import urllib
from run_app.models import Plan, Schedule
from datetime import datetime, timedelta

def get_schedule():
    import urllib3.request
    from bs4 import BeautifulSoup

    html = urllib.request.urlopen("https://www.halhigdon.com/training-programs/marathon-training/personal-best/")
    soup = BeautifulSoup(html, 'html.parser')

    #find nfl section within the html

    schedule = (soup.find("div", {'id': 'miles'}))

    plan = Plan.objects.get(name="Nagano 19")
    date = plan.start_date

    for row in schedule.find_all('tr')[1:]:
        col = row.find_all('td')
        if len(col) >0:
            week = col[0]
            for day in col[1:]:
                schedule = Schedule()
                schedule.plan = plan
                schedule.date  = date
                schedule.week = week
                dist = str(day.string)

                if day.string[-3:] == 'run':
                    schedule.dist = int(str(day.string).split(' ')[0])
                if day.string[-4:] in ['Rest', "ross"]:
                    schedule.dist = 0
                if day.string[-4:] in ['hill', 'empo', 'tlek', ' 200', ' 400',]:
                    schedule.dist = 3
                if day.string[-4:] in ['empo', 'tlek']:
                    schedule.dist = 5
                if day.string[-4:] == 'pace':
                    schedule.dist = int(str(day.string).split(' ')[0])
                if day.string[-4:] == 'Race':
                    if day.string[0:4] == "Half":
                        schedule.dist = 21
                    elif day.string[0:1] == "5":
                        schedule.dist = 3
                    elif day.string[0:2] == "10":
                        schedule.dist = 6
                    elif day.string[0:2] == "15":
                        schedule.dist = 10
                    #else:
                    #    schedule.dist = int(str(day.string).split('-')[0])
                if day.string[-3:] == 'hon':
                    schedule.dist = 26

                schedule.type = day.string
                schedule.save()
                print (date, schedule.week, schedule.dist, schedule.type)
                date = date + timedelta(days=1)






    #pull out the games and spreads from the NFL section
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
    #      try:
    #         Games.objects.get(week=week, home=fav_obj)
    #         Games.objects.filter(week=week, home=fav_obj).update(fav=fav_obj, dog=dog_obj, opening=opening, spread=spread)
    #
    #      except ObjectDoesNotExist:
    #         Games.objects.filter(week=week,away=fav_obj).update(fav=fav_obj, dog=dog_obj, opening=opening, spread=spread)
    #
    # return

get_schedule()
