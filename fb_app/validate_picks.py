import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","fb_proj.settings")

import django
django.setup()
from fb_app.models import Games, Picks, Week

def validate(pick_list):
    '''takes a list of teams and validates the picks vs the games object.
    returns a list with a boolean indicating if the list is valid
    and a list with error messages'''


    picks_valid = True
    error = []

    week = Week.objects.get(current=True)
    games_dict = {}

    for game in Games.objects.filter(week=week):
        count = 0
        if str(game.away) in pick_list:
            count +=1
        if str(game.home) in pick_list:
            count +=1

        games_dict[game.eid] = str(game.home), str(game.away), count

    #if len(pick_list) != len(set(pick_list)):
     #   picks_valid=False
      #  error = "Duplicate Picks"
    #else:
    print (games_dict)
    for count in games_dict.values():
        if count[2] > 1:
            picks_valid = False
            error.append("Picked the same game twice: " + str(count[0]) + '  ' + str(count[1]))
        if count[2] == 0:
            picks_valid = False
            error.append("Missed picking: " + str(count[0]) + '  ' + str(count[1]))

    return [picks_valid, error]
