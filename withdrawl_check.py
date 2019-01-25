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
from golf_app import calc_score
from django.core.mail import send_mail
from gamesProj import settings
import datetime

def withdrawls():

    tournament = Tournament.objects.get(current=True)
    print ('now', datetime.date.today())
    print ('time delta', datetime.date.today() - datetime.timedelta(days=2))

    try:
        score_file = calc_score.getRanks({'pk': tournament.pk})
        if score_file[0].get('started') == False and score_file[0].get('finished') == False:
            field_wd_list = []
            pick_wd_dict = {}
            for golfer in Field.objects.filter(tournament=tournament):
                if golfer.playerName not in score_file[0].keys():
                    field_wd_list.append(golfer.playerName)
            for user in User.objects.all():
                if Picks.objects.filter(user=user, playerName__tournament=tournament).exists():
                    pick_wd_list = []
                    for pick in Picks.objects.filter(playerName__tournament=tournament):
                        if pick.playerName.playerName not in score_file[0].keys():
                            pick_wd_list.append(pick.playerName.playerName)
                    if len(pick_wd_list) > 0:
                        pick_wd_dict[user]=pick_wd_list
            print (field_wd_list, pick_wd_dict)

            print ('field list', len(field_wd_list))
            print ('picjs', len(pick_wd_dict.values()))

            if len(field_wd_list) > 0 and len(pick_wd_dict) >0:
                mail_field = "golfers who have withdrawn: " + str(field_wd_list) + "\r"
                mail_picks = "picks that have WD (please update): " + str(pick_wd_dict) + "\r"
            elif len(field_wd_list) > 0:
                mail_field = "golfers who have withdrawn: " + str(field_wd_list) + "\r"
                mail_picks = "No picks for withdrawls"+ "\r"
            else:
                mail_field = "No withdrawls" + "\r"
                mail_picks = '' + "\r"

            mail_recipients = []
            if not settings.DEBUG:
                for user in User.objects.filter(email__gt=''):
                    mail_recipients.append(user.email)
            else:
                mail_recipients = ['jflynn87@hotmail.com']
        else:
            print ('not within tournament window')
            exit()

    except Exception as e:
        mail_field = "No score file yet" + "\r" + str(e) + "\r"
        mail_picks = '' + "\r"
        mail_recipients = ['jflynn87@hotmail.com']
        print ('score file lookup issue', e)

    mail_sub = "Golf Game Withdrawl Update"
    mail_t = "Tornament: " + tournament.name + "\r"
    mail_url = "Website to make changes or picks: " + "http://jflynn87.pythonanywhere.com"

    mail_content = mail_t + "\r" + mail_field + "\r" +mail_picks + "\r"+ mail_url
    print (mail_recipients)
    send_mail(mail_sub, mail_content, 'jflynn87g@gmail.com', mail_recipients)  #add fail silently

withdrawls()
