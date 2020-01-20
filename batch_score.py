import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from golf_app.models import Tournament, TotalScore, ScoreDetails, Field, Picks, PickMethod, BonusDetails
from django.contrib.auth.models import User
from datetime import datetime, timedelta, timezone
from golf_app import scrape_scores
from golf_app import update_golf_score

t = Tournament.objects.get(current=True)
print ('score batch starting', datetime.now())
scores = scrape_scores.ScrapeScores()
score_dict = scores.scrape()
#print(score_dict)
update_golf_score.updateWeeklyScore(score_dict, t).update()
t.score_update_time = datetime.now()
t.save()
print (' score batch complete', datetime.now())

