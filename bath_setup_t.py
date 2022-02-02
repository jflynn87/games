import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")


from dotenv import load_dotenv
project_folder = os.path.expanduser('~')
load_dotenv(os.path.join(project_folder, '.env'))

SECRET_KEY = os.environ['SECRET_KEY']

import django
django.setup()
from golf_app.models import Tournament, TotalScore, ScoreDetails, Field, Picks, PickMethod, BonusDetails
from golf_app import populateField
from django.contrib.auth.models import User
from datetime import datetime, timedelta, timezone
import sys
import json


print ('before set up current Tournament : ', Tournament.objects.filter(current=True))
start = datetime.now()
populateField.create_groups(tournament_number='005', espn_t_num='401353235')

print ('set up complete', Tournament.objects.filter(current=True))

print ('SEtup Duration: ', datetime.now() - start)
print (Field.objects.filter(tournament__current=True))

