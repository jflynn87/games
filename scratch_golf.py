import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from golf_app.models import Tournament, TotalScore, ScoreDetails, Picks, PickMethod, BonusDetails, Season, Golfer, Group, Field, ScoreDict
from django.contrib.auth.models import User
from datetime import datetime, timedelta
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
import collections


start = datetime.now()

#print (scrape_espn.ScrapeESPN(None, None, True).get_data())
#t = Tournament.objects.get(pk=24) #Match Play

t = Tournament.objects.get(current=True)
#web = scrape_scores_picks.ScrapeScores(t, 'https://www.pgatour.com/competition/2019/wgc-dell-technologies-match-play/group-stage.html').mp_brackets()
web = scrape_espn.ScrapeESPN().get_mp_data()
print (web)
print (len(web))
exit()
sd = ScoreDict.objects.get(tournament=t)
#sd.cbs_data = web
#sd.save()
bracket = sd.cbs_data
#print (bracket.items())
for f in Field.objects.filter(tournament=t):
    #k = f.playerName.rstrip()
    for k, v in bracket.items():
        if k.split(' ')[1] == f.playerName.split(' ')[1]:
            print (k, v)
#print (populateField.get_field("470"))
exit()



sd = {}
golfers = {}
pick_per = ScoreDetails.objects.filter(pick__playerName__tournament=t).values('pick__playerName', 'score').annotate(Count('pick__playerName'))
for g in Golfer.objects.all():
    golfers[g.golfer_name] = {'espn_num': g.espn_number}

#print ({k:v for k,v in golfers.items() if k.startswith('O')})
for p in pick_per:
    #print (Field.objects.get(pk=p.get('pick__playerName')), p.get('score'))
    f = Field.objects.get(pk=p.get('pick__playerName'))
    num = utils.fix_name(f.playerName.rstrip(), golfers)
    try:
        espn = num[1].get('espn_num')
        score = p.get('score')
    except Exception as e:
        espn = ''
        score = ''
    
    sd.update({f.playerName: {
        'pga_num': espn,
        'rank': score
    }})

print (sd)
sd_o = ScoreDict()
sd_o.tournament = t
sd_o.data = sd
sd_o.save()

exit()



scores = ScoreDict.objects.get(tournament=t)
print (scores.data)
c = len([v for k, v in scores.data.items() if v.get('round_score') not in ['--', '-', None]])
print (c)
exit()

print (Field.objects.filter(tournament=t).count())    
print (Group.objects.filter(tournament=t).count())

for g in Group.objects.filter(tournament=t):
    print ('Group: ', g.number)
    for f in Field.objects.filter(group=g):
        print (f, f.currentWGR)


#for sd in ScoreDetails.objects.filter(pick__playerName__tournament=t).order_by('score'):
#    print (sd)


url = 'https://www.espn.com/golf/leaderboard?tournamentId=401056524'
html = urllib.request.urlopen(url)
soup = BeautifulSoup(html, 'html.parser')
            
leaderboard = soup.find('div', {'class': 'MatchPlay__Group'})
groups = leaderboard.find_all('div', {'class': 'MatchPlay__Match'})
#for g in groups:
#    print (g)




exit()

#sd = populateField.prior_year_sd(t)
#print ({k:v for k,v in sd.items() if v.get('rank') == str(1)})

#f = Field.objects.get(tournament=t, playerName='Justin Rose')
#Picks.objects.filter(playerName__tournament=t, playerName__playerName='Victor Perez').update(playerName=f)
#print (t.started())
#names = scrape_espn.ScrapeESPN().get_t_num(Season.objects.get(season='2020'))
#print (names)
#sd  = scrape_espn.ScrapeESPN(None, None, True).get_data()
#f = open('just_started', 'w')
#f.write(json.dumps(sd))
#f.close()

#web = scrape_espn.ScrapeESPN(None, None, True, False).get_data()
#scores = manual_score.Score(web, t)

#sd = ScoreDict.objects.get(tournament=t)
#scores = manual_score.Score(sd.data, t)

#print (web)
# 
# #for g in Group.objects.filter(tournament=t):
#    print ('grp ', g.number, ' ', scores.worst_picks(g.number))

print ('By score:')
for g in Group.objects.filter(tournament=t):
    print ('grp ', g.number, ' ', scores.worst_picks_score(g.number))


exit()
#avs = update_favs.UpdateFavs().scrape() 
t = Tournament.objects.get(current=True)

f = Field.objects.get(tournament=t, playerName="Dustin Johnson")
print (f.recent)
print ('-----')
print (collections.OrderedDict(sorted(f.recent_results().items(), reverse=True)))
print ('-----')
#m = sorted(sd.values(), key = lambda data: (sum(formatRank(data['rank']), data['handicap'])))
data = json.dumps(golf_serializers.NewFieldSerializer(Field.objects.filter(tournament=t, playerName="Dustin Johnson"),  many=True).data)
print (data)
exit()
#for f in Field.objects.filter(tournament=t):
#    data = golf_serializers.FieldSerializer(f).data
#for g in Group.objects.filter(tournament=t):
#    g_start = datetime.now()

