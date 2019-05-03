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

    for t in Tournament.objects.all():
        scores = TotalScore.objects.filter(tournament=t).order_by('score').values('score')
        i = 2
        print (scores[0].get('score'), scores[i].get('score'), scores[i].get('score') - scores[0].get('score'), '{0:.0f}%'.format((scores[i].get('score') - scores[0].get('score')/scores[0].get('score'))/100))


get_schedule()
