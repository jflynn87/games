import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from golf_app.models import Tournament, TotalScore, ScoreDetails, Picks, PickMethod, BonusDetails, \
        Season, Golfer, Group, Field, ScoreDict, AuctionPick, AccessLog, StatLinks, CountryPicks, FedExSeason, FedExField
from django.contrib.auth.models import User
from datetime import date, datetime, timedelta
import sqlite3
from django.db.models import Min, Q, Count, Sum, Max
from django.db.models.functions import ExtractWeek, ExtractYear
import time
from requests import get
from random import randint
import sys
# pip install PyQt5 and PyQtWebEngine
#from PyQt5.QtWidgets import QApplication, QWidget
#from PyQt5.QtCore import QUrl
#from PyQt5.QtWebEngineWidgets import QWebPage
#from PyQt5.QtWebEngine import QtWebEngine as QWebPage

#from PyQt5.QtWebEngineWidgets import QWebEngineView
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from selenium import webdriver
import urllib
import json
from golf_app import views, manual_score, populateField, withdraw, scrape_scores_picks, utils, \
                            scrape_masters, scrape_espn, espn_api, fedexData, espn_ryder_cup, ryder_cup_scores
from unidecode import unidecode
from django.core import serializers
from golf_app.utils import formatRank, format_name, fix_name
from golf_app import golf_serializers
import pytz
from collections import OrderedDict
import math
import scipy.stats as ss
import csv
import random
from operator import itemgetter

start  = datetime.now()
s = Season.objects.get(current=True)
t = Tournament.objects.get(current=True)
#field = data= golf_serializers.NewFieldSerializer(Field.objects.filter(tournament=t), context={}, many=True).data
#print (field)
#exit()

espn = espn_ryder_cup.ESPNData()
f = espn.field()
print (f.get('Sunday Singles'))
exit()
#print (type(espn.get_all_data()), len(espn.get_all_data()))
for event in espn.get_all_data().get('events')[0].get('competitions'):
    print (len(event), type(event))
    for e in event:
        if e.get('description') == "Sunday Singles":
            print ('=============================')
            print (e)
    
    
exit()
f = espn.field()
print (f)
print (f.get('overall'))
print (f.get('Sunday Singles'))
exit()
#print (match)
winning_holes = [v.get('score').get('value') for k,v in match.items() if k !='status' and v.get('score').get('winner') == True]
print (winning_holes)
exit()

#for k, v in espn.field().items():
#    print (k, v)
score = ryder_cup_scores.Score(espn.field()).update_scores()
total_scores = ryder_cup_scores.Score(espn.field()).total_scores()

exit()
for session, matches in espn.field().items():
    print (session)
    if session != 'overall':
        for m_id, m_data in matches.items():
            for espn_num, info in m_data.items():
                print (m_id, info.get('golfer'), info.get('score'))
                print ('-----')         
print (espn.field().get('overall'))
print (espn.field())
print (datetime.now() - start)
exit()

#espn = espn_ryder_cup.ESPNData(espn_t_num='401025269')


for session, matches in espn.field.items():
    print (session, matches)



exit()
sd = ScoreDict.objects.get(tournament=t)
if espn.field() == sd.cbs_data:
    print ("No change in ryder cup score DATA")
else:
    print ('different ryder cup data')
    sd.cbs_data = espn.field()
    sd.save()
 
ryder_cup_scores.Score(espn.score_dict()).update_scores()
exit()
#print (espn.field())
#exit()
headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
score_dict = {}
for match, info in espn.field().items():
    score_dict[match] = {}
    if match != 'overall':
        if info.get('type') != 'singles':
            for t in ['USA', 'EURO']:
                url =  info.get(t).get('golfers_link')
                golfers = get(url, headers=headers).json()
                for entry in golfers.get('entries'):
                    golfer_obj = Golfer.objects.get(espn_number=entry.get('playerId'))
                    score_url = info.get(t).get('score_link')
                    score_data = get(score_url, headers=headers).json()
                    #print (t, info.get('type'), golfer_obj, score_data.get('winner'), score_data.get('value'), score_data.get('holesRemaining'), score_data.get('displayValue'), score_data.get('draw'))
                    score_dict[match].update({t: {'type': info.get('type'),
                                                  'golfer_pk': golfer_obj.pk, 
                                                  'winner': score_data.get('winner'),
                                                  'value': score_data.get('value'),
                                                  'holes_remaining': score_data.get('holesRemaining'),
                                                  'display_value': score_data.get('displayValue'),
                                                  'draw': score_data.get('draw')
                                                  }})
        elif info.get('type') == 'singles':
            for t in ['USA', 'EURO']:
                url =  info.get(t).get('golfers_link')
                golfer = get(url, headers=headers).json()
                #print (golfer)
                golfer_obj = Golfer.objects.get(espn_number=golfer.get('id'))
                score_url = info.get(t).get('score_link')
                score_data = get(score_url, headers=headers).json()
                #print (t, info.get('type'), golfer_obj, score_data.get('winner'), score_data.get('value'), score_data.get('holesRemaining'), score_data.get('displayValue'), score_data.get('draw'))
                score_dict[match].update({t: {'type': info.get('type'),
                            'golfer_pk': golfer_obj.pk, 
                            'winner': score_data.get('winner'),
                            'value': score_data.get('value'),
                            'holes_remaining': score_data.get('holesRemaining'),
                            'display_value': score_data.get('displayValue'),
                            'draw': score_data.get('draw')
                            }})

    
