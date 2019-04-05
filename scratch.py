import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from fb_app.models import Week, WeekScore, Player, League, Games, User, Picks, Player
from golf_app.models import BonusDetails, Tournament, Field, Picks, Group, TotalScore, ScoreDetails
#from datetime import datetime, timedelta
import datetime
import sqlite3
from django.db.models import Min, Q, Count
from golf_app import calc_score


def test():

    t = Tournament.objects.get(current=True)

    for sd in ScoreDetails.objects.filter(pick__playerName__tournament=t).order_by('user'):
        print (sd.user, sd.pick, sd.score)



test()