#print (g, datetime.now() - g_start)
#data = golf_serializers.FieldSerializer(Field.objects.filter(tournament=t), many=True).data
#j_data = json.dumps(data)
print (data)
print (data.get('recent'))
print (datetime.now() - start)
exit()



pga_list = []
espn_list = []

for g in Golfer.objects.all():
    if g.espn_number:
        espn_list.append(g.espn_number)
    if g.golfer_pga_num:
        pga_list.append(g.golfer_pga_num)

for n in espn_list:
    if n in pga_list:
        print('espn: ', Golfer.objects.get(espn_number=n))
        print('pga: ', Golfer.objects.get(golfer_pga_num=n))

for m in pga_list:
    if m in espn_list:
        print('espn: ', Golfer.objects.get(espn_number=m))
        print('pga: ', Golfer.objects.get(golfer_pga_num=m))
        
exit()

start = datetime.now()
#cur_t = Tournament.objects.get(current=True)
print (Tournament.objects.all().order_by('-pk')[1:5])
for t in Tournament.objects.all().order_by('-pk')[1:5]:
    if Field.objects.filter(tournament=t, playerName="Phil Mickelson").exists():
        f = Field.objects.get(tournament=t, playerName="Phil Mickelson")
        sd = ScoreDict.objects.get(tournament=t)
        x = [v.get('rank') for k, v in sd.data.items() if k !='info' and v.get('pga_num') in [f.golfer.espn_number, f.golfer.golfer_pga_num]]
        print (t, f, x)
    else:
        print (t, 'dnp')

exit()



for f in Field.objects.filter(tournament=t, playerName="Phil Mickelson"):
    print (f, f.prior_year_finish())

print (datetime.now() - start)

exit()

last_yr = Tournament.objects.get(pga_tournament_num='005', season__season='2020')
sd = ScoreDict.objects.get(tournament=last_yr)
print (sd.data.get('Phil Mickelson  (PB'))
exit()



u = User.objects.get(pk=1)
print (u)
#print (Field.objects.filter(tournament=t, golfer__espn_number__isnull=True))
g = scrape_espn.ScrapeESPN().get_data()
scores = manual_score.Score(g, t).update_scores_player(u)
print (datetime.now() - start)
for sd in ScoreDetails.objects.filter(pick__playerName__tournament=t, user=u):
    print (sd.pick.playerName, sd.score)
exit()

d = {}
season = Season.objects.get(current=True)
for u in season.get_users():
    user = User.objects.get(pk=u.get('user'))
    d[user.username] = {'f5_wins': 0,
                        't_wins': 0,
                        'f5_total': 0,
                        't_total':0}

#print (d)

first_5 = ScoreDetails.objects.filter(pick__playerName__tournament__season__current=True, pick__playerName__group__number__lt=6) \
            .values('pick__playerName__tournament__name', 'user__username').annotate(Sum('score'))
total = ScoreDetails.objects.filter(pick__playerName__tournament__season__current=True) \
            .values('pick__playerName__tournament__name', 'user__username').annotate(Sum('score'))
#print (first_5)
#print (total)
    
#    t = total.filter(pick__playerName__tournament__name=s.get('pick__playerName__tournament__name'), user__username=s.get('user__username'))
    #print (t)
for t in Tournament.objects.filter(season__current=True):
    #print (t)
    f_5 = first_5.filter(pick__playerName__tournament__name=t.name).order_by('score__sum').first()
    f5_w = f_5.get('user__username')
    tot = total.filter(pick__playerName__tournament__name=t.name).order_by('score__sum').first()
    t_w = tot.get('user__username')

    d[f5_w]['f5_wins'] = d[f5_w]['f5_wins'] + 1
    d[t_w]['t_wins'] = d[t_w]['t_wins'] + 1

    for s in first_5.filter(pick__playerName__tournament__name=t.name):
        d[s['user__username']]['f5_total'] = d[s['user__username']]['f5_total'] + s.get('score__sum')

    for s in total.filter(pick__playerName__tournament__name=t.name):
        d[s['user__username']]['t_total'] = d[s['user__username']]['t_total'] + s.get('score__sum')


sd = dict(sorted(d.items(), key=lambda item:int(item[1]['f5_total'])))

for k,v in sd.items():
    print (k, v)

exit()