print (score_dict)
print (datetime.now() - start)
exit()
print (espn.get_all_data().keys())
print ('competitions')
print (espn.get_all_data().get('competitions')[0].keys(), len(espn.get_all_data().get('competitions')[0]))

for c in espn.get_all_data().get('competitions'):
    print ('=============================================================')
    print (c)

print ('competitors')
print (espn.get_all_data().get('competitions')[0].get('competitors')[0].keys())
print ("Teams")
print (espn.get_all_data().get('competitions')[0].get('competitors')[0].get('team'))
print (espn.get_all_data().get('competitions')[0].get('competitors')[0].get('score'))

exit()
#f = open('owgr.json',)
#print (type(f))
#owgr = json.load(f)

for golfer in Golfer.objects.filter()[1:5]:
    rank = utils.fix_name(golfer.golfer_name, owgr)
    if int(rank[1][0]) < 30:
        print (golfer, rank[0])
exit()
#owgr = populateField.get_worldrank()
f = open('owgr.json',)
print (type(f))
owgr = json.load(f)
#field = populateField.get_field(t, owgr)


#sorted_intl_team = sorted({k:v for k,v in field.items() if v.get('team') == 'INTL'}, key=lambda item: item[1].get('curr_owgr'))
#sorted_usa_team = sorted({k:v for k,v in field.items() if v.get('team') == 'USA'}, key=lambda item: item[1].get('curr_owgr'))

headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
#url =  "https://site.web.api.espn.com/apis/site/v2/sports/golf/leaderboard?league=pga"
#url = 'http://sports.core.api.espn.com/v2/sports/golf/leagues/pga/events/401025269'
espn = espn_ryder_cup.ESPNData(espn_t_num='401025269').field()

print (espn)

# print ('--------------------------------------------------------')

# for key, match in espn.items():
#     print (key, match)
#     try:
#         print (match.get('id'), match.get('description'))
#     except Exception as e:
#         continue

exit()  
s = Season.objects.get(current=True)
f, created = FedExSeason.objects.get_or_create(season=s, allow_picks=True)
f.prior_season_data = populateField.get_fedex_data()

f.save()

fed = fedexData.FedEx(s).create_field()
#owgr = populateField.get_worldrank()
#top_200 = {k:v for k,v in owgr.items() if int(v[2] <= 201)}





#espn_data = espn_api.ESPNData().get_all_data()
#context = {'espn_data': espn_data, 'user': User.objects.get(pk=1)}
#data= golf_serializers.NewFieldSerializer(Field.objects.filter(tournament=t, group__number=2), context=context, many=True).data
#d = json.loads(data[0])
print (datetime.now() - start)

#f = open('owgr.json',)
#print (type(f))
#owgr = json.load(f)
#field_dict = populateField.get_field(t, owgr)
#print (len(field_dict))
#populateField.configure_groups(field_dict, t)
#for k, v in sorted(field.items(), key=lambda v:v[1].get('soy_owgr')):
#    print (k, v)
#print (len(field))
exit()


t= Tournament.objects.get(current=True)
d = {}
for g in range(1,11):
    print (g)
    group_data = ScoreDetails.objects.filter(pick__playerName__tournament__season=season, pick__playerName__group__number=g).order_by('user').values('user__username').annotate(Sum('score'))
    for gd in group_data:
        #print (gd)
        if d.get(gd.get('user__username')):
            d.get(gd.get('user__username')).update({g: gd.get('score__sum')})
        else:
            d[gd.get('user__username')] = {g: gd.get('score__sum')}
    
    
for k, v in d.items():
    print (k, v)

for f in Field.objects.filter(tournament__current=True).order_by('soy_WGR'):
    print (f, ',', f.soy_WGR, ',', f.season_stats.get('fed_ex_rank'))


owgr = populateField.get_worldrank()
top_30 = {k:v for k,v in owgr.items() if int(v[2] <= 30)}
print (top_30, len(top_30))
fed_ex = populateField.get_fedex_data()

for k, v in top_30.items():
    print (k, ',', v[2], ',', fed_ex.get(k).get('rank'))


exit()
d = {'weak': {},
    'strong': {},
    'major': {}}

e = {}

for sd in ScoreDict.objects.filter(tournament__season__current=True).exclude(tournament__pga_tournament_num__in=['999', '470', '028']):  #018 zurich
    if sd.tournament.last_group_multi_pick():
        winner = [v.get('pga_num') for k,v in sd.data.items() if k != 'info' and v.get('rank') == '1']
        
        f = Field.objects.get(golfer__espn_number=winner[0], tournament=sd.tournament)
        #print (f, f.group.number)
        if d.get(sd.tournament.field_quality()).get(f.group.number):
            c = d.get(sd.tournament.field_quality()).get(f.group.number) + 1
            d.get(sd.tournament.field_quality()).update({f.group.number: c})
            
        else:
            d[sd.tournament.field_quality()][f.group.number] = 1
            
        if f.group.number == 6:
            if ScoreDetails.objects.filter(gross_score=1, pick__playerName__tournament=sd.tournament).exists():
                print ('G6 winner: ', sd.tournament, ScoreDetails.objects.filter(gross_score=1, pick__playerName__tournament=sd.tournament))
        if e.get(f.group.number):
            e.update({f.group.number: e.get(f.group.number) + 1 })
        else:
            e[f.group.number] = 1

        if f.group.number == 6:
            print (f.playerName, f.tournament)

