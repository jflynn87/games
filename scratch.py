import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from fb_app.models import Week, WeekScore, Player, League, Games, User, Picks, Player
from golf_app.models import BonusDetails, Tournament, Field, Picks, Group
from datetime import datetime, timedelta
import sqlite3
from django.db.models import Min, Q, Count
from golf_app import calc_score

def get_schedule():

    import urllib3.request
    import urllib
    import urllib3
    from bs4 import BeautifulSoup
    import json

    import urllib3.request
    from bs4 import BeautifulSoup

    from docx import Document
    # import win32com.client as win32
    # word = win32.Dispatch("Word.Application")
    # word.Visible = 0
    # word.Documents.Open("18-19 FOOTBALL FOOLS")
    i = 0
    while i < 10:
        for tournament in Tournament.objects.all():
            key = {}
            key['pk'] = tournament.pk
            print (tournament.pk, tournament.name, key)
            scores = calc_score.getRanks(key)

            for group in Group.objects.filter(tournament=tournament):
                for golfer in Field.objects.filter(group=group):
                    if golfer.playerName not in scores[1] and golfer.playerName not in scores[0]:
                        #score = scores[0][golfer.playerName]
                        print (golfer.playerName, tournament.name)
            i +=1






get_schedule()