#s = Season.objects.get(current=True)
t = Tournament.objects.get(current=True)
#print (Field.objects.filter(tournament=t, golfer__espn_number__isnull=True))
g = scrape_espn.ScrapeESPN().get_data()
print (g)
#print (len([v for k, v in g.items() if v.get('round_score') not in ['--', '-', None]]))
#f = open('r2-inprog.json', 'w')
#f.write(json.dumps(g))
#f.close()
#wd = withdraw.WDCheck().check_wd()
#print (g.get('Patrick Reed'))

exit()
g = scrape_espn.ScrapeESPN().get_espn_players()
#print (g)


user=User.objects.get(username="Ryosuke")
print (ScoreDetails.objects.filter(pick__playerName__tournament=t, user=user).aggregate(Sum('score')))
bd = BonusDetails.objects.get(tournament=t, user=user)
print (bd.best_in_group_bonus, bd.winner_bonus, bd.playoff_bonus)

for bd in BonusDetails.objects.filter(tournament=t):
    bd.winner_bonus = 0
    bd.playoff_bonus = 0
    bd.best_in_group_bonus = 0
    bd.save()

exit()


# print (Field.objects.filter(tournament=t, golfer__espn_number__isnull=True).count())


# for golfer in Field.objects.filter(tournament=t, golfer__espn_number__isnull=True):
#     print (golfer.playerName,  utils.fix_name(golfer.playerName, g))
#     try:
#         num = utils.fix_name(golfer.playerName, g).get('espn_num')
#     except Exception as e:
#         num = utils.fix_name(golfer.playerName, g)[1].get('espn_num')
    
#     g_obj = Golfer.objects.get(golfer_pga_num=golfer.golfer.golfer_pga_num)
#     g_obj.espn_number = num
#     g_obj.save()

#print (len(f.filter(golfer__espn_number__isnull=True)))
exit()
# pick = Picks.objects.get(playerName=f, user__pk=1)
# sd = ScoreDetails.objects.get(pick=pick)
# print ('pick_score: ', pick.score)
# print (sd.score, 
#     sd.toPar,
#     sd.today_score,
#     sd.thru,
#     sd.sod_position,
#     sd.gross_score)





web = scrape_espn.ScrapeESPN().get_data()
#score = manual_score.Score(web, t)
#optimal = score.optimal_picks(6) 
print (web)
exit()
#web = withdraw.WDCheck().check_wd()
#print (web)

#for k, v in web.items():
#     if k != 'info':
        
#         if Field.objects.filter(golfer__espn_number=v['pga_num']).exists():
#             pass
#         else:
#             print ('in dict, nit field: ', k, v)

# for f in Field.objects.filter(tournament__current=True):
#     if f.golfer.espn_number in [v['pga_num'] for k, v in web.items() if v.get('pga_num') == f.golfer.espn_number]:
#         pass
#     else:
#         print ('in field, not in dict: ', f)
    

#web = populateField.get_espn_field(t)
#print (web)

print (datetime.now() - start)


exit()



golfers = list(t.season.get_users())
user = User.objects.get(username='milt')
print (golfers, type(golfers))
print ([x for x in golfers if x.get('user') == user.pk])
exit()

sd = ScoreDict.objects.get(tournament=t)

print ('score dict: ', len(sd.data))
scores = manual_score.Score(sd.data, t).update_scores()
print (scores)
exit()

print (Picks.objects.filter(playerName__tournament=t).values('playerName').distinct().count())

exit()


for g in Group.objects.filter(tournament=t):
    g_min = g.min_score()
    
    print (g, g_min)
    #f = Field.objects.filter(tournament=self, group=group).exclude(withdrawn=True)
    









exit()
        #if group.number == 6:
        #    if field.rank in ["CUT", "WD"]:
        #        print (field.playerName, field.handi, t.saved_cut_num)
        #    else:    
        #        print (field.playerName, field.handi, formatRank(field.rank))

exit()
#m = sorted(sd.values(), key = lambda data: (sum(formatRank(data['rank']), data['handicap'])))

print (m)
exit()


#print (sd.clean_dict()
for k, v in sd.data.items():
    print (k, v)
exit()
for group in Group.objects.filter(tournament=t):
    start = datetime.now()
    group.min_score()
    print (datetime.now() - start)
    #print (t, group, group.min_score())

exit()

data = serializers.serialize('json', Group.objects.filter(tournament=t))
print (data)
print ('ccccccccc')
groups = json.loads(data)
for g in groups:
    if g.get('pk') == 1183:
        print (g['fields']['number'])
exit()
#web = scrape_masters.ScrapeScores(t).scrape()

g5 = Field.objects.filter(tournament=t, group__number=6).exclude(withdrawn=True)
print (int(round(len(g5)/2, 0)))

for i, g in enumerate(g5):
    if i == int(round(len(g5)/2, 0)):
        print (g)




exit()
t= Tournament.objects.get(pga_tournament_num='014', season__season='2019')

