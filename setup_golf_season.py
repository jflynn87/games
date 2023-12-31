import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")
import django
django.setup()

from golf_app.models import *
from golf_app import pga_t_data, espn_schedule 
import ssl
#First set up season model manually in Admin

season = Season.objects.get(current=True)
ssl._create_default_https_context = ssl._create_unverified_context
pga = pga_t_data.PGAData(season, update=False)
sched = espn_schedule.ESPNSchedule().get_event_list()

print (pga.next_t())
#for t, data in sched.items():
#    print (t, data)

#for t, data in pga.items():
#    print (t, data)
