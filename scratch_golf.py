import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from golf_app.models import Tournament, TotalScore, ScoreDetails, Picks, PickMethod, BonusDetails, Season, Golfer, Group, Field, ScoreDict, AuctionPick, AccessLog
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
from golf_app import views, manual_score, populateField, withdraw, scrape_scores_picks, utils, scrape_cbs_golf, scrape_masters, scrape_espn, update_favs
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



start = datetime.now()

u_list = []
season = Season.objects.get(current=True)

for u in season.get_users():
    user = User.objects.get(pk=u.get('user'))
    u_list.append(user.email)

print (u_list)
print (os.environ.get("DEBUG"))

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
