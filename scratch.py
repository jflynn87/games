import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from fb_app.models import Week, WeekScore, Player, League, Games, User, Picks, Player
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

    loss = 0
    win = 0
    week = Week.objects.get(week=1)
    for player in Player.objects.all():
        win = 0
        loss = 0
        for pick in (Picks.objects.filter(player=player)):
            if pick.is_loser():
                loss +=1
            else:
                win +=1
        avg = win/(win+loss)
        print (player, win, loss, avg)




    # result = {}
    # fav_total = 0
    # dog_total = 0
    #
    # for week in Week.objects.all():
    #     work_list = []
    #     fav_count = 0
    #     dog_count = 0
    #     tie_count = 0
    #     for game in Games.objects.filter(week=week):
    #         print (game.week, game.eid, game.fav, game.dog)
    #         if game.winner == game.fav:
    #             fav_count += 1
    #         elif game.winner == game.dog:
    #             dog_count += 1
    #         elif game.tie:
    #             tie_count += 1
    #         else:
    #             print ('else', game.week, game.eid, game.fav, game.dog)
    #     work_list.append(fav_count)
    #     work_list.append(dog_count)
    #     work_list.append(tie_count)
    #     result[week.week]=work_list
    #     fav_total += fav_count
    #     dog_total += dog_count
    # print (result)
    # print ('fav', fav_total)
    # print ('dog', dog_total)

    # table = doc.Tables(1)
    # row_i = 1
    #
    #
    #
    # while row_i < 37:
    #     col_i = 1
    #     while col_i < 28:
    #         if (row_i, col_i, table.Cell(Row=row_i,Column=col_i).Range.Text) == None  and col_i == 1:
    #             col_i = 29
    #         else:
    #             cell = table.Cell(Row=row_i,Column=col_i).Range.Text
    #             print (row_i, col_i, len(cell))
    #
    #             col_i += 1
    #     row_i += 1
    #






get_schedule()