web = scrape_scores_picks.ScrapeScores(t, "https://www.pgatour.com/competition/2019/masters-tournament/leaderboard.html", None).scrape()
#print (web)

#sd = ScoreDict()

#sd.tournament = t
#sd.data = web
#sd.save()


exit()

owgr = populateField.get_worldrank()

f = open("owgr.txt", "w")
for k,v in owgr.items():
    try:
        line = k + ' ' + str(v)
        f.write(line)
        f.write('/n')
    except Exception as e:
        continue
f.close()

for name in Field.objects.filter(tournament__current=True):
    populateField.fix_name(name.playerName, owgr)

exit()

t= Tournament.objects.get(current=True)
#t= Tournament.objects.get(pga_tournament_num='047', season__current=True)
print (t)

web = scrape_scores_picks.ScrapeScores(t).scrape()

c_score =  (int(t.cut_score.split(' ')[len(t.cut_score.split(' '))-1]))


print (len([x for x in web.values() if int(x['total_score']) <= c_score and x['rank'] != 'WD']))
#print (ScoreDetails.objects.filter(pick__playerName__tournament=t).order_by('user').count())

exit()

print (ScoreDetails.objects.filter().count())

users = Season.objects.get(current=True).get_users()
print (users)
for u in users:
    user = User.objects.get(pk=u.get('user'))
    for p in Picks.objects.filter(playerName__tournament=t, user=user):
        sd, created = ScoreDetails.objects.get_or_create(pick=p, user=user)

print (ScoreDetails.objects.filter(pick__playerName__tournament=t).order_by('user').count())
print (ScoreDetails.objects.filter().count())
exit()

web = scrape_scores_picks.ScrapeScores(t).scrape()
scores = manual_score.Score(web, t).update_scores()
print (scores)

print (datetime.now() - start)

exit()

for p in Picks.objects.filter(playerName__tournament=t).values('playerName').distinct():

    pick = Picks.objects.filter(playerName__pk=p.get('playerName')).first()
    pick_loop_start = datetime.now()
    #print ('1 -', pick.playerName.playerName)

    data = score_dict.get(unidecode(pick.playerName.playerName))
    if data == None:
        print ('*********', 'player name issue', pick.playerName.playerName, '*************')
        for k, v in score_dict.items():
            if v.get('pga_num') == pick.playerName.playerID:
                data = v
                print ('pick data from pga_num', pick)
            elif pick.playerName.playerName.replace('Jr.', '').replace('Jr','').rstrip(' ') == k:
                print ('strip JR: ', k)
                data = v
            else:
                continue


    if data.get('rank') == "CUT":
        pick.score = cut_num
    elif data.get('rank') == "WD":
        pick.score = self.get_wd_score(pick) 
    else:
        if int(utils.formatRank(data.get('rank'))) > cut_num:
                pick.score=cut_num 
        else:
            pick.score = utils.formatRank(data.get('rank')) 

    #pick.save()  commented as part of batch attempt
    Picks.objects.filter(playerName__tournament=t, playerName=pick.playerName).update(score=pick.score)

    #sd, sd_created = ScoreDetails.objects.get_or_create(user=pick.user, pick=pick)
    sd = ScoreDetails.objects.get(user=pick.user, pick=pick)
    sd.score=pick.score - pick.playerName.handicap()
    sd.gross_score = pick.score
    if data.get('rank') == "CUT" or \
        data.get('rank') == "WD" and round < 3:
        sd.today_score  = "CUT"
        sd.thru  = "CUT"
    elif data.get('rank') == "WD":
        sd.today_score = "WD"
        sd.thru = "WD"
    else:
        sd.today_score = data.get('round_score')
        sd.thru  = data.get('thru')
    sd.toPar = data.get('total_score')
    sd.sod_position = data.get('change')
    #sd.save()  commented as part of batch attempt
    ScoreDetails.objects.filter(pick__playerName__tournament=t, pick__playerName=pick.playerName).update(
        today_score=sd.today_score,
        thru=sd.thru,
        toPar=sd.toPar,
        sod_position='test'
    )

print ('finish time', datetime.now() - start)

exit()

#score_dict = sd.sorted_dict()



#if not t.has_cut:
#     print ('no cut: ', len([x for x in score_dict.values() if x['rank'] not in ['WD', 'DQ']]) + 1)

# if t.get_round() < 3:
#     print ('round less than 3', '66')
# elif len([x for x in score_dict.values() if x['rank'] in t.not_playing_list()]) > 10:
#     print ('in elif: ',  len([x for x in score_dict.values() if x['rank'] not in t.not_playing_list()]))

# print ('dur: ', datetime.now() - start)
# exit()

# wd = len([x for x in score_dict.values() if x['rank'] == 'WD' and x['r'+str(round+1)] != '--']) 

