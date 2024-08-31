#import os
#os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

#import django
#django.setup()
from golf_app.models import Tournament, TotalScore, ScoreDetails, Field, Picks, PickMethod, BonusDetails, PGAWebScores
from django.contrib.auth.models import User
from datetime import datetime, timedelta

from django.db.models import Min, Q, Count, Sum, Max
from requests import get
#from selenium import webdriver
import urllib
#from selenium.webdriver import Chrome
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

class updateWeeklyScore(object):

    def __init__(self, score_dict, tournament):
        self.score_dict = score_dict
        self.tournament = tournament

    @transaction.atomic
    def update(self):
        #print (self.score_dict)
        PGAWebScores.objects.filter(tournament=self.tournament).delete()
        for g, data in self.score_dict.items():
            try:
                #print (g.split('(')[0].split(',')[0], data)
                print (g, data)
                score = PGAWebScores()
                score.tournament=self.tournament
                score.golfer=Field.objects.get(tournament=self.tournament, \
                                        playerName=g.split('(')[0].split(',')[0])
                score.rank = data.get('rank')
                score.change = data.get('change')
                score.thru = data.get('thru')
                score.round_score = data.get('round_score')
                score.total_score = data.get('total_score')
                score.r1 = data.get('r1')
                score.r2 = data.get('r2')
                score.r3 = data.get('r3')
                score.r4 = data.get('r4')
                score.save()
            except ObjectDoesNotExist:
                pass
            except Exception as e:
                print ('score update fail', e)






