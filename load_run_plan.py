import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
import urllib
#import urllib
from run_app.models import Plan, Schedule
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

def get_schedule():
    #import urllib3.request
    
    html = urllib.request.urlopen("https://www.halhigdon.com/training-programs/marathon-training/marathon-3/")
    soup = BeautifulSoup(html, 'html.parser')
    schedule = (soup.find("div", {'id': 'training-schedule'}))

    plan = Plan.objects.get(name="Nagano 21")
    date = plan.start_date
    sect = 0


    for row in schedule.find_all('tr')[1:]:
        col = row.find_all('td')
        if len(col) >0:
            week = col[0].string
            for day in col[1:]:
                schedule = Schedule()
                schedule.plan = plan
                schedule.date  = date
                schedule.week = week
                #dist = str(day.string)
#                print ('day.string', day.string)
                schedule.dist = 0
                if day.string[-3:] == 'run' and day.string[1] != '-':
                    schedule.dist = int(str(day.string).split(' ')[0])
                if day.string[-3:] == 'run' and day.string[1] == '-':
                    schedule.dist = int(str(day.string)[2])
                if day.string[-4:] in ['Rest', "ross", "Bike"]:
                    schedule.dist = 0
                if day.string[-4:] in ['hill', 'empo', 'tlek', ' 200', ' 400', 'pace']:
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
                    elif day.string[0:3] == '1-2':
                        schedule.dist = 2
                    #else:
                    #    schedule.dist = int(str(day.string).split('-')[0])
                if day.string[-3:] == 'hon':
                    schedule.dist = 26

                schedule.sched_type = day.string
                print ('date', schedule.date, 'week', schedule.week, 'dist', schedule.dist, 'type', schedule.sched_type)
                schedule.save()
                #print (date, schedule.week, schedule.dist, schedule.type)
                date = date + timedelta(days=1)
            if date > plan.end_date:
                break



def act_type(activity):
    pass        


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