for k, v in d.items():
    print(k, v)
print (e)

s = Season.objects.get(current=True)
users = s.get_users()
totals = {}

for u in users:
    u_obj = User.objects.get(pk=u.get('user'))
    g1 = ScoreDetails.objects.get(pick__)


exit()    
#t = Tournament.objects.get(current=True)
start = datetime.now()
espn_data = espn_api.ESPNData().get_all_data()

data= golf_serializers.NewFieldSerializer(Field.objects.filter(tournament=t, group__number=1), context={'espn_data': espn_data}, many=True).data
#print (datetime.now() - start)
print (data)

exit()
start1 = datetime.now()
espn_data = espn_api.ESPNData().get_all_data()

data= golf_serializers.NewFieldSerializer(Field.objects.filter(tournament=t), context={'espn_data': espn_data}, many=True).data
#print (datetime.now() - start)
print (len(data), datetime.now() - start1)

exit()

for k,v  in data.items():
    print (k)

exit()
espn = espn_api.ESPNData(mode='setup')
#print (espn.player_started('10548'))

for g in espn.field():
    print (g.get('athlete').get('displayName'))

#field = espn.field()
#print (field[0].get('id') == '10548')
owgr = populateField.get_worldrank()

field = populateField.get_field(t, owgr)

exit()
espn_data = espn_api.ESPNData().get_all_data()
start = datetime.now()
data= golf_serializers.NewFieldSerializer(Field.objects.filter(tournament=t), context={'espn_data': espn_data}, many=True).data
print (datetime.now() - start)
print (len(data))
 

golfers = espn_api.ESPNData().field()

#for g in golfers:
 #   print (g, g.get('status').get('period'), g.get('status').get('type').get('name'), g.get('status').get('type').get('shortDetail'))

exit() 

#     f_len = Field.objects.filter(tournament=t).count()
#     owgr_sum = Field.objects.filter(tournament=t).exclude(currentWGR=9999).aggregate(Sum('currentWGR'))
#     unranked = Field.objects.filter(tournament=t, currentWGR=9999).count()
#     top_100 = round(Field.objects.filter(tournament=t, currentWGR__lte=100).count()/f_len,2)
#     d[t.name] = {'avg_rank': round(int(owgr_sum.get('currentWGR__sum') + (unranked*2000))/f_len,0),
#                  'unranked_golfers': unranked,
#                  'top_100': top_100}

# sorted_d = sorted(d.items(), key=lambda v:v[1].get('avg_rank'))
# for k, v in sorted_d:
#     print (k,v)



sd = ScoreDict.objects.get(tournament=t)

scores = manual_score.Score(sd.data, t)
updated = scores.update_scores()
totals = scores.new_total_scores()
print (totals)
exit()



d = {}



users = season.get_users()
# tie = 0
# no_t = 0
# for sd in ScoreDict.objects.filter(tournament__season=season).exclude(tournament__current=True):
#     t2 = {k:v for k,v in sd.data.items() if k!='info' and v.get('rank') == "T2"}
#     t3 = {k:v for k,v in sd.data.items() if k!='info' and v.get('rank') == "T3"}
#     if len(t2) + len(t3) > 0:
#         tie += 1     
#         print (sd.tournament, len(t2) + len(t3))
#     else:
#         no_t += 1

# print ('tie: ', tie)
# print ('no tie:', no_t)






exit()                 

g = Golfer.objects.get(golfer_name="Hideki Matsuyama")
d = espn_api.ESPNData().player_started(g.espn_number)
e = Golfer.objects.get(golfer_name="Matt Wallace")
f = espn_api.ESPNData().player_started(e.espn_number)
#p = espn_api.ESPNData().picked_golfers()
#print (d)
print (f)
exit()

#golfer detail link  11098 is the espn_id
#http://sports.core.api.espn.com/v2/sports/golf/leagues/pga/events/401243408/competitions/401243408/competitors/11098/status?lang=en&region=us

#historic tournamanet link
#http://sports.core.api.espn.com/v2/sports/golf/leagues/pga/events/401243408

#current event 
#https://site.web.api.espn.com/apis/site/v2/sports/golf/leaderboard?league=pga

#info
#https://gist.github.com/akeaswaran/b48b02f1c94f873c6655e7129910fc3b

#t = Tournament.objects.get(current=True)
#print (t.get_country_counts())

espn_num = '401243404'  #Northern Trust

headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
url =  "https://site.web.api.espn.com/apis/site/v2/sports/golf/leaderboard?league=pga"

#payload = {'week':'1'}
jsonData = get(url, headers=headers).json()

#print ('dur ', datetime.now() - start)

f = open('espn_api.json', "w")
f.write(json.dumps(jsonData))
f.close()

#print('A', jsonData.get('events')[0].keys())
print ('start events keys')
for k, v in jsonData.get('events')[0].items():
    if k != 'competitions':
        print (k, v)
