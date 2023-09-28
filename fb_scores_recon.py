import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()

from fb_app.models import Season, Week, Games, Teams, Picks, League, Player, calc_scores, MikeScore, WeekScore
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.db.models import Min, Q, Count, Sum, Max
import sys
from django.core.exceptions import ObjectDoesNotExist


def recalc(league):
    '''compares my scores to mike's scores'''
    l = League.objects.get(league=league)
    season = Season.objects.get(current=True)
    c_week = Week.objects.get(current=True)
    good_list = []
    bad_list = []
    print (c_week)
    
    for player in Player.objects.filter(league=l, active=True):
        print (player)
        user=User.objects.get(username=player.name)
        l_week = Week.objects.get(week=c_week.week-1, season_model__current=True)
        print (l_week)
        ms = MikeScore.objects.get(player__name=user, week=l_week)
        js = WeekScore.objects.filter(Q(player=player) & (Q(week__season_model__current=True) & Q(week__current=False))).aggregate(Sum('score'))
        #print (player, ms.total, js.get('score__sum'))
        if ms.total == js.get('score__sum'):
            good_list.append(player)
        else:
            w = Week.objects.get(season_model__current=True, week=1)
            while w.week < c_week.week:
                print (w, player)
                try:
                    m_score = MikeScore.objects.get(week=w, player=player)
                    j_score = WeekScore.objects.filter(Q(player=player) & (Q(week__season_model__current=True) & Q(week__week__lte=w.week))).aggregate(Sum('score'))
                    if m_score.total != j_score.get('score__sum'):
                        d = (player, w, 'mike', m_score.total, 'john', j_score.get('score__sum'))
                        bad_list.append(d)
                        print (player, w, 'mike', m_score.total, 'john', j_score.get('score__sum'))
                    w = Week.objects.get(season_model__current=True, week=w.week+1)

                except Exception:
                    w = Week.objects.get(season_model__current=True, week=w.week+1)
  
                #j_score = WeekScore.objects.get(week=w, player=player)

    print (len(good_list))
    print (bad_list)
    

def clean_up_dup_weeks():
    for week in Week.objects.filter(season_model__current=True):
        mscore = MikeScore.objects.filter(week=week).values('player').order_by('player').annotate(count=Count('player'))
        for item in mscore:
            if item.get('count') > 1:
                print ('duplicate', week, item)
                for dup in MikeScore.objects.filter(player__id=item.get('player'), week=week):
                    i = 1
                    print ('1', dup, item)
                    while i < item.get('count'):
                        print ('2', dup)
                        dup.delete()
                        i += 1

week = Week.objects.get(season_model__current=True, week=2)
week.save()
recalc('Football Fools')
#clean_up_dup_weeks()
