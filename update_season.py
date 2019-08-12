import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()

from fb_app.models import Season, Week

def update():
    for week in Week.objects.all():
        if week.season_model == None:
            season = Season.objects.get(season=week.season)
            week.season_model = season
            week.save()

update()