print ('end events keys')
for event in jsonData.get('events'):
    if event.get('id') == espn_num:
        #print (event)
        #continue

        for row in event.get('competitions'):
            print ('start Competions keys')
            print ('field len', len(row.get('competitors')))
            for k, v in row.items():
                if k != 'competitors':
                    print (k, v)
                    print ('================================================')
            print ('end Competions keys')
        
            #print ('B', row.items())
            #print ('status', row.get('holeByHoleSource'))
            for c in row.get('competitors'):
                continue
                #print (c.get('id'), ' ', c.get('athlete').get('displayName'))
                #print (c.get('status'))
                #if c.get('athlete').get('displayName') in ["Hideki Matsuyama", "Abraham Ancer"]:
                #    print (c)
                #    for k, v in c.items():
                #        if k == 'linescores':
                #            for l in v:
                #                #print (l) 
                #                print (' ')
                ##        else:
                #           print (k, v)
                #print  (c)
        #print ('------------------------------------')
    
exit()

d = {}
for sd in ScoreDict.objects.filter(tournament__season__current=True).exclude(tournament__pga_tournament_num__in=['470', '999']):
    winner = [v.get('pga_num') for k,v in sd.data.items() if k != 'info' and v.get('rank') == '1'][0]
    
    golfer  = Golfer.objects.get(espn_number=winner)
    if d.get(golfer.country()):
        d.update({golfer.country(): d.get(golfer.country()) + 1})
    else:
        d[golfer.country()] = 1
print (d)

pd = {}
c = {}
s = Season.objects.get(current=True)
users = s.get_users()
for u in users:
    pd[User.objects.get(pk=u.get('user'))] = {}
try:
    for p in Picks.objects.filter(playerName__tournament__season__current=True):
        f = Field.objects.get(playerName=p.playerName, tournament=p.playerName.tournament)
        if pd.get(p.user).get(f.golfer.country()):
            pd.get(p.user).update({f.golfer.country(): pd.get(p.user).get(f.golfer.country()) + 1})
        else:
            pd.get(p.user).update({f.golfer.country(): 1})

        if c.get(f.golfer.country()):
            c.update({f.golfer.country(): c.get(f.golfer.country()) + 1})
        else:
            c[f.golfer.country()] = 1
except Exception as e:
    print ('failed ', p, p.user)

print (pd)
print (c)

exit()

mens_field = scrape_espn.ScrapeESPN(tournament=t, url='https://www.espn.com/golf/leaderboard?tournamentId=401285309', setup=True).get_data() 
mens_field['mens_info'] = mens_field.get('info')   
womens_field = scrape_espn.ScrapeESPN(tournament=t, url="https://www.espn.com/golf/leaderboard/_/tour/womens-olympics-golf", setup=True).get_data()
womens_field['womens_info'] = womens_field.get('info')

#mens_field = scrape_espn.ScrapeESPN(tournament=t, url='https://www.espn.com/golf/leaderboard?tournamentId=401285309', setup=True).get_data()    
#womens_field = scrape_espn.ScrapeESPN(tournament=t, url="https://www.espn.com/golf/leaderboard/_/tour/womens-olympics-golf", setup=True).get_data()
score_dict = {**mens_field, **womens_field}
if not mens_field.get('info').get('complete'):
    if mens_field.get('info').get('round') > 1:
        info = mens_field.get('info')
        score_dict['info'] = mens_field.get('info')
        score_dict['info']['round_status'] = score_dict.get('info').get('round_status') + " - Mens"

#score_dict.get('info') = mens_field.get('info')
#print (score_dict)
#print (score_dict.get('info'))
#print (mens_field.get('info'))
print (womens_field)
print (score_dict.get('info'))
print (score_dict.get('mens_info'))
print (score_dict.get('womens_info'))
exit()

f = open('lpga_links.json',)
print (type(f))
lpga_data = json.load(f)

for g in Golfer.objects.filter(golfer_pga_num=''):
    print (g)
    link = [v for k,v in lpga_data.items() if g.golfer_name == k.replace('\xa0', ' ')]

    if len(link) == 1:
        print (link)
        pic_link = link[0].get('pic_link')
        print (g, pic_link)
        g.pic_link = pic_link
        g.save()
    else:
        print (g, 'no pic')

exit()

req = Request("https://www.lpga.com/players", headers={'User-Agent': 'Mozilla/5.0'})
html = urlopen(req).read()
   
soup = BeautifulSoup(html, 'html.parser')
#print (soup)
golfers = (soup.find("div", {'id': 'topMoneyListTable'}))
d = {}

for row in golfers.find_all('tr')[1:]:
    try:
        name = row.find_all('td')[1].text.strip()
        lpga_link = str('https://lpga.com/') + row.find_all('td')[1].find('a')['href'].replace(' ', '%20')
        
        
        dtl_req = Request(lpga_link, headers={'User-Agent': 'Mozilla/5.0'})
        dtl_html = urlopen(dtl_req).read()
    
        dtl_soup = BeautifulSoup(dtl_html, 'html.parser')
        #print (soup)
        try:
            pic = str('https://lpga.com') + dtl_soup.find("div", {'class': 'player-banner-gladiator'}).find('img')['src']
        except Exception:
            pic = ''
            print ('no picture', name)
        print (name, pic)
        d[name] = {'link': str('https://www.lpga.com/') + str(lpga_link), 'pic_link': pic}
    except Exception as e:
        print (e)        
