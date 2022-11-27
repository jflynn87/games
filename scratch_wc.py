import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")
import django
django.setup()

from wc_app import wc_group_data
from wc_app.models import Event, Group, Team, Picks, Stage, Data
from django.contrib.auth.models import User
from django.db.models import Min, Q, Count, Sum, Max
from datetime import datetime

#e = wc_group_data.ESPNData().get_group_data()

for t in Team.objects.filter(group__group="Final 16").order_by('rank'):
    print (t, t.rank, t.ko_first_game())

exit()

Team.objects.filter(group__group='Final 16').delete()
stage = Stage.objects.get(name="Group Stage")
e  = Data.objects.get(stage=stage)
print (e.group_data.keys())
ko_group = Group.objects.get(group="Final 16")

for g in Group.objects.filter(stage=stage):
    #rank = [data.get('rank') for k,v in espn.items() for t, data  in v.items() if t == team.name][0]
    d = [(t,data.get('rank')) for k,v in e.group_data.items() for t, data in v.items() if data.get('rank') in ['1', '2'] and k == g.group ]
    #print (g.group[-1].lower(),ord(g.group[-1].lower()) -96, d)
    for x in d:
        if int(x[1]) == 1:
            rank = ord(g.group[-1].lower()) -96
        else:
            rank = (ord(g.group[-1].lower()) -96) + 8
        t_data = Team.objects.get(name=x[0], group__stage__name="Group Stage")
        team = Team()
        team.group = ko_group
        team.name = x[0]
        team.rank = rank
        team.flag_link = t_data.flag_link

        team.save()

        print (g, x[0], rank)


exit()

wc = wc_group_data.ESPNData(url='https://www.espn.com/soccer/standings/_/league/FIFA.WORLD/season/2018')
#print (wc.get_rankings(use_file=True))

espn = wc.get_group_data(create=True)
# loop_start = datetime.now()
# for g in Group.objects.filter(stage__current=True):
#     x = [k for k, v in sorted(espn.get(g.group).items(), key= lambda r: r[1].get('rank'))]
#     for u in User.objects.filter(pk__in=[1,2]):
#         if Picks.objects.filter(team__name=x[0], rank=1, user=u).exists() and \
#             Picks.objects.filter(team__name=x[1], rank=2, user=u).exists() and \
#             Picks.objects.filter(team__name=x[2], rank=3, user=u).exists() and \
#             Picks.objects.filter(team__name=x[3], rank=4, user=u).exists():
#                 print (g, 'right picks')
# print ('pefect picks loop: ', datetime.now() - loop_start)

users = [1, 2]

for x in users:
    u = User.objects.get(pk=x)
    Picks.objects.filter(team__group__stage__current=True, user=u).delete()

    for g in Group.objects.filter(stage__current=True):
        for i, team in enumerate(Team.objects.filter(group=g)):
            p = Picks()
            p.user = u
            p.rank = i + 1
            p.team = team
            p.save()

exit()


#record = wc.get_group_records(groups)

stage = Stage.objects.get(current=True)
#for p in Picks.objects.filter(stage=stage):
    

exit()


event = Event.objects.all().first()
stage = Stage.objects.get(event=event, current=True) 
wc = wc_group_data.ESPNData()

groups = wc.get_group_data()
rankings = wc.get_rankings()

Team.objects.all().delete()

for group, teams in groups.items():
    g, g_created = Group.objects.get_or_create(stage=stage, group=group)
    for team, data in teams.items():
        t, t_created = Team.objects.get_or_create(group=g, name=team,\
             rank=rankings.get(team).get('rank'), flag_link=data.get('flag'), \
             info_link=data.get('info'), full_name=data.get('full_name')) 

print ('Groups: ', Group.objects.filter(stage__event=event).count(), ' Teams: ', Team.objects.filter(group__stage__event=event).count())        

#print (rankings)
 