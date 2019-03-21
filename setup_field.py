import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

from dotenv import load_dotenv
project_folder = os.path.expanduser('~')
load_dotenv(os.path.join(project_folder, '.env'))

SECRET_KEY = os.environ['SECRET_KEY']

import django
django.setup()
from golf_app.models import Tournament, Field, Picks, User
#import sqlite3
#from django.db.models import Min, Q, Count
import json
import urllib.request
from golf_app import populateField


from django.core.mail import send_mail
from gamesProj import settings
import datetime

def setup(tournament_num=None):

    if tournament_num == None:
        url = 'https://statdata.pgatour.com/r/current/message.json'
        with urllib.request.urlopen(url) as tournament_url:
            data = json.loads(tournament_url.read().decode())
        id = data['tid']
    else:
        id = tournament_num

    if Tournament.objects.filter(pga_tournament_num=id, season__current=True).exists():
        print ('tournament exists')
        msg = "Tournament Exists"
    else:
        print ('creating tournament')
        msg = "creating tournament"
        populateField.create_groups(id)

    missing_owgr = list(Field.objects.filter(tournament__pga_tournament_num=id, tournament__season__current=True, currentWGR='9999'))
    tournament = Tournament.objects.get(current=True)
    #print (field)

    mail_sub = "Golf Game Setup Update"
    mail_msg = msg + "\r"
    mail_num = "PGA Tournament Number: " + id + "\r"
    mail_t = "Tournament (start date): " + tournament.name + " (" + str(tournament.start_date) + ")" + "\r"
    mail_no_owgr = "Failed OWGR lookups: " + str(missing_owgr)
    mail_recipients = ["jflynn87@hotmail.com",]

    # mail_url = "Website to make changes or picks: " + "http://jflynn87.pythonanywhere.com"
    #
    mail_content = mail_msg + "\r" + mail_num + "\r" + mail_t + "\r"+ mail_no_owgr
    # print (mail_recipients)
    send_mail(mail_sub, mail_content, 'jflynn87g@gmail.com', mail_recipients)  #add fail silently

setup()
