import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from golf_app.models import Tournament, TotalScore
from datetime import datetime, timedelta
import sqlite3
from django.db.models import Min, Q, Count, Sum, Max
from django.db.models.functions import ExtractWeek, ExtractYear

def get_schedule():

    tournament = Tournament.objects.get(current=True)
    print (tournament)
    print (TotalScore.objects.filter(tournament=tournament, cut_count=0).exists())
    ts = TotalScore.objects.filter(tournament=tournament, cut_count=0)
    print (ts)
get_schedule()
