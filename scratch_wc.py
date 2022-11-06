import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")
import django
django.setup()

from wc_app import wc_group_data
from wc_app.models import Event, Group, Team, Picks



event = Event.objects.all().first()
wc = wc_group_data.ESPNData()

groups = wc.get_group_data()
rankings = wc.get_rankings()

Team.objects.all().delete()

for group, teams in groups.items():
    g, g_created = Group.objects.get_or_create(event=event, group=group)
    for team, data in teams.items():
        t, t_created = Team.objects.get_or_create(group=g, name=team,\
             rank=rankings.get(team).get('rank'), flag_link=data.get('flag'), \
             info_link=data.get('info'), full_name=data.get('full_name')) 

print ('Groups: ', Group.objects.filter(event=event).count(), ' Teams: ', Team.objects.filter(group__event=event).count())        

#print (rankings)
 