import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")


from dotenv import load_dotenv
project_folder = os.path.expanduser('~')
load_dotenv(os.path.join(project_folder, '.env'))

SECRET_KEY = os.environ['SECRET_KEY']

import django
django.setup()
from golf_app.models import Tournament, TotalScore, ScoreDetails, Field, Picks, PickMethod, BonusDetails
from django.contrib.auth.models import User
from datetime import datetime, timedelta, timezone
from golf_app import scrape_scores
from golf_app import manual_score
from golf_app import withdraw
from django.core.mail import send_mail


t = Tournament.objects.get(current=True)

if t.started():
    print (t.name, ': started, exiting')
    exit()


#t = Tournament.objects.get(pk=95)
#if t.started():
#    print ('tournament started')
#    exit()

wd = withdraw.WDCheck(t)
score = wd.check_wd() 
wd_picks = wd.check_wd_picks()

print ('wd', score['wd_list'], len(score['wd_list']))
print ('no wd', score['good_list'], len(score['good_list']))
print ('wd_picks', wd_picks)

mail_field = "golfers who have withdrawn: "

if len(score['wd_list']) > 0:
    for golfer in score['wd_list']:
        mail_field = mail_field + golfer + ", "

    for golfer, user in wd_picks.items():
        mail_field = mail_field + "\r" 
        golfer, user
else:
    mail_field = "no wd's"

mail_picks = ''

pick_status_dict = {}
for player in t.season.get_users():
    print(player)
    user = User.objects.get(id=player.get('user'))
    pick_status_dict[user.username] = str(Picks.objects.filter(user__id=user.id, playerName__tournament=t).count())
    

mail_sub = "Golf Game Withdrawal Update"
mail_t = "Tournament: " + t.name + "\r"
mail_url = "Website to make changes or picks: " + "http://jflynn87.pythonanywhere.com"
mail_content = mail_t + "\r" + mail_field + "\r" +mail_picks + "\r"+ mail_url + "\r" 
for p, c in pick_status_dict.items():
    mail_content = mail_content + "\r" + p + ' pick count:  ' + c

mail_recipients = ['jflynn87@hotmail.com']
send_mail(mail_sub, mail_content, 'jflynn87g@gmail.com', mail_recipients)  #add fail silently

