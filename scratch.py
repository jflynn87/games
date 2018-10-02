import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from run_app.models import Plan, Schedule
from datetime import datetime, timedelta

def get_schedule():

    plan = Plan.objects.get(name="Nagano 19")

    for day in Schedule.objects.all():
        if day.type[-4:] in ['hill', 'empo', 'tlek', ' 200', ' 400',]:
            day.dist = 2
            day.save()
#





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