with open('lpga_links.json', 'w') as convert_file:
     convert_file.write(json.dumps(d))

#with open('lpga_links.csv', 'w', newline='') as csvfile:
#    csvwriter = csv.writer(csvfile, delimiter=',',
#                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
#    for k, v in d.items():

#        csvwriter.writerow([k, v.link, v.pic_link])

#csvfile.close()


exit()
    

#t = populateField.setup_t('999')
t = Tournament.objects.get(pga_tournament_num='999')
#print (scrape_espn.ScrapeESPN(tournament=t, url="https://www.espn.com/golf/leaderboard/_/tour/womens-olympics-golf", setup=True).get_data())

for f in Field.objects.filter(tournament__pga_tournament_num='999').order_by('currentWGR'):
    print (f, f.currentWGR)
    print (f.golfer, f.golfer.espn_number)
exit()
print (Field.objects.filter(tournament__pga_tournament_num='999').count())

for g in Group.objects.filter(tournament=t):
    print (g, g.playerCnt)
    print (Field.objects.filter(group=g).count())
exit()
#t = populateField.setup_t('999')
#print (scrape_espn.ScrapeESPN(tournament=t, url='https://www.espn.com/golf/leaderboard?tournamentId=401285309', setup=True).get_data())
print (scrape_espn.ScrapeESPN(tournament=t, url="https://www.espn.com/golf/leaderboard/_/tour/womens-olympics-golf", setup=True).get_data())
#print (populateField.get_womans_rankings())
#exit()
#t = populateField.setup_t('999')
t = Tournament.objects.get(pga_tournament_num=999)
ranks = populateField.get_worldrank()
field = populateField.get_field(t,ranks)
#print (field, len(field))
print (len(field))
exit()

f = Field.objects.get(playerName="Dustin Johnson", tournament__current=True)
for k, v in f.season_stats.items():
    print (k, v)

# d = {}

# for stat in StatLinks.objects.all():
#     #url = 'https://www.pgatour.com/stats/stat.02569.html'

    
#     html = urllib.request.urlopen(stat.link)
#     soup = BeautifulSoup(html, 'html.parser')
            
#     for row in soup.find('table', {'id': 'statsTable'}).find_all('tr')[1:]:
#     #print (row)
#     #print(row.find('td', {'class': 'player-name'}).text.strip())
#         if d.get(row.find('td', {'class': 'player-name'}).text.strip()):
#             d[row.find('td', {'class': 'player-name'}).text.strip()].update({stat.name: {
#                                                                 'rank': row.find_all('td')[0].text.strip(),
#                                                                 'rounds': row.find_all('td')[3].text,
#                                                                 'average': row.find_all('td')[4].text,
#                                                                 'total_sg': row.find_all('td')[5].text,
#                                                                 'measured_rounds': row.find_all('td')[6].text}})
#         else:
#             d[row.find('td', {'class': 'player-name'}).text.strip()] = {'pga_num': row.get('id').strip('playerStatsRow')}
#             d[row.find('td', {'class': 'player-name'}).text.strip()].update( 
#                                                                 {stat.name: {'rank': row.find_all('td')[0].text.strip(),
#                                                                 'rounds': row.find_all('td')[3].text,
#                                                                 'average': row.find_all('td')[4].text,
#                                                                 'total_sg': row.find_all('td')[5].text,
#                                                                 'measured_rounds': row.find_all('td')[6].text}})


# print (d['Kevin Na'], len(d))

exit()


#season = Season.objects.get(current=True)
#t = Tournament.objects.get(current=True)
#print (season.get_total_points(t))
#exit()

for t in Tournament.objects.filter(season__current=True):
    #picks = Picks.objects.filter(playerName__tournament=t).values('playerName__playerName').annotate(count=Count('playerName')).order_by('-count')
    #for p in picks:
    #    print (p)
    all_picks = Picks.objects.filter(playerName__tournament=t).aggregate(Count('playerName', distinct=True))
    tot_picks = Picks.objects.filter(playerName__tournament=t).count()
    g_5 = Picks.objects.filter(playerName__tournament=t, playerName__group__number=6).aggregate(Count('playerName', distinct=True))
    tot_g5 = Picks.objects.filter(playerName__tournament=t, playerName__group__number=6).count()
    print (t, all_picks, tot_picks, g_5, tot_g5)
    #print (t, '  ', Picks.objects.filter(playerName__tournament=t).aggregate(Count('playerName', distinct=True)))
    #print (t, '  ', Picks.objects.filter(playerName__tournament=t, playerName__group__number=6).aggregate(Count('playerName', distinct=True)))
exit()

started = 0
not_start = 0
sd = scrape_espn.ScrapeESPN().get_data()
#scores = ScoreDict.objects.get(tournament__current=True)
#sd = scores.data
for f in Field.objects.filter(tournament__current=True):
    if f.started(sd):
        #print (f)
        started += 1
    else:
        print (f)
        not_start += 1

