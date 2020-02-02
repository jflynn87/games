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

t = Tournament.objects.get(current=True)
if t.complete:
    print (t, 'complete')
    exit()

print (t, 'active, loading scores')
print ('score batch starting', datetime.now())
web = scrape_scores.ScrapeScores(t)
score_dict = web.scrape()
scores = manual_score.Score(score_dict, t)
scores.update_scores()
#print(score_dict)
#update_golf_score.updateWeeklyScore(score_dict, t).update()
#t.score_update_time = datetime.now()
#t.save()
print (' score batch complete', datetime.now())

