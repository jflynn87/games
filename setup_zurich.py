import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()

from golf_app.models import BonusDetails, Tournament, Field, Picks, Group, TotalScore, ScoreDetails, Season
#from datetime import datetime, timedelta
import datetime
import sqlite3
from django.db.models import Min, Q, Count
from golf_app import calc_score
import json
from golf_app import populateField
import urllib
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
import urllib3
import urllib.request

@transaction.atomic
def test():

    season = Season.objects.get(current=True)

    if Tournament.objects.filter(season=season).count() > 0:
        try:
            last_tournament = Tournament.objects.get(current=True, complete=True, season=season)
            last_tournament.current = False
            last_tournament.save()
            key = {}
            key['pk']=last_tournament.pk
            calc_score.calc_score(key)

        except ObjectDoesNotExist:
            print ('no current tournament')
    else:
        print ('setting up first tournament of season')

    json_url = 'https://statdata.pgatour.com/r/018/field.json'
    with urllib.request.urlopen(json_url) as field_json_url:
        data = json.loads(field_json_url.read().decode())


    tournament_number = '018'
    tourny = Tournament()
    tourny.name = data["Tournament"]["TournamentName"]
    tourny.season = season
    start_date = datetime.date.today()
    print (start_date)
    while start_date.weekday() != 3:
        start_date += datetime.timedelta(1)
    tourny.start_date = start_date
    #tourny.start_date = data["Tournament"]["yyyy"] + '-' +data["Tournament"]["mm"] + '-' + data["Tournament"]["dd"]
    tourny.field_json_url = json_url
    tourny.score_json_url = 'https://statdata.pgatour.com/r/' + str(tournament_number) +'/' + str(season) + '/leaderboard-v2mini.json'
    tourny.pga_tournament_num = tournament_number
    tourny.current=True
    tourny.complete=False
    tourny.save()

    i = 1
    while i < 9:
        group = Group()
        group.tournament = tourny
        group.number = i
        group.playerCnt = 10
        group.save()
        i +=1


    field_dict = {}
    s_field_dict = {}
    #ranks = populateField.get_worldrank()
    pga_ranks = populateField.get_pga_worldrank()
    owgr_ranks = populateField.get_worldrank()

    #f = open('field.json', 'rb')
    for player in data['Tournament']['Players']:
        team = player['TeamID']

        name = (' '.join(reversed(player["PlayerName"].split(', '))).replace(' Jr.','').replace('(am)',''))
        if name == "Roberto D?az":
            name = "Roberto Diaz"
        if name == "Freddie Jacobson":
            name = "Freddie Jacobson(Sept1974)"
        #if name == "Si Woo Kim":
        #    name = "Siwoo Kim"
        if name == "Whee Kim":
            name = "Meenwhee Kim"
        if name == "Kyoung-hoon Lee":
            name = "Kyounghoon Lee"
        if name == "Dru Love":
            name = "Dru Love IV"


        if field_dict.get(team) == None:
            team_list = []
            try:
                rank = pga_ranks[name.capitalize()]
            except Exception:
                print ('except', name)
                rank = owgr_ranks.get(name.capitalize())
            tuple = (player['PlayerName'], rank)
            team_list.append(tuple)
            field_dict[team] = team_list
        else:
            team_list= field_dict.get(team)
            try:
                rank = pga_ranks[name.capitalize()]
            except Exception:
                print ('except', name)
                rank = owgr_ranks.get(name.capitalize())
            tuple = (player['PlayerName'], rank) #get owgr
            team_list.append(tuple)
            field_dict[team] = team_list
    #print(field_dict)
    #print (len(field_dict))

    for k,v in field_dict.items():
        if int(v[0][1]) < int(v[1][1]):
            s_field_dict[k] = (v[0], v[1], v[0][1]+v[1][1])
        else:
            s_field_dict[k] = (v[1], v[0], v[0][1]+v[1][1])


    group_size = 10
    group = 1
    count = 0

    for k, v in sorted(s_field_dict.items(), key=lambda x: x[1][2]):
        if count < group_size:
            field = Field()
            field.playerName = v[0][0]
            field.currentWGR = v[0][1]
            field.tournament = tourny
            field.group = Group.objects.get(number=group, tournament=tourny)
            field.alternate = False
            field.withdrawn = False
            field.partner = v[1]
            field.teamID = k
            field.save()
            count += 1
            print (field, field.partner)

            if count == group_size:
                group += 1
                count = 0



test()