print ('started: ', started)
print ('not started: ', not_start)
exit()
for sd in ScoreDict.objects.filter(tournament__season__current=True):
    if not sd.data.get('info'):
        print ('no info ', sd.tournament)
    elif sd.data.get('info').get('source') != 'espn':
        print ('not espn ', sd.tournament)
    #else:
    #    print ('final ', sd.tournament)

exit()

sd = ScoreDict.objects.get(tournament__current=True)
print (sd.sorted_dict())
exit()
for f in Field.objects.filter(playerName__in=["Scott Brown", "Mark Hubbard", "Rickie Fowler"], tournament__current=True):
    print (f.playerName, f.playing(sd.data))
print (datetime.now() - start)



exit()
t_diff = 0

for t in Tournament.objects.filter(season__current=True):
    ts = TotalScore.objects.filter(tournament=t).order_by('score')
    if ts[1].score != ts[0].score:
        diff = ts[1].score - ts[0].score 
    else:
        diff = ts[2].score - ts[0].score 
    
    t_diff += diff
    if t.major:
        t_diff -= 100

print (t_diff, Tournament.objects.filter(season__current=True).count())
print (t_diff/Tournament.objects.filter(season__current=True).count())
exit()


for a in AccessLog.objects.filter(page='picks'):
    print (a, a.device_type)

exit()

fedex = populateField.get_fedex_data()
for golfer, data  in fedex.items():
       print (golfer, data)
exit()

g = Golfer.objects.get(golfer_name='Dustin Johnson')
print (g.get_pga_player_link())
print (g.get_fedex_stats())
exit()

flag = populateField.get_flag('45526', 'Abraham Ancer')
print (flag)
stats = populateField.get_fedex_stats('45526', 'Abraham Ancer')
print (stats)

exit()

for g in Golfer.objects.filter(golfer_name='Antoine Rozner'):
    for k, v in g.results.items():
        print (k, v)
#for g in Golfer.objects.all():
    
    #mp = g.results.get('153')
    #if mp.get('rank') != 'n/a':
    #    print (g, mp.get('rank'))
        #print (k, r.get('t_name'), r.get('rank'))

sd = ScoreDict.objects.get(tournament__pk=153)
print (sd.data.get('Antoine Rozner'))

start = datetime.now()

exit()

t = Tournament.objects.get(pga_tournament_num=538, season__current=True)
sd = ScoreDict.objects.get(tournament=t)

web = scrape_espn.ScrapeESPN(t, 'https://www.espn.com/golf/leaderboard?tournamentId=401317529', True, False).get_data()
sd.data = web
sd.save()


for f in Field.objects.filter(tournament__current=True):
    f.recent = f.recent_results()
    f.prior_year = f.prior_year_finish()
    f.save()

print ('field done')

for g in Golfer.objects.all():
    g.get_season_results(rerun=True)

print (datetime.now() - start)

exit()

for t in Tournament.objects.filter(season__current=True):
    sd = ScoreDict.objects.get(tournament=t)
    if not sd.data.get('info') and not ("Masters" in t.name or "Match Play" in t.name):
        print ('NAME: ', t.name)
        t_num = scrape_espn.ScrapeESPN(tournament=t).get_t_num(season=t.season)
        #print (t, t_num)
        # if (not created and (not sd.data or len(sd.data) == 0 or len(pga_nums) == 0)) or created:
        # print ('updating prior SD', prior_t)
        # espn_t_num = scrape_espn.ScrapeESPN().get_t_num(prior_season)
        url = "https://www.espn.com/golf/leaderboard?tournamentId=" + t_num
        score_dict = scrape_espn.ScrapeESPN(t,url, True, True).get_data()
        sd.data = score_dict
        #sd.save()
        t.espn_t_num = t_num
        #t.save()

exit()
#Masters
t = Tournament.objects.get(season__current=True, pga_tournament_num='014')
t_num = '401219478'
url = "https://www.espn.com/golf/leaderboard?tournamentId=" + t_num
score_dict = scrape_espn.ScrapeESPN(t,url, True, True).get_data()
sd.data = score_dict
sd.save()
t.espn_t_num = t_num
t.save()

#Zozo
t = Tournament.objects.get(season__current=True, pga_tournament_num='527')
t_num = '401219797'
url = "https://www.espn.com/golf/leaderboard?tournamentId=" + t_num
score_dict = scrape_espn.ScrapeESPN(t,url, True, True).get_data()
sd.data = score_dict
sd.save()
t.espn_t_num = t_num
t.save()




exit()


start = datetime.now()
g = Golfer.objects.get(golfer_name="Justin Thomas")
r= g.get_season_results(Season.objects.get(current=True), rerun=True)
for k, v in r.items():
    print (v)
exit()

#for a in AccessLog.objects.filter(user__username__startswith='j_b').order_by('updated'):
#    print (a.updated, a.page)

#print (Field.objects.filter(tournament__current=True).count())
#t_keys = list(Tournament.objects.filter(season__current=True).values_list('pk', flat=True))
#g = Golfer.objects.get(golfer_name='Justin Thomas')
#print (t_keys)
#for g in Golfer.objects.all():
#    g.results =  g.get_season_results()
#    g.save()

#data = g.get_season_results()
#print (data)
#print (164 in data.keys())
#print (127 in data.keys())

