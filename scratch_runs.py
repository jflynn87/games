import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from run_app.models import Schedule, Plan, Run
from datetime import datetime, timedelta
import sqlite3
from django.db.models import Min, Q, Count, Sum, Max
from django.db.models.functions import ExtractWeek, ExtractYear

def get_schedule():

    import urllib3.request
    import urllib
    import urllib3
    from bs4 import BeautifulSoup
    import json

    import urllib3.request
    from bs4 import BeautifulSoup

    #plan = Plan.objects.get(pk=1)
    #today = datetime.now()
    #print (Schedule.objects.filter(Q(plan__id=plan.id) & Q(date__lte=today) & Q(date__gte='2018-12-17') & Q(dist__gt=0)).aggregate((Sum('dist')), (Count('date'))))
    #for  run in Schedule.objects.filter(Q(plan__id=plan.id) & Q(date__lte=today) & Q(date__gte='2018-12-17') & Q(dist__gt=0)):
    #    print (run)


    week_start = datetime.today() - timedelta(days=180)

    for week in (Run.objects.filter(date__gte=week_start).annotate(year=ExtractYear('date')).annotate(week=ExtractWeek('date')).values('year', 'week')
    .annotate(total_dist=Sum('dist'), time=Sum('time'), cals=Sum('cals'), num=Count('date'), max_dist=(Max('dist'))).order_by('-year', '-week')):
        print (week)





get_schedule()
