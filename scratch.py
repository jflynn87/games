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


data = {}
l = League.objects.get(league="Golfers")
print (l.leading_score())

players = Player.objects.filter(league=l)

for p in players:
    print (p, p.season_points_behind())
exit()

TotalScore.objects.filter(league=player.league)
#for score in TotalScore.objects.filter(league=player.league):



def parse_sheet(sheet, players=None):
    
    if players == None:
        players = 26

    row_len = players + 2
    sheet_dict = {}
    player_list = []
    sheet_list = []
    row = 0

    doc = docx2txt.process(sheet)
    l = doc.split('\n')
    ps = ([x for x in l if x not in ['', '  ']])
    sheet_dict['week'] = ps[0]
    print (ps)
    #build player name keys in dict
    for s in ps[1:players+1]:
        try:
            if s not in  ['', '  ']:
                sheet_dict['picks'].update({fix_name(s): {}})
                sheet_dict['totals'].update({fix_name(s): {}})
                player_list.append(fix_name(s))
        except KeyError:
            sheet_dict['picks'] = {fix_name(s): {}}
            sheet_dict['totals'] = {fix_name(s): {}}
            player_list.append(fix_name(s))
    
    #add picks to dict
    player_i = -1
    for i, pick in enumerate(ps[players+1:]):
        #print ('i: ', i, 'row: ', row, 'pick: ', pick, 'player_i: ', player_i)
        #print (pick, ps[i-1]) 
        if i == len(ps) - ((players*2)+1) or row > 15:  # break after scanning picks, skipping totals in this loop
            print ('break')
            break
        if i == 0:
            player_i = 0
        elif player_i == 26:  #last col in row, setting for next row
            row +=1
            player_i = 27
        elif player_i == 27:  #first col in new row, skipping pick number
            player_i = 0
        else:
            if pick == ps[(players+1 +i)-1]:
                print ('A', pick, ps[(players+1 +i)-1])
                try: #detecting no pick rows on bye weeks
                  int(pick)
                  int(ps[(players+1 +i)-1])
                  print ('break 1')
                  continue
                except Exception as e:
                  print ('passing', e)
            sheet_dict['picks'][player_list[player_i]].update({16-(row): pick})
            player_i = (i - (row*row_len)) 
                
    #add season totals to dict
    for i, total in enumerate(ps[-players:]):
        sheet_dict['totals'][player_list[i]]=total
            
    
    print (sheet_dict)
    
        
    
    
    


def fix_name(name):
    fix_name = ''
    for i, c in enumerate(name):
        if c != ' ':
            fix_name += c
        elif name[i-1] != ' ':
            fix_name += c

    return fix_name.rstrip()



# #parse_sheet('20-21 FOOTBALL FOOLS-week14.docx')
# print ('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
# parse_sheet('THANKSGIVING.docx')
# print ('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
# parse_sheet('week14-sheet.docx')
# print ('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
# parse_sheet('20-21 FOOTBALL FOOLS-wek13.docx')
# print ('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')