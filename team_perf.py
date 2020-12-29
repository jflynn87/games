import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
#from golf_app.models import Tournament, TotalScore, ScoreDetails, Field, Picks, PickMethod
from fb_app.models import Season, Week, Games, Teams, Picks, League, Player,  MikeScore, WeekScore
from django.contrib.auth.models import User
from datetime import datetime, timedelta, timezone
from django.db.models import Min, Q, Count, Sum, Max
from django.db.models.functions import ExtractWeek, ExtractYear
import time
import urllib
from urllib import request
import json
#from fb_app.scores import Scores
#from urllib.request import Request, urlopen
from selenium.webdriver import Chrome, ChromeOptions
#

#
import requests
#from linebot import LineBotApi
#from linebot.models import TextSendMessage
#from linebot.exceptions import LineBotApiError
from bs4 import BeautifulSoup
from fb_app import scrape_cbs
import pytz
from django.core import serializers
import docx2txt




def calc_results():
    start = datetime.now()
    #user = User.objects.get(username='john')

    season = Season.objects.get(current=True)
    c_week = Week.objects.get(current=True)
    league = League.objects.get(league='Golfers')
    team_dict = {}
    league_dict = {}
    for p in Player.objects.filter(league=league):
        league_dict[p.name.username] = {}

    total_points = 0
    for week in Week.objects.filter(season_model=season).order_by('week'):
        count = Games.objects.filter(week=week).count()
        min_pick = 16 - count
        c = 16
        points = 0
        while c > min_pick:
            points += c
            c -= 1
        total_points = total_points + points
        #print (week, count, points)
    print ('total: ', total_points)

    lose = 0
    win = 0

    for pick in Picks.objects.filter(player__name__username='john', week__season=season):
        if pick.is_loser():
            lose += pick.pick_num
        else:
            win += pick.pick_num

    print ('win: ', win)
    print ('lose: ', lose)

    #exit()

    for player in Player.objects.filter(league=league):
        for team in Teams.objects.all():
            team_dict[team] = {'picked_and_won': 0,
                            'picked_and_lost': 0,
                            'picked_against_won': 0,
                            'picked_against_lost': 0,
                            'tie': 0,
                            'right': 0,
                            'wrong': 0,
                            'points_lost': 0,
                            'points_won': 0}

        user = player.name
        for week in Week.objects.filter(week__lt=c_week.week, season_model=season):
            for pick in Picks.objects.filter(week=week, player__name=user).order_by('-pick_num'):
                #print ('pick: ', pick)
                game =  Games.objects.get(Q(week=week) & (Q(home=pick.team) | Q(away=pick.team)))
                if game.tie:
                    team_dict[game.home].update({'tie': team_dict[game.home]['tie'] +1})
                    team_dict[game.away].update({'tie': team_dict[game.away]['tie'] +1})
                    if pick.player.league.ties_lose:
                        team_dict[game.home].update({'wrong': team_dict[game.home]['wrong'] +1})
                        team_dict[game.away].update({'wrong': team_dict[game.away]['wrong'] +1})
                        team_dict[game.home].update({'points_lost': team_dict[game.home]['points_lost'] + pick.pick_num})
                        team_dict[game.away].update({'points_lost': team_dict[game.away]['points_lost'] + pick.pick_num})
                    else:
                        team_dict[game.home].update({'right': team_dict[game.home]['right'] +1})
                        team_dict[game.away].update({'right': team_dict[game.away]['right'] +1})
                        team_dict[game.away].update({'points_won': team_dict[game.away]['points_won'] + pick.pick_num})
                else:
                    if pick.team == game.winner:
                        team_dict[pick.team].update({'picked_and_won': team_dict[pick.team]['picked_and_won'] +1})
                        team_dict[pick.team].update({'right': team_dict[pick.team]['right'] +1})
                        team_dict[pick.team].update({'points_won': team_dict[pick.team]['points_won'] + pick.pick_num})

                        team_dict[game.loser].update({'picked_against_lost': team_dict[game.loser]['picked_against_lost'] +1})
                        team_dict[game.loser].update({'right': team_dict[game.loser]['right'] +1})
                        #team_dict[pick.team].update({'points_won': team_dict[pick.team]['points_lost'] + pick.pick_num})
                    elif pick.team == game.loser:
                        team_dict[pick.team].update({'picked_and_lost': team_dict[pick.team]['picked_and_lost'] +1})
                        team_dict[pick.team].update({'wrong': team_dict[pick.team]['wrong'] +1})
                        team_dict[pick.team].update({'points_lost': team_dict[pick.team]['points_lost'] + pick.pick_num})

                        team_dict[game.winner].update({'picked_against_won': team_dict[game.winner]['picked_against_won'] +1})
                        team_dict[game.winner].update({'wrong': team_dict[game.winner]['wrong'] +1})
                        team_dict[game.winner].update({'points_lost': team_dict[game.winner]['points_lost'] + pick.pick_num})
        league_dict[user.username].update(team_dict)

    print (league_dict)
    print (datetime.now() - start)
    
    for player, data in league_dict.items():
        print ('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
        print (player)
        for team, stats in data.items():
            print (team, ': ', stats)    

    print ('duation: ', datetime.now() - start)

calc_results()