#data = golf_serializers.GolferSerializer(Golfer.objects.all(), many=True)
#print (data.data)
#for g in data.data:
#    print (g)

print (datetime.now() - start)
exit()




score_dict = scrape_espn.ScrapeESPN().get_data()
totals = {}
t = Tournament.objects.get(current=True)
for u in User.objects.filter(username__in=['john', 'jcarl62', 'ryosuke']):
    totals[u.username] = {'total': 0}
for pick in AuctionPick.objects.filter(playerName__tournament=t):
    sd = [v for v in score_dict.values() if v.get('pga_num') == pick.playerName.golfer.espn_number]
    print (pick, utils.formatRank(sd[0].get('rank')))
    if int(utils.formatRank(sd[0].get('rank'))) > score_dict.get('info').get('cut_num'):
        total = totals[pick.user.username].get('total') + int(score_dict.get('info').get('cut_num'))
        rank = rank = (score_dict.get('info').get('cut_num'))
    else:
        total = totals[pick.user.username].get('total') + int(utils.formatRank(sd[0].get('rank')))
        rank = utils.formatRank(sd[0].get('rank'))
    totals[pick.user.username].update({pick.playerName.playerName : rank,
                                        'total': total
                                         })



for k, v in sorted(totals.items(), key= lambda v:v[1].get('total')):
    print (k, v)
print (datetime.now() - start)
exit()

start = datetime.now()

with open('joe.csv', 'w', newline='') as f:
    # create the csv writer
    writer = csv.writer(f)

    header = ['Tournament', 'Group', 'Golfer', 'Current OWGR', 'Last Week OWGR', 'End of last year OWGR', 'Recent Tournament 1', 'Recent Toounament 1 result' \
                , 'Recent Tournament 2', 'Recent Toounament 2 result'
                , 'Recent Tournament 3', 'Recent Toounament 3 result'
                , 'Recent Tournament 4', 'Recent Toounament 4 result'
                ]
    writer.writerow(header)

    for t in Tournament.objects.filter(season__current=True).order_by('-pk')[:3]:
        for f in Field.objects.filter(tournament=t):
            line = []
            line.append(t.name)
            line.append(f.group.number)
            line.append(f.playerName)
            line.append(f.currentWGR)
            line.append(f.sow_WGR)
            line.append(f.soy_WGR)
            for k, v in f.recent.items():
                line.append(v.get('name'))
                line.append(v.get('rank'))
            print (line)
            writer.writerow(line)

exit()


for t in Tournament.objects.filter(season=season):
    ts = list(TotalScore.objects.filter(tournament=t).order_by('user__pk').values_list('score', flat=True))
    ranks = ss.rankdata(ts, method='min')
    for i, (k,v) in enumerate(d.items()):
        print (d[i])
    #print (t, ts)
    #print (ranks)
    
    

print (d)
exit()
g = Group.objects.filter(tournament=tournament).aggregate(Max('number'))
print (g)
exit()
t = Tournament.objects.get(current=True)
g = Golfer.objects.get(golfer_name='Ryan Palmer')
print (g.summary_stats(t.season))
exit()
for f in Field.objects.filter(tournament=t):
    loop_start = datetime.now()
    print (f.golfer.summary_stats(t.season))
    print (f, datetime.now() - loop_start)

print (datetime.now() - start)
exit()
print (web)

web1 = scrape_espn.ScrapeESPN(None, None, False, True).get_data()


#sd = ScoreDetails.objects.filter(pick__playerName__tournament=t)
#print (sd.values_list('pick__playerName__golfer__espn_number', flat=True).distinct(), len(sd.values_list('pick__playerName__golfer__espn_number', flat=True).distinct()))

exit()
for sd in ScoreDetails.objects.filter(pick__playerName__tournament=t, user__username__startswith="shi"):
    print (sd, sd.sod_position)
exit()
sd =ScoreDict.objects.get(tournament=t)
web = scrape_espn.ScrapeESPN().get_data()
print ('---------------')
print (sd.data.get('info'))
print (web.get('info'))

start_1 = datetime.now()
print ('1', {k:v for k,v in sd.data.items() if k != 'info'} == \
    {k:v for k,v in web.items() if k != 'info'})
print ('dur 1:', datetime.now() - start_1)
start_2 = datetime.now()
print ('2', {k:v for k,v in sd.data.get('info').items() if k != 'dict_status'} == \
    {k:v for k,v in web.get('info').items() if k != 'dict_status'})
print ('dur 2:', datetime.now() - start_2)
#print (sd.data == web)
#print (sd.data.get('info'))
#print (web.get('info'))
#print ({k:v for k,v in sd.data.items() if v != v.get('dict_status')})
#sorted_score_dict = {k:v for k, v in sorted(sd.data.items(), if k != 'info' key=lambda item: item[1].get(utils.formatRank(item[1].get('rank'))))}
#print (sorted_score_dict)




exit()


#for user in user_pks:
#    u = User.objects.get(pk=user.get('user'))
#    picks = manual_score.Score(None, t, 'json').get_picks_by_user(u)
#    print (u, picks)

print ('loop dur: ', datetime.now() - start)