# for v in score_dict.values():
#     if v['rank'] in self.not_playing_list():
#         return len([x for x in score_dict.values() if x['rank'] not in self.not_playing_list()]) + wd + 1
# if self.get_round() != 4 and len(score_dict.values()) >65:
#     return 66
# else:
#     return len([x for x in score_dict.values() if x['rank'] not in self.not_playing_list()]) + wd + 1

cut_num = t.cut_num()
for g in Group.objects.filter(tournament=t):
    start = datetime.now()

    score_dict = ScoreDict.objects.get(tournament=t)
    clean_dict = score_dict.clean_dict()
    #print ('clean dict', datetime.now() - start)
    #cut_num = t.cut_num()
    #cut_num = 75
    #print ('cut_num', datetime.now() - start)
    not_playing_list = t.not_playing_list()
    min_score = 999  
    print ('prep', datetime.now() - start)
    min_handi = Field.objects.filter(group=g).order_by('currentWGR').first()
    print (min_handi.playerName, min_handi.currentWGR)
    max_handi = Field.objects.filter(group=g).order_by('currentWGR').last()
    print (max_handi.playerName, max_handi.currentWGR)
    for score in Field.objects.filter(group=g).order_by('-currentWGR'):
        
        try:
            #if score_dict.data.get(score.playerName).get('rank') in self.tournament.not_playing_list():
            if clean_dict.get(score.playerName).get('rank') in not_playing_list:
                if cut_num - score.handicap() < min_score:
                    min_score = cut_num - score.handicap()
            #elif utils.formatRank(score_dict.data.get(score.playerName).get('rank')) - score.handicap() < min_score:
            elif utils.formatRank(clean_dict.get(score.playerName).get('rank')) - score.handicap() < min_score:
                min_score = utils.formatRank(clean_dict.get(score.playerName).get('rank')) - score.handicap()
            #else:
            #    print ('not min', score.playerName, score_dict.data.get(score.playerName).get('rank'), utils.formatRank(score_dict.data.get(score.playerName).get('rank')))
        except Exception as e:
            print (score.playerName, e, 'exclded from min score')
            #print (self, score.rank_as_int(), score.handicap())
        #print ('end min score ', datetime.now() - start, self)
    print (score.group, min_score, datetime.now() - start)
exit()









print (t.optimal_picks())
exit()

s = datetime.now()
#t = Tournament.objects.get(current=True)
t = Tournament.objects.get(pga_tournament_num='464', season__current=True)
sd = ScoreDict.objects.get(tournament=t)


score_dict = sd.sorted_dict()
scores = manual_score.Score(score_dict, t, 'json')
ts = scores.total_scores()
d = scores.get_picks_by_user() 
        
optimal = t.optimal_picks()
scores_json = json.dumps(score_dict)
totals = Season.objects.get(season=t.season).get_total_points()
leaders = scores.get_leader()

display_dict = {}
display_dict['display_data'] = {'picks': d,
                    'totals': ts,
                    'leaders': leaders,
                    'cut_line': t.cut_score,
                    'optimal': optimal,
                    'scores': json.dumps(score_dict),
                    'season_totals': totals,}

sd.pick_data = json.dumps(display_dict)
sd.save()


exit()



for g in Field.objects.filter(tournament=t):
    print (g, g.currentWGR, g.handi)



exit()
for g in Group.objects.filter(tournament=t).order_by('number'):
    start = datetime.now()
    print (g, g.min_score(), datetime.now()-start)

print ('current process: ', datetime.now() - s)








exit()


for f in Field.objects.filter(tournament=t).order_by('number'):
    if f.playerName not in web.keys():
        for k,v in web.items():
            if unidecode(k) == unidecode(f.playerName):
                break
        if unidecode(k) == unidecode(f.playerName):
            continue
        else:
            field_name_len = len(f.playerName.split(' '))
            cbs_name_len = len(k.split(' '))
            print (f.playerName, 'field_len', field_name_len, 'cbs len:', cbs_name_len)
            if unidecode(k.split(' ')[cbs_name_len-1]) == unidecode(f.playerName.split(' ')[field_name_len-1]) and \
               unidecode(k.split[0][1]) == unidecode(f.playerName.split[0][1]):
               print ('found match', f.playerName )


            
            #print ('not in cbd', f.playerName)

exit()

print ('============================================')

for f in Field.objects.filter(tournament=t):
    if f.playerName not in pga.keys():
        for k, v in pga.items():
            if k.replace('(a)', '').strip() == f.playerName:
                break
        if k.replace('(a)', '').strip() == f.playerName:
            continue
        else:
            print ('not in pga', f)

    


#print (web)

exit()


#for t in Tournament.objects.filter(season__current=True):
#    print (t, t.pk)

t = Tournament.objects.get(pk=126)
user = User.objects.get(username='j_beningufirudo')
print (t)

