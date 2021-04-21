import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()

from golf_app.models import BonusDetails, Tournament, Field, Picks, Group, TotalScore, ScoreDetails, Season, Golfer
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
from urllib.request import Request, urlopen
from golf_app import utils
import unidecode
from bs4 import BeautifulSoup

@transaction.atomic
def test():

    season = Season.objects.get(current=True)

    if Tournament.objects.filter(season=season).count() > 0:
        try:
            last_tournament = Tournament.objects.get(current=True, complete=True, season=season)
            last_tournament.current = False
            last_tournament.save()
            #key = {}
            #key['pk']=last_tournament.pk
            #calc_score.calc_score(key)

        except ObjectDoesNotExist:
            print ('no current tournament')
    else:
        print ('setting up first tournament of season')

    json_url = 'https://statdata-api-prod.pgatour.com/api/clientfile/Field?T_CODE=r&T_NUM=018&YEAR=2021&format=json'
    #with urllib.request.urlopen(json_url) as field_json_url:
    #    data = json.loads(field_json_url.read().decode())


    req = Request(json_url, headers={'User-Agent': 'Mozilla/5.0'})
    data = json.loads(urlopen(req).read())


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
    #pga_ranks = populateField.get_pga_worldrank()
    owgr_ranks = populateField.get_worldrank()
    #with open('owgr.json') as json_file:  owgr_ranks = json.loads(json_file.read())

    #f = open('field.json', 'rb')
    for player in data['Tournament']['Players']:
        if player['isAlternate'] == "Yes":
            continue
        team = player['TeamID']

        name = (' '.join(reversed(player["PlayerName"].split(', '))).replace(' Jr.','').replace('(am)',''))
        pga_num = player["TournamentPlayerId"]
        lookup_name = name
        # if name == "Roberto D?az":
        #     name = "Roberto Diaz"
        #if name == "Freddie Jacobson":
        #     lookup_name = "Freddie Jacobson(Sept1974)"
        # #if name == "Si Woo Kim":
        # #    name = "Siwoo Kim"
        # if name == "Whee Kim":
        #     name = "Meenwhee Kim"
        # if name == "Kyoung-hoon Lee":
        #     name = "Kyounghoon Lee"
        #if name == "Dru Love":
        #     lookup_name = "Dru Love IV"

        if field_dict.get(team) == None:
            #print ('team missing', name)
            field_dict[team] = {'name1': name,
                                'pga_num1': pga_num,
                                'ranks1': utils.fix_name(name, owgr_ranks)[1]}
        else:
            field_dict[team].update({'name2': name,
                                'pga_num2': pga_num,
                                'ranks2': utils.fix_name(name, owgr_ranks)[1]})
