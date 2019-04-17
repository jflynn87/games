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

    users = TotalScore.objects.filter(tournament__pga_tournament_num="014")
    for user in users:
        bd = BonusDetails()
        bd.user = user.user
        bd.tournament = Tournament.objects.get(current=True)
        bd.cut_bonus = 0
        bd.winner_bonus = 0
        bd.save()

    print (BonusDetails.objects.filter(tournament=Tournament.objects.get(current=True)))

test()
