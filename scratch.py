import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from fb_app.models import Week, WeekScore, Player, League, Games, User, Picks, Player
from golf_app.models import BonusDetails, Tournament, Field, Picks, Group, TotalScore
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
    user = User.objects.get(username="Laroqm")

    for tournament in Tournament.objects.all():
            total_score = TotalScore()
            bonus_detal = BonusDetails()

            total_score.user = user
            total_score.tournament = tournament
            total_score.score = 999
            total_score.cut_count = 0

            bonus_detal.user = user
            bonus_detal.tournament = tournament
            bonus_detal.winner_bonus = 0
            bonus_detal.cut_bonus = 0

            total_score.save()
            bonus_detal.save()





get_schedule()