Picks.objects.filter(user=user).delete()
ScoreDetails.objects.filter(user=user).delete()


for pick in ScoreDetails.objects.filter(pick__playerName__tournament=t, user__username='jcarl62'):

    jb_pick = Picks()
    jb_pick.user = user
    jb_pick.playerName = pick.pick.playerName
    jb_pick.score = pick.pick.score
    jb_pick.save()

    bonus, c = BonusDetails.objects.get_or_create(user=user, tournament=t, winner_bonus=0, cut_bonus=0, major_bonus=0, best_in_group_bonus=0, playoff_bonus=0)
    #bonus.save()

    PickMethod.objects.get_or_create(method=3, tournament=t, user=user)

    sd = ScoreDetails()
    sd.user = user
    sd.pick = pick.pick
    sd.score = pick.score
    sd.toPar = pick.toPar
    sd.today_score = pick.today_score
    sd.thru = pick.thru
    sd.sod_position = pick.sod_position
    sd.gross_score = pick.gross_score
    sd.save()

TotalScore.objects.get_or_create(user=user, tournament=t, score=573)








exit()
for golfer in Field.objects.filter(tournament=t):
    golfer.withdrawn = False
    golfer.save()

print (len(Field.objects.filter(tournament=t, withdrawn=True)))


exit()

urls:  ['https://www.pgatour.com/competition/2020/the-cj-cup-at-nine-bridges/leaderboard.html',
         'https://www.pgatour.com/competition/2020/the-zozo-championship/leaderboard.html',
         'https://www.pgatour.com/competition/2020/wgc-hsbc-champions/leaderboard.html',
         'https://www.pgatour.com/competition/2020/at-t-pebble-beach-pro-am/leaderboard.html',
         'https://www.pgatour.com/competition/2020/genesis-invitational/leaderboard.html',
         #'https://www.pgatour.com/competition/2020/wgc-mexico-championship/leaderboard.html',   can't find?
         'https://www.pgatour.com/competition/2020/wgc-fedex-st-jude-invitational/leaderboard.html'
         


]




season = Season.objects.get(season='2019')
g6_total = 0
g6_hc = 0
last_total = 0
last_hc = 0
t_count = 0
for t in Tournament.objects.filter(season=season):
    if  Group.objects.filter(tournament=t, number=7).exists():
        group = Group.objects.get(tournament=t, number=7)
        if group.playerCnt > 6:
            try:
                print (t)
                sd = ScoreDict.objects.get(tournament=t)
                
                group_6 = Field.objects.filter(tournament=t, group__number=6).order_by('currentWGR')
                group_6_score = 0
                handi = 0
                for golfer in group_6[:5]: 
                    #print (golfer)
                    if sd.data[golfer.playerName]['rank'] not in t.not_playing_list():
                        group_6_score = group_6_score + utils.formatRank(sd.data[golfer.playerName]['rank']) - golfer.handicap()
                        handi = handi + golfer.handicap()
                    else:
                        group_6_score = group_6_score + (int(t.cut_num()) - golfer.handicap())
                        handi = handi + golfer.handicap()
                    
                last_group = Field.objects.filter(tournament=t).order_by('-currentWGR')
                last_score = 0
                last_handi = 0
                for golfer in last_group[:5]: 
                    #print (golfer)
                    if sd.data[golfer.playerName]['rank'] not in t.not_playing_list():
                        last_score = last_score + utils.formatRank(sd.data[golfer.playerName]['rank']) - golfer.handicap()
                        last_handi = last_handi + golfer.handicap()
                    else:
                        last_score = last_score + (int(t.cut_num()) - golfer.handicap())
                        last_handi = last_handi + golfer.handicap()

                print ('G6 score: ', group_6_score)
                print ('G6 handi: ', handi)
                print ('last score: ', last_score)
                print ('last handi: ', last_handi)
                g6_total = g6_total + group_6_score
                g6_hc = g6_hc + handi
                last_total = last_total + last_score
                last_hc = last_hc + last_handi
                t_count += 1

            


            except Exception as e:
                print ('issue: ', t, e)
        else:
            print ("T group size too small", t)
    else:
        print ("T too small", t)

print  ('group 6 total: ', g6_total)
print  ('group 6 h/c: ', g6_hc)
print  ('last group total: ', last_total)
print  ('last group hc: ', last_hc)
print  ('total tournaments: ', t_count)

        
exit()



t = Tournament.objects.get(current=True)

#start = datetime.now()
#web1 = scrape_scores_picks.ScrapeScores(t).scrape()
#scrape_finish = datetime.now()

#print ('scrape time: ', scrape_finish - start)

## attempt to speed up best in group function

start_cut = datetime.now()

score_dict = ScoreDict.objects.get(tournament=t)
cut_num = t.cut_num()
min_score = 999  
print (type(score_dict))

