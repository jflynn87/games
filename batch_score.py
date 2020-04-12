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


## comment out to rerun
t = Tournament.objects.get(current=True)
if t.complete:
    print (t, 'complete')
    exit()

if datetime.now() < t.score_update_time + timedelta(minutes=15):
    print (datetime.now())
    print (t.score_update_time)
    print (t.score_update_time + timedelta(minutes=15))
    exit()

print (t, 'active, loading scores')
print ('score batch starting', datetime.now())

web = scrape_scores.ScrapeScores(t)

if len(web) == 0:
    print (t, 'leaderboard empty')
    exit()


## end comment for rerun


#### comment out for regular run.
#t = Tournament.objects.get(pga_tournament_num='010', season__current=True)

#for bd in BonusDetails.objects.filter(tournament=t):
#    bd.winner_bonus = 0
#    bd.cut_bonus = 0
#    bd.major_bonus = 0
#    bd.save()

#t.winner = ' '
#t.current = True
#t.save()

#url = "https://www.pgatour.com/competition/2020/the-honda-classic/leaderboard.html"

#print (t, 'active, loading scores')
#print ('score batch starting', datetime.now())

#web = scrape_scores.ScrapeScores(t, url)

### end re-run uncomment

score_dict = web.scrape()
scores = manual_score.Score(score_dict, t)
scores.update_scores()
scores.total_scores()
#print(score_dict)
#update_golf_score.updateWeeklyScore(score_dict, t).update()
#t.score_update_time = datetime.now()
#t.save()
print (' score batch complete', datetime.now())

