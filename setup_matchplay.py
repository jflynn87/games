import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from fb_app.models import Week, WeekScore, Player, League, Games, User, Picks, Player
from golf_app.models import BonusDetails, Tournament, Field, Picks, Group, TotalScore, Season
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

@transaction.atomic
def setup(tournament_number):

            season = Season.objects.get(current=True)

            last_tournament = Tournament.objects.get(current=True, complete=True, season=season)
            last_tournament.current = False
            last_tournament.save()

            json_url = 'https://statdata.pgatour.com/r/' + str(tournament_number) +'/field.json'
            print (json_url)

            with urllib.request.urlopen(json_url) as field_json_url:
                data = json.loads(field_json_url.read().decode())

            tourny = Tournament()
            tourny.name = data["Tournament"]["TournamentName"]
            tourny.season = season
            start_date = datetime.date.today()
            print (start_date)
            while start_date.weekday() != 2:
                start_date += datetime.timedelta(1)
            tourny.start_date = start_date
            tourny.field_json_url = json_url
            tourny.score_json_url = 'https://statdata.pgatour.com/r/' + str(tournament_number) +'/' + str(season) + '/leaderboard-v2mini.json'
            tourny.pga_tournament_num = tournament_number
            tourny.current=True
            tourny.complete=False
            tournament = tourny.save()

            print (tourny)
            group_cnt = 1
            while group_cnt < 17:
                group = Group()
                group.tournament = tourny
                group.number = group_cnt
                group.playerCnt = 4
                print (group_cnt)
                group.save()
                group_cnt += 1

def get_field():


    f = open ('match_play_field.txt', 'r')
    tournament = Tournament.objects.get(current=True)


    for line in f:
        if len(line) < 4:
            print ('group', line)
            group = Group.objects.get(number=int(line), tournament=tournament)
        else:
            rank = (int(line[-5:].replace('(','').replace(')','')))
            name = (line[0:-5])

            field = Field()
            field.playerName  = name
            field.currentWGR = rank
            field.tournament = tournament
            field.group = group
            field.save()
            print (group, name, rank)


    #html = urllib.request.urlopen("https://www.pgatour.com/competition/2019/wgc-dell-technologies-match-play/group-stage.html")
    #soup  = BeautifulSoup(html, 'html.parser')

    #field  = (soup.find_all("div", {'class': 'group-section-title'}))

    #print (field)


    # json_url = "https://statdata.pgatour.com/r/470/2019/leaderboard_mp.json"
    #
    # with urllib.request.urlopen(json_url) as field_json_url:
    #     data = json.loads(field_json_url.read().decode())
    #
    # field = data['rounds']
    # #print ((field[0]))
    # for k,v in field[0].items():
    #     #print (k, type(v))
    #     if k == "brackets":
    #         i = 0
    #         j = 2
    #         while i <= 3:
    #             #print (i)
    #             for key, value in v[i].items():
    #                 if key == "groups":
    #                     #print ('Group: ', value[0])
    #                     print (value[1]['debug']['group'])
    #                     print (value[0]['players'][0]['lName'])
    #                     print (value[0]['players'][1]['lName'])
    #                     print (value[1]['players'][0]['lName'])
    #                     print (value[1]['players'][1]['lName'])
    #             if i == 3:
    #                 while j < 24:
    #                     print (v[i]['groups'][j]['debug']['group'])
    #                     print (v[i]['groups'][j]['players'][0]['lName'])
    #                     print (v[i]['groups'][j]['players'][1]['lName'])
    #                     print (v[i]['groups'][j+1]['players'][0]['lName'])
    #                     print (v[i]['groups'][j+1]['players'][1]['lName'])
    #                     j += 2
    #
    #
    #                 #print ((v[i]['groups'][4]['players']))
    #                 #print ((v[i]['groups'][5]))
    #             i += 1



    #print ('group')




setup('470')
get_field()