for score in Field.objects.filter(group__number=6, tournament=t):
    #print ('min score calc: ', datetime.now())
    try:
        if score_dict.data.get(score.playerName).get('rank') in ['CUT', 'WD']:
            if cut_num - score.handicap() < min_score:
                min_score = cut_num - score.handicap()
        elif utils.formatRank(score_dict.data.get(score.playerName).get('rank')) - score.handicap() < min_score:
            min_score = utils.formatRank(score_dict.data.get(score.playerName).get('rank')) - score.handicap()
        #else:
        #    print ('not min', score.playerName, score_dict.data.get(score.playerName).get('rank'), utils.formatRank(score_dict.data.get(score.playerName).get('rank')))
    
    except Exception as e:
        continue
        #print (score.playerName, e, 'exclded from min score')
print ('min 1: ', min_score)

print ('cut round 1: ', datetime.now() - start_cut )



start_cut = datetime.now()

score_dict = ScoreDict.objects.get(tournament=t)
cut_num = t.cut_num()
min_score = 999  

for k, v in score_dict.data.items():
    try:
        if Field.objects.filter(playerName=k, group__number=6, tournament=t).exists():
            field = Field.objects.get(playerName=k, group__number=6, tournament=t)
            #print (cut_num, field.handicap())
            if v.get('rank') in ['CUT', 'WD']:
                if cut_num - field.handicap() < min_score:
                    #print ('cut is best')
                    min_score = cut_num - field.handicap()
            elif utils.formatRank(v.get('rank')) - field.handicap() < min_score:
                #print ('no cut best')
                min_score = utils.formatRank(v.get('rank')) - field.handicap()
        
    except Exception as e:
        print (e)
        #continue
        #print (score.playerName, e, 'exclded from min score')
    #print (min_score)
print ('min 2: ', min_score)



print ('cut round 2: ', datetime.now() - start_cut )

exit()

#### end of best pick perf seciton


for golfer in Field.objects.filter(tournament=t, group__number=6):
    try:
        if sd.data.get(golfer.playerName).get('rank') not in t.not_playing_list():
            d[golfer.playerName]=golfer.currentWGR, utils.formatRank(sd.data.get(golfer.playerName).get('rank')), golfer.handicap(), utils.formatRank(sd.data.get(golfer.playerName).get('rank')) - golfer.handicap()
        else:
            d[golfer.playerName]=golfer.currentWGR, cut_num, golfer.handicap(), cut_num - golfer.handicap()
    except Exception as e:
        print ('f potter', golfer.playerName, e)
    #print (group, group.min_score())
sorted_d = ({k:v for k, v in sorted(d.items(), key=lambda item: item[1][0])})
for k, v in sorted_d.items():
    print (k, v)
 
exit()
start = datetime.now()
print (t.optimal_picks())
exit()
old_start = datetime.now()
web1 = scrape_scores_picks.ScrapeScores(t).scrape()
old_finish = datetime.now()

print (old_finish - old_start)
#print (web1)
exit()

#score_dict = ScoreDict.objects.get(tournament=t)
#print ('after sd: ', datetime.now() - start)

score_start = datetime.now()
scores = manual_score.Score(score_dict, t, 'json')
ts = scores.total_scores()
print ('total_score: ', datetime.now() - score_start)
d = scores.get_picks_by_user() 

optimal_start = datetime.now()
optimal = t.optimal_picks()
print ('optimal: ', datetime.now() - optimal_start)

#scores_json = json.dumps(score_dict)
season_start = datetime.now()
totals = Season.objects.get(season=t.season).get_total_points()
print ('season: ', datetime.now() - season_start)
leaders = scores.get_leader()

print ('verall: ', datetime.now() - start)


#web = scrape_scores_by_id.ScrapeScores(t).scrape()
#new_finish = datetime.now() 
#print ('new: ', new_finish - new_start)

print ('old: ', old_finish - old_start)
#print ('new: ', new_finish - new_start)

exit()

scores = manual_score.Score(sd.data, t)
scores.update_scores()

for bd in BonusDetails.objects.filter(tournament=t):
    print (bd.user, bd.best_in_group_bonus)

print (scores.total_scores())


exit()


start = (datetime.now())
optimal_picks  = json.loads(t.optimal_picks())
print (type(optimal_picks), optimal_picks)
for pick in Picks.objects.filter(playerName__tournament=t):
    if pick.playerName.playerName in optimal_picks.get(str(pick.playerName.group.number)).get('golfer'):
        print (pick, ' in')
    #print (pick.playerName, ': ', optimal_picks.get(str(pick.playerName.group.number)).get('golfer'))
print (start - datetime.now()) 

for t in Tournament.objects.filter(season__current=True, pga_tournament_num='013'):

    for g in Group.objects.filter(tournament=t):
        print (g)
        print (g.min_score(), g.best_picks())

