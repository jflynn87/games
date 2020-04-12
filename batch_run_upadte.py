import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from run_app.models import Schedule, Plan, Run, Shoes
from datetime import timedelta
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
import csv
import datetime
from datetime import timedelta

file = 'cardioActivities.csv'
with open(file, encoding="utf8") as csv_file:
     csv_reader = csv.reader(csv_file, delimiter=',')
     for row in csv_reader:
         #print (row)
         if row[2] == 'Running':
            
            t = row[5]
        
            if t.count(':') == 1:
        
               time = datetime.timedelta(minutes=int(t.split(':')[0]), seconds=int(t.split(':')[1]))
            elif t.count(':') == 2:
               time = datetime.timedelta(hours=int(t[0]), minutes=int(t[2:4]), seconds=int(t[5:7]))
            else:
        
               time = datetime.timedelta(0)

            if datetime.datetime.strptime(row[1].split(' ')[0], '%Y-%m-%d') > datetime.datetime.strptime('2018-12-31', '%Y-%m-%d'):

               if not Run.objects.filter(date=datetime.datetime.strptime(row[1].split(' ')[0], '%Y-%m-%d')).exists():
                  
                  Run.objects.get_or_create(date=datetime.datetime.strptime(row[1].split(' ')[0], '%Y-%m-%d'),
                  dist = row[4], 
                  time = time,
                  cals = int(row[8].split('.')[0]),
                  shoes = Shoes.objects.get(main_shoe=True),
                  location = 1
         
                  
                  )


             #print (row[1].split(' ')[0], row[4], row[5], row[8])

