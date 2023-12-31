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

    plan = Plan.objects.get(current=True)
    html = urllib.request.urlopen(plan.url)
    soup = BeautifulSoup(html, 'html.parser')
    schedule = (soup.find("div", {'id': 'training-schedule'}))

    date = plan.start_date
    sect = 0
    Schedule.objects.filter(plan=plan).delete()

    for row in schedule.find_all('tr')[1:]:
        col = row.find_all('td')
        if len(col) >0:
            week = col[0].string
            for day in col[1:]:
                schedule = Schedule()
                schedule.plan = plan
                schedule.date  = date
                schedule.week = week
                schedule.dist = 0
                if day.string.isnumeric():
                    schedule.dist = int(day.string)
                elif day.string[0].isnumeric():
                    schedule.dist = int(day.string[0])
                elif day.string[0:1].isnumeric():
                    schedule.dist = int(day.string[0:1])
                elif day.string[0:4] == 'Half':
                    schedule.dist = 13
                elif day.string[-3:] == 'hon':
                    schedule.dist = 26

                schedule.sched_type = day.string
                print ('date', schedule.date, 'week', schedule.week, 'dist', schedule.dist, 'type', schedule.sched_type)
                schedule.save()
                #print (date, schedule.week, schedule.dist, schedule.type)
                date = date + timedelta(days=1)
            if date > plan.end_date:
                break


if __name__ == '__main__':
    print ("Starting Run Plan population script...")
    get_schedule()