exit()
#print (season.get_total_points())

#sorted(ts_dict.items(), key=lambda v: v[1].get('total_score'))

#fields = BonusDetails._meta.get_fields()
#print (type(fields), len(fields))
#for f in fields:
#    print (f)
#exit()

for t in Tournament.objects.filter(season=season):
    field_list = []
    field = Field.objects.filter(tournament=t).order_by('currentWGR')
    for f in field:
        field_list.append(f.handicap())
    print (t, ' field size: ', len(field))
    populateField.configure_groups(field)
    try:
        print ('group 6 h/c: ', field_list[50], ' - ', field_list[-1])
    except Exception as e:
        print ('entire field h/c: ', field_list[0], ' - ', field_list[-1])
    print (' ')

exit()

first_picks = {'Sam36': ['Sungjae Im', 'Tom Lewis', 'Charles Howell III', 'Dylan Frittelli', 'Harold Varner III', 'Mark Hubbard', 'Ryan Armour', 'Sam Ryder', 'Bronson Burgoon',
 'Peter Uihlein', 'Nelson Ledesma', 'John Senden'],
  'JoeLong': ['Shane Lowry', 'Sung Kang', 'J.T. Poston', 'Dylan Frittelli', 'Andrew Landry', 'Brian Stuard', 'Charl Schwartzel',
 'Kyoung-Hoon Lee', 
'Hank Lebioda',
'Kramer Hickok',
'Michael Gligic',
'Michael Kim'], 
'BigDipper': ['Webb Simpson',
'Tom Lewis',
'Jason Kokrak',
'Matt Jones',
'Ryan Moore',
'Tom Hoge',
'Russell Knox',
'Cameron Davis',
'Jason Dufner',
'Sebastian Cappelen',
'Rob Oppenheim',
'Arjun Atwal',],
'JL Choice':
['Paul Casey',
'Brendon Todd',
'Matthias Schwab',
'Dylan Frittelli',
'Si woo Kim',
'Sepp Straka', 
'Russell Henley', 
'Will Gordon', 
'Bronson Burgoon', 
'Matt Every', 
'Luke Donald',
'Ben Taylor']
}


t = Tournament.objects.get(current=True)

for k,v in first_picks.items():
    score = 0
    cuts = 0
    #print (k)
    for p in v:
    #    print (p)
        f = Field.objects.get(playerName=p, tournament=t)
        if f.rank_as_int() > 64:
            score += 78
            cuts += 1
        else:
            score += f.rank_as_int()
        #print(p, f.rank_as_int(), score)
    print ('orig picks: ', k, score, cuts)
    try:
        ts = TotalScore.objects.get(tournament=t, user__username=k)
        print ('game score: ', ts.user, ts.score, ts.cut_count)

    except Exception as e:
        continue



 



#season = Season.objects.get(current=True)
#users = season.get_users()
#print (users)

#pk_list = []
#for t in Tournament.objects.filter(season__current=True):
#    pk_list.append(t.pk)


#f = open('handicap.txt', 'wb')

#t = Tournament.objects.get(current=True)
#try:
#    scrape_scores_by_id.ScrapeScores(t).scrape()
#except Exception as e:
#    print ('Fail: ', t, e)

#from django.contrib.admin.models import LogEntry

#logs = LogEntry.objects.all() #or you can filter, etc.
#for l in logs:
#    print (l.action_time)
#    print (l.get_edited_object())






# score_dict = ScoreDict.objects.get(tournament=t)
# print (score_dict)
# score = manual_score.Score(score_dict.data, t)
# print (score.optimal_picks())

# exit()

# for key in pk_list:#pk_list[-15:]:
#     t = Tournament.objects.get(pk=key)
#     print (t)
#     min_list = []
#     max_list = []
#     for f6 in Field.objects.filter(tournament=t, group__number__gte=6):
#         min_list.append(f6.handicap())


#     f.write('handicap range in group 6: ', min(min_list), max(min_list))
#     handicap = 0

    


#     h_dict = {}
#     for u in users:
#         user_o = User.objects.get(pk=u.get('user'))
#         handicap = 0
#         for sd in ScoreDetails.objects.filter(pick__playerName__tournament=t, user=user_o):
#                 handicap = handicap + sd.pick.playerName.handicap()
#         score = TotalScore.objects.get(tournament=t, user=sd.user)
#         #print (score)
#         h_dict[user_o.username] = handicap, score.score, score.score - handicap


#     sorted_h = sorted(h_dict.items(), key=lambda x: x[1][2])

#     for k in sorted_h:
#         f.write(k)
#         print (str(k))

# f.close()



#for golfer in Field.objects.filter(tournament=t):
#    print (golfer, 'owgr: ', golfer.currentWGR, ',  ', golfer.handicap())