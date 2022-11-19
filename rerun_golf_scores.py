import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")
import django
django.setup()
from golf_app.models import Tournament, TotalScore, ScoreDetails, Picks, PickMethod, BonusDetails, \
        Season, Golfer, Group, Field, ScoreDict, AuctionPick, AccessLog, StatLinks, CountryPicks, \
         FedExSeason, FedExField, FedExPicks
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from golf_app import populateField, calc_leaderboard, manual_score, bonus_details, espn_api, \
                     round_by_round, scrape_espn, utils, golf_serializers, espn_schedule, \
                     scrape_scores_picks, espn_ryder_cup, withdraw, fedex_email, pga_t_data, fedexData, \
                     setup_fedex_field
from django.db.models import Count, Sum
from unidecode import unidecode as decode
import json
from requests import get
from collections import OrderedDict
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from golf_app import views
from django.core import serializers
from django.db.models import  Q, Min, Max
import urllib
from pprint import pprint
import csv
from rest_framework.request import Request
from django.http import HttpRequest
import numpy as np
import pytz
from operator import itemgetter


def rerun(t):
    start = datetime.now()

    if t.complete:
        r = HttpRequest()
        req = views.EspnApiScores().get(r, t.pk, rerun=True)
        return req
    else:
        print ("Cant rerun, not complete", t, t.complete)

t_num = '020'
t = Tournament.objects.get(pga_tournament_num=t_num, season__current=True)
print ('reruning score: ', t)
if t.complete:
    r = rerun(t)
    print ('rerun complete', t, r)
else:
    print ('Tournament Not Complete, check', t, t.complete)


