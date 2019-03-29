import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from fb_app.models import Week, WeekScore, Player, League, Games, User, Picks, Player
from golf_app.models import BonusDetails, Tournament, Field, Picks, Group, TotalScore, Season, mpScores
#from datetime import datetime, timedelta
import datetime
import sqlite3
from django.db.models import Min, Q, Count
from golf_app import calc_score
import golf_app.populateField
#import urllib

from django.db import transaction
from bs4 import BeautifulSoup
import urllib.request
import json

def get_data():



    for score in mpScores.objects.all().order_by('round'):
        print (score.round, score.match_num, score.pick.playerName, score.result, score.score)



get_data()