#            try:
#                rank = utils.fix_name(name, owgr_ranks)
#            except Exception:
#                print ('owgr except', name)
                #rank = utils.fix_name(name, owgr_ranks)
            #tuple = (player['PlayerName'], rank)
    #         t = (name, rank[1], pga_num)
    #         team_list.append(t)
    #         field_dict[team] = team_list
    #     else:
    #         team_list= field_dict.get(team)
    #         try:
    #             #rank = pga_ranks[name.capitalize()]
    #             rank = utils.fix_name(name, owgr_ranks)
    #         except Exception:
    #             print ('owgr except', name)
    #             #rank = owgr_ranks.get(lookup_name.capitalize())
    #         #tuple = (player['PlayerName'], rank) #get owgr
    #         #t = (name, rank)
    #         t = (name, rank[1], pga_num)
    #         team_list.append(t)
    #         field_dict[team] = team_list
    
    #print (len(field_dict))
    #print ('Field List', field_dict)
    # for k,v in field_dict.items():
    #     print ('k', k)
    #     print (v)
    #     print (v[0][1][0], v[1][1][0])
    #     if int(v[0][1][0]) < int(v[1][1][0]):
    #         s_field_dict[k] = (v[0][0], v[1][0], v[0][1][0]+v[1][1][0])
    #     else:
    #         s_field_dict[k] = (v[1][0], v[0][0], v[0][1][0]+v[1][1][0])

    print(field_dict)
    s_dict = {k:v for k, v in sorted(field_dict.items(), key=lambda x: x[1].get('ranks1')[0] + x[1].get('ranks2')[0])}

    group_size = 10
    group = 1
    count = 0

    #print ('S DICT')
    print (s_dict)

    #for k, v in sorted(s_field_dict.items(), key=lambda x: x[1][2]):
    for k, v in s_dict.items():
        print (k,v)
        g1, c1 = Golfer.objects.get_or_create(golfer_pga_num=v.get('pga_num1'))
        g1.pic_link = populateField.get_pick_link(v.get('pga_num1'))
        if c1:
            g1.golfer_name = v.get('name1')
            if v.get('name1')[1]=='.' and v.get('name1')[3] =='.':
                name = str(v.get('pga_num1') + '.' + v.get('name1')[0].lower() + '-' + v.get('name1')[2].lower() + '--' + v.get('name1').split(' ')[1].strip(', Jr.').lower())
            else:
                name = str(v.get('pga_num1')) + '.' + v.get('name1').split(' ')[0].lower() + '-' + v.get('name1').split(' ')[1].strip(', Jr.').lower()

            link = 'https://www.pgatour.com/players/player.' + unidecode.unidecode(name) + '.html'
            print (link)

            player_html = urllib.request.urlopen(link)
            player_soup = BeautifulSoup(player_html, 'html.parser')
            country = (player_soup.find('div', {'class': 'country'}))

            flag = country.find('img').get('src')
            print (flag)
            g1.flag_link = "https://www.pgatour.com" + flag
        g1.save()

        g2, c2 = Golfer.objects.get_or_create(golfer_pga_num=v.get('pga_num2'))
        g2.pic_link = populateField.get_pick_link(v.get('pga_num2'))
        if c2:
            g2.golfer_name = v.get('name2')
            if v.get('name2')[1]=='.' and v.get('name2')[3] =='.':
                name = str(v.get('pga_num2') + '.' + v.get('name2')[0].lower() + '-' + v.get('name2')[2].lower() + '--' + v.get('name2').split(' ')[1].strip(', Jr.').lower())
            else:
                name = str(v.get('pga_num2')) + '.' + v.get('name2').split(' ')[0].lower() + '-' + v.get('name2').split(' ')[1].strip(', Jr.').lower()

            link = 'https://www.pgatour.com/players/player.' + unidecode.unidecode(name) + '.html'
            print (link)
            player_html = urllib.request.urlopen(link)
            player_soup = BeautifulSoup(player_html, 'html.parser')
            country = (player_soup.find('div', {'class': 'country'}))

            flag = country.find('img').get('src')
            print (flag)
            g2.flag_link = "https://www.pgatour.com" + flag
        g2.save()


        #g1  = populateField.get_flag(k, v, owgr_ranks)
        #g2 = populateField.get_flag(v[1], v, owgr_ranks)
        if count < group_size:
            field = Field()
            field.currentWGR = field.currentWGR = v.get('ranks1')[0] + v.get('ranks2')[0]
            if v.get('ranks1')[0] <  v.get('ranks2')[0]: #0 is the current OWGR
                field.playerName = v.get('name1')
                field.golfer = Golfer.objects.get(golfer_pga_num=v.get('pga_num1'))
                
                field.partner = v.get('name2')
                field.partner_golfer = Golfer.objects.get(golfer_pga_num=v.get('pga_num2'))
                field.partner_owgr = v.get('ranks2')[0]

            else:
                field.playerName = v.get('name2')
                field.golfer = Golfer.objects.get(golfer_pga_num=v.get('pga_num2'))
                
                field.partner = v.get('name1')
                field.partner_golfer = Golfer.objects.get(golfer_pga_num=v.get('pga_num1'))
                field.partner_owgr = v.get('ranks1')[0]

            field.tournament = tourny
            field.group = Group.objects.get(number=group, tournament=tourny)
            field.alternate = False
            field.withdrawn = False

            field.teamID = k
#            field.golfer = g1
#            field.partner_golfer = g2
            field.save()
            count += 1
            print (field, field.partner)

            if count == group_size:
                group += 1
                count = 0



test()
