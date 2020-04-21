import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from run_app.models import Schedule, Plan, Run
from datetime import timedelta, datetime
import sqlite3
from django.db.models import Min, Q, Count, Sum, Max
from django.db.models.functions import ExtractWeek, ExtractYear


import urllib3.request
import urllib
import urllib3
from bs4 import BeautifulSoup
import json

import urllib3.request
from bs4 import BeautifulSoup
from run_app import scrape_runs

web = scrape_runs.ScrapeRuns()


print (web.scrape())

#runs = Run.objects.filter(date__gte=datetime.strptime('2018-12-31', '%Y-%m-%d')).values('date').annotate(Count('date'))
#for r in runs:
#    if r.get('date__count') > 1:
#        print (r)

