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
def configure_groups(t):
    '''takes a tournament and returns nothing.  updates groups for the tournament'''
    i = 1
    while i < 9:
        group = Group()
        group.tournament = t
        group.number = i
        group.playerCnt = 10
        group.save()
        i +=1
    
    return

def get_field():
    field_dict = {}
    s_field_dict = {}
    #owgr_ranks = populateField.get_worldrank()
    for player in data['Tournament']['Players']:
        if player['isAlternate'] == "Yes":
            continue
        team = player['TeamID']

        name = (' '.join(reversed(player["PlayerName"].split(', '))).replace(' Jr.','').replace('(am)',''))
        pga_num = player["TournamentPlayerId"]
        lookup_name = name
        if field_dict.get(team) == None:
            field_dict[team] = {'name1': name,
                                'pga_num1': pga_num,
                                'ranks1': utils.fix_name(name, owgr_ranks)[1]}
        else:
            field_dict[team].update({'name2': name,
                                'pga_num2': pga_num,
                                'ranks2': utils.fix_name(name, owgr_ranks)[1]})

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


