import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
#from golf_app.models import Tournament, TotalScore, ScoreDetails, Field, Picks, PickMethod
from fb_app.models import Season, Week, Games, Teams, Picks, League, Player, calc_scores, MikeScore, WeekScore
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import sqlite3
from django.db.models import Min, Q, Count, Sum, Max
from django.db.models.functions import ExtractWeek, ExtractYear
import time
from golf_app import populateField
import urllib
from urllib import request
import json
from fb_app.scores import Scores
#from requests import get
#from random import randint
import sys
# pip install PyQt5 and PyQtWebEngine
#from PyQt5.QtWidgets import QApplication, QWidget
#from PyQt5.QtCore import QUrl
#from PyQt5.QtWebEngineWidgets import QWebPage
#from PyQt5.QtWebEngine import QtWebEngine as QWebPage

#from PyQt5.QtWebEngineWidgets import QWebEngineView
#from bs4 import BeautifulSoup
#from urllib.request import Request, urlopen
#from selenium import webdriver
#

#

def check():
    p = Player.objects.get(name=User.objects.get(username='milt'))
    for s in MikeScore.objects.filter(week__season_model__current=True, player=p):
        print (s)
    
def picks():
    week = Week.objects.get(current=True)
    player = Player.objects.get(name=User.objects.get(username="JoeLong"))

    print(week, player)
    Picks.objects.filter(week=week, player=player).delete()
    print(Picks.objects.filter(week=week, player=player))

    pick_num = 16
    pick_list = ['LAC', 'LA', 'BAL', 'NE', 'IND', 'KC', 'SEA', 'GB', 'ATL', 'HOU', 'PIT', 'DAL', 'MIN', 'JAC', 'WAS']

    for p in pick_list:
        pick = Picks()
        pick.week = week
        pick.player = player
        pick.pick_num = pick_num
        pick.team = Teams.objects.get(nfl_abbr = p)
        pick.save()
        pick_num -= 1

    print (Picks.objects.filter(week=week, player=player))

    
   
def weeks():
    for week in Week.objects.all():
        print (week.season, week, week.pk)

def count():
    curr_week = Week.objects.get(current=True)
    print (Games.objects.filter(week__season_model__current=True, week__week__gt=curr_week.week).values('week__week').annotate(Count('week')))

def recalc(league):
    '''compares my scores to mike's scores'''
    l = League.objects.get(league=league)
    season = Season.objects.get(current=True)
    c_week = Week.objects.get(current=True)
    good_list = []
    bad_list = []
    
    for player in Player.objects.filter(league=l, active=True):
        print (player)
        user=User.objects.get(username=player.name)
        l_week = Week.objects.get(week=c_week.week-1, season_model__current=True)
        ms = MikeScore.objects.get(player__name=user, week=l_week)
        js = WeekScore.objects.filter(Q(player=player) & (Q(week__season_model__current=True) & Q(week__current=False))).aggregate(Sum('score'))
        #print (player, ms.total, js.get('score__sum'))
        if ms.total == js.get('score__sum'):
            good_list.append(player)
        else:
            w = Week.objects.get(season_model__current=True, week=1)
            while w.week < c_week.week:
                print (w, player)
                m_score = MikeScore.objects.get(week=w, player=player)
                #j_score = WeekScore.objects.get(week=w, player=player)
                j_score = WeekScore.objects.filter(Q(player=player) & (Q(week__season_model__current=True) & Q(week__week__lte=w.week))).aggregate(Sum('score'))
                if m_score.total != j_score.get('score__sum'):
                    print (player, w, 'mike', m_score.total, 'john', j_score.get('score__sum'))
                w = Week.objects.get(season_model__current=True, week=w.week+1)

    print (len(good_list))
    print (bad_list)
    


#check()
#picks()
#weeks()
#count()

# for week in Week.objects.filter(season_model__current=True):
#     mscore = MikeScore.objects.filter(week=week).values('player').order_by('player').annotate(count=Count('player'))
#     for item in mscore:
#         if item.get('count') > 1:
#             for dup in MikeScore.objects.filter(player__id=item.get('player'), week=week):
#                 i = 1
#                 print ('1', dup, item)
#                 while i < item.get('count'):
#                   print ('2', dup)
#                   dup.delete()
#                   i += 1

#recalc('Football Fools')
#week = Tournament.objects.get(current=True)
#print ('week', week, week.started())
#from golf_app import pga_score
#print ('==  no cut ==')
#t = pga_score.PGAScore('489')
#print ('hc', t.has_cut())
#print ('pmc', t.players_making_cut())
#print ('cs',t.cut_status())
#print ('cc', t.cut_count())
#print ('round', t.round(), type(t.round()))
#print ('player', t.get_golfer_by_id('26329'))
#print (t.get_golfer_dict())
#w = Week.objects.get(week=13, season_model__current=True)
#for game in Games.objects.filter(week=w):
#    game.spread = None
#    game.save()

# json_url = 'http://www.nfl.com/liveupdate/scores/scores.json'

# with urllib.request.urlopen(json_url) as field_json_url:
#      data = json.loads(field_json_url.read().decode())

# print (data['2019121200']["clock"])

import scipy.stats as ss
season = Season.objects.filter(current=True)
league = League.objects.get(league="Football Fools")

# for week in Week.objects.filter(season_model__current=True):
#     s=Scores(week, league, False)
#     norm_rank = s.get_week_rank().get('TLUKE')
#     count = sum(value == norm_rank for value in s.get_week_rank().values())
#     print('week ' + str(week.week) + ': ' + str(s.get_week_rank().get('TLUKE')), + count)

d={}
total_picks = 0

for player in Player.objects.filter(league__league="golfers"):
    print (player)        

    for team in Teams.objects.all():
        d[team] = {}
        d[team].update({'picks': 0, 
                    'wins': 0,
                    'loss': 0,
                    'miss': 0,
                    'points': 0})

    for team in Teams.objects.all():
        picks = 0
        loss = 0
        win = 0
        wrong = 0
        game_cnt = 0
        #week = Week.objects.get(season_model__current=True, week=17)
        for pick in Picks.objects.filter(player=player, week__season_model__current=True, team=team):
            total_picks +=1 
            d[pick.team]['picks'] = d[pick.team]['picks'] + 1
            if pick.is_loser():
                d[pick.team]['loss'] = d[pick.team]['loss'] + 1
                d[pick.team]['points'] = d[pick.team]['points'] + pick.pick_num

            else:
                d[pick.team]['wins'] = d[pick.team]['wins'] + 1
            game = Games.objects.get((Q(home=pick.team) | Q(away=pick.team)), week=pick.week) #week__season_model__current=True):
            game_cnt += 1
            if not game.tie and pick.team != game.winner:
                
                d[game.winner]['miss'] = d[game.winner]['miss']+1
                
        
    #print ({k: v for k, v in sorted(d.items(), key=lambda item:item['loss'])})
    print (d)
    print (total_picks)
    print (game_cnt)