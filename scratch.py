import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from fb_app.models import Week, WeekScore, Player, League, Games, User, Picks, Player
from golf_app.models import BonusDetails
from datetime import datetime, timedelta
import sqlite3
from django.db.models import Min, Q, Count

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


#most recent logic to test
    #doc = Document("18-19 FOOTBALL FOOLS")

    #for table in doc.tables:
    #    for row in table.rows:
    #        for cell in row.cells:
    #            print (cell.text)
    # json_url = 'http://www.nfl.com/liveupdate/scores/scores.json'
    #
    # with urllib.request.urlopen(json_url) as field_json_url:
    #     data = json.loads(field_json_url.read().decode())
    #
    # for k, v in data.items():
    #     print (k, v['home']['abbr'], v['away']['abbr'])

    # home_team = data[score.eid]['home']["abbr"]
    # away_team = data[score.eid]['away']["abbr"]
    # away_score = data[score.eid]['away']['score']['T']

    bonus = BonusDetails.objects.all().order_by('tournament')

    for b in bonus:
        print (b.tournament, b.user, b.winner_bonus, b.cut_bonus)


get_schedule()
