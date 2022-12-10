import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")
import django
django.setup()

from wc_app import wc_group_data, wc_ko_data
from wc_app.models import Event, Group, Team, Picks, Stage, Data
from django.contrib.auth.models import User
from django.db.models import Min, Q, Count, Sum, Max
from datetime import datetime
from requests import get
import json
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from datetime import datetime

start = datetime.now()
stage = Stage.objects.get(name="Knockout Stage")

#espn = wc_ko_data.ESPNData().api_winners_losers()
#print (espn)

for p in Picks.objects.filter(team__group__group='Final 16').order_by('rank'):
    if p.rank in [13, 14]:
        #print (p.team, p.rank, p.calc_score(espn, 'api'))
        right_pick = p.ko_fix_picks()
        print (p.user , p.team, p.rank, right_pick.team)
        p.team = right_pick.team
        p.save()

print (datetime.now() - start)

exit()


order = stage.ko_match_order()
left = order[0:8]
right = order[8:]
print (order)
for t in Team.objects.filter(group__stage=stage):
    print (t, t.rank)

for u in stage.event.get_users():
    print (u)
    left_side = 0
    right_side = 0

    for p in Picks.objects.filter(user=u, team__group__stage=stage):
        if p.team.rank in left:
            left_side += 1 
        elif p.team.rank in right:
            right_side += 1

    p_9 = Picks.objects.get(user=u, team__group__stage=stage, rank=9)
    p_10 = Picks.objects.get(user=u, team__group__stage=stage, rank=10)
    print (p_9, p_10)
    if p_9.team.rank not in left:
        print ('1313131313 - error')
    if p_10.team.rank not in left:
        print ('1414141414 - error')

    print ('left: ', left_side)
    print ('right: ', right_side)
exit()



for p in Picks.objects.filter(team__group__group='Final 16', user__pk=1).order_by('rank'):
    print (p.team.name, p.rank)

for t in Team.objects.filter(group__group='Final 16'):
    full_team = Team.objects.get(group__stage__name='Group Stage', name=t.name)
    t.full_name = full_team.full_name
    t.save()
exit()

espn = wc_ko_data.ESPNData(source='web')
#espn = wc_ko_data.ESPNData()
for s, l in espn.web_get_data().items():
    print (s, l)

for t in Team.objects.filter(group__group="Final 16"):
    print (t, len([x for k,x in espn.web_get_data().items() if t.full_name in x]))
exit()

#url = 'https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard'
url = 'https://site.api.espn.com/apis/v2/scoreboard/header?sport=soccer&league=fifa.world'
headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
#url =  "https://site.web.api.espn.com/apis/site/v2/sports/golf/leaderboard?league=pga"

all_data = get(url, headers=headers).json()

#with open('wc_api.json', 'w') as outfile:
#    json.dump(all_data, outfile, indent=4)

for sport in all_data.get('sports'):
    print (sport.get('name'))
    for league in sport.get('leagues'):
        print (league.keys(), league.get('name'))
        for event in league.get('events'):
            #print (event.keys())
            print (event.get('group'), event.get('summary'))

#print(json.dumps(all_data, indent=4))

web_url = 'https://www.espn.com/soccer/bracket'

html = urlopen(web_url)
#html = get(web_url)
soup = BeautifulSoup(html, 'html.parser')

bracket = soup.find('div', {'class': 'BracketLayout'})

#for group in bracket.find_all('div', {'data-testid': 'regionRound'}):
for game in bracket.find_all('div', {'class': 'BracketCell__Competitors'}):
    for team in game.find_all('div', {'class': 'BracketCell__Name'}):
        print (team.text)



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
 