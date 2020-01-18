import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from golf_app.models import Tournament, TotalScore, ScoreDetails, Field, Picks, PickMethod, BonusDetails
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from golf_app import scrape_scores
from golf_app import update_golf_score

t = Tournament.objects.get(current=True)
print ('batch starting', datetime.now())
scores = scrape_scores.ScrapeScores()
score_dict = scores.scrape()
update_golf_score.updateWeeklyScore(score_dict, t).update()
print ('batch complete', datetime.now())

