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
from golf_app import views, manual_score, populateField, withdraw, scrape_scores_picks, utils, scrape_cbs_golf, scrape_masters, scrape_espn
from unidecode import unidecode
from django.core import serializers
from golf_app.utils import formatRank, format_name, fix_name

start = datetime.now()
for sd in ScoreDetails.objects.filter(Q(pick__playerName__tournament__season__current=True) & (Q(thru="WD") | Q(toPar="WD"))):
    print (sd.pick.playerName.tournament, sd.pick.playerName.tournament.saved_cut_num, sd, sd.pick.playerName.handicap())
exit()



#s = Season.objects.get(current=True)
t = Tournament.objects.get(current=True)
#print (Field.objects.filter(tournament=t, golfer__espn_number__isnull=True))
g = scrape_espn.ScrapeESPN().get_data()
#print (g)
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