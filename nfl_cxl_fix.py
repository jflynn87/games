import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from fb_app.models import Season, Week, Games, Teams, Picks, League, Player, MikeScore, WeekScore#, get_data
from django.contrib.auth.models import User
from datetime import datetime, timedelta, timezone
from django.db.models import Min, Q, Count, Sum, Max
#from django.db.models.functions import ExtractWeek, ExtractYear
#import time
#import urllib
#from urllib import request
#import json
#from fb_app.scores import Scores
#from urllib.request import Request, urlopen

team_list = []
h = Teams.objects.get(nfl_abbr="NE")
team_list.append(h)
a = Teams.objects.get(nfl_abbr="DEN")
team_list.append(a)
game = Games.objects.get(eid="20205NEDEN")
week = Week.objects.get(current=True)
l = League.objects.get(league="Golfers")

week.game_cnt = week.game_cnt -1
week.save()

game.delete()

print ('****** pick summary before update ******')
#for p in Picks.objects.filter(week=week, player__league=l).values('player__name__username').annotate(Count('player')):
for p in Picks.objects.filter(week=week).values('player__name__username').annotate(Count('player')):
    print (p.get('player__name__username'), ' : ', p.get('player__count'))

f = open("picksweek"+ str(week.week) + "pre-fix.txt", "w")
#for pick in Picks.objects.filter(week=week, player__league=l):
for pick in Picks.objects.filter(week=week):
    f.write(pick.player.name.username + ',' + str(pick.pick_num) + ',' + str(pick.team.nfl_abbr) + '\n')
    #f.write('\n')
f.close()

for pick in Picks.objects.filter(team__in=team_list, week=week):
    pick.delete()

# find missing pics

fix_list = []
#for player in Player.objects.filter(league=l).order_by('name'):
for player in Player.objects.filter(active=True).order_by('name'):
    prior_pick = Picks.objects.filter(week=week, player=player).order_by('-pick_num')[0]
    for p in Picks.objects.filter(week=week, player=player).order_by('-pick_num').exclude(pick_num = prior_pick.pick_num):
        if p.pick_num + 1 == prior_pick.pick_num:
            prior_pick = p
        #print ('good', p)
        else:
            fix_list.append((player.name, p.pick_num +1))
            print ('fixing picks: ', player.name, p.pick_num, p.team, prior_pick.pick_num, prior_pick.team)    
            prior_pick = p
print ('picks to fix: ', fix_list)

#fix missing picks
for u in fix_list:
    for p in Picks.objects.filter(week=week, player__name=u[0], pick_num__lte=u[1]):
        p.pick_num = p.pick_num +1
        p.save()

print ("###### updated players")
#print (Picks.objects.filter(week=week, player__league=l))
print (Picks.objects.filter(week=week))


print ('****** pick summary after update ******')

#for p in Picks.objects.filter(week=week, player__league=l).values('player__name__username').annotate(Count('player')):
for p in Picks.objects.filter(week=week).values('player__name__username').annotate(Count('player')):
    print (p.get('player__name__username'), ' : ', p.get('player__count'))