serialize_start = datetime.now()
#models = [*ScoreDetails.objects.filter(pick__playerName__tournament=t), *Picks.objects.filter(playerName__tournament=t)]
#data = serializers.serialize('json', models)
data = golf_serializers.ScoreDetailsSerializer('json', ScoreDetails.objects.filter(pick__playerName__tournament=t), many=True)
print (type(data.data))
#for d in data.initial_data:
#    print(type(d))
#    print (d)
print ('serialize dur: ', datetime.now() - serialize_start)
exit()



web1 =  scrape_scores_picks.ScrapeScores(t, 'https://www.pgatour.com/competition/2021/wgc-dell-technologies-match-play/group-stage.html').mp_brackets() 
web = scrape_scores_picks.ScrapeScores(t, 'https://www.pgatour.com/competition/2021/wgc-dell-technologies-match-play/leaderboard.html').mp_final_16()
print (web1)
exit()
#with open('owgr.json') as f:
#  owgr = json.load(f)
for sd in ScoreDict.objects.all():
    #print (sd.tournament)
    solo_2 = {k:v for k,v in sd.data.items() if v.get('rank') =='2'}
    solo_3 = {k:v for k,v in sd.data.items() if v.get('rank') =='3'}
    if len(solo_2) > 0 and len(solo_3) > 0:
        print (sd.tournament, sd.tournament.season)
        print (solo_2)
        print (solo_3)
        print ('-----------------------')
exit()
sds = ScoreDetails.objects.filter(pick__playerName__tournament=t)
print (sd)

exit()
for t in Tournament.objects.all():
    sd = ScoreDetails.objects.filter(pick__playerName__tournament=t).values('user').annotate('score')
    print (sd)
    if len(sd) < 0:
        print (sd)

exit()
t = Tournament.objects.get(current=True)
with open('owgr.json') as f:
  owgr = json.load(f)
#owgr = populateField.get_worldrank()
#owgr = {}
field  = populateField.get_field(t, owgr)
sorted_field = {k:v for k,v in sorted(field.items(), key=lambda item:item[1].get('curr_owgr'))}
print (sorted_field)
exit()
#print (Field.objects.filter(tournament__current=True).count())
f = Field.objects.get(tournament=t, playerName__startswith="By")
print (f, f.recent_results())
exit()


#cbs_web = scrape_cbs_golf.ScrapeCBS().get_data()
#pga_web = scrape_scores_picks.ScrapeScores().scrape_zurich()
#print (pga_web)
#print ('PGA: ', pga_web['info'])
#print ('PGA: ', pga_web['Cameron Smith'])
#print ('CBS: ', cbs_web['info'])
#print ('CBS: ', cbs_web['Cameron Smith'])
#t = Tournament.objects.get(current=True)
#f_start  = datetime.now()
#for pick in Picks.objects.filter(playerName__tournament=t):
    #print (pick)
#    web.get(unidecode(pick.playerName.playerName)).update({'group': pick.playerName.group.number})
    #print (web.get(pick.playerName.playerName))
#print ('duration: ', datetime.now() - start)
#print (web['info'])
exit()





#for player in data['Tournament']['Players']:
#for player in ['Ted Potter, Jr.', ]:
#    name = (' '.join(reversed(player["PlayerName"].rsplit(', ', 1))))
#    print (player.get('PlayerName'), player.get('TournamentPlayerId'), utils.fix_name(name, owgr))
print (utils.fix_name('Ted Potter, Jr.', owgr))


exit()




field = scrape_espn.ScrapeESPN().get_field()
#players = scrape_espn.ScrapeESPN().get_espn_players()
for k, v in field.items():
    print (k, v)
print (len(field))
print (Field.objects.filter(tournament__current=True).count())

exit()

f = Field.objects.get(tournament__current=True, playerName='Matt Kuchar')
print (f.recent_results())
print (datetime.now() - start)
print (f.prior_year_finish())
print (datetime.now() - start)
exit()
def get_mp_result(f, sd):
    #winner = {k:v for k, v in sd.data.items() if k == 'Finals' and {num:match for num, match in v.items() if match.get('winner') == f.playerName}}
    if {k:v for k, v in sd.data.items() if k == 'Finals' and {num:match for num, match in v.items() if match.get('winner') == f.playerName}}:
        return 1 
    elif {k:v for k, v in sd.data.items() if k == 'Finals' and {num:match for num, match in v.items() if match.get('loser') == f.playerName}}:
        return 2
    elif {k:v for k, v in sd.data.items() if k == '3rd Place' and {num:match for num, match in v.items() if match.get('winner') == f.playerName}}:
        return 3
    elif {k:v for k, v in sd.data.items() if k == '3rd Place' and {num:match for num, match in v.items() if match.get('loser') == f.playerName}}:
        return 4
    elif {k:v for k, v in sd.data.items() if k == 'Quaterfinals' and {num:match for num, match in v.items() if match.get('loser') == f.playerName}}:
        return 5
    elif {k:v for k, v in sd.data.items() if k == 'Round of 16' and {num:match for num, match in v.items() if match.get('loser') == f.playerName}}:
        return 9
    else:
        return 17



t = Tournament.objects.get(season__current=True, pga_tournament_num='470')
sd = ScoreDict.objects.get(tournament=t)



for f in Field.objects.filter(tournament=t):
    print (f.playerName, get_mp_result(f, sd))

print (datetime.now() - start)
