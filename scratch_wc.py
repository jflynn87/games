import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")
import django
django.setup()

from wc_app import wc_group_data, wc_ko_data, wbc_group, wbc_group_standings, mlb_group_stage, wbc_ko_data
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

d = wbc_group.TeamData().create_teams()

print (d)

exit()

#e = wbc_ko_data.ESPNData()
#data = e.data
#print (e.data)

data_obj = Data.objects.get(stage__event__current=True, stage__name='Group Stage')

Picks.objects.filter(team__group__stage__current=True, rank__in=[5,6,7]).delete()

for t in Team.objects.filter(group__stage__current=True):
    if t.full_name == 'United States':
        t.rank = 2
    elif t.full_name == 'Venezuela':
        t.rank = 3
    #elif t.full_name == 'Australia':
    #    t.rank = 4
    elif t.full_name == 'Japan':
        t.rank = 5
    elif t.full_name == 'Puerto Rico':
        t.rank = 6
    elif t.full_name == 'Mexico':
        t.rank = 7
    elif t.full_name == 'Italy':
        t.rank = 8
    elif t.full_name in ['Cuba', 'Australia']:
        continue

    else: raise Exception('t rank issue ', t)

    t.early_game = True
    t.save()

for p in Picks.objects.filter(team__group__stage__current=True):
    print (p.team.full_name)
    if p.team.full_name != 'United States':
        group_team = Team.objects.get(group__stage__name='Group Stage', full_name=p.team.full_name, group__stage__event__current=True)
    else:        
        group_team = Team.objects.get(group__stage__name='Group Stage', full_name='USA', group__stage__event__current=True)
    data = data_obj.group_data.get(group_team.group.group).get(group_team.full_name).get('rank')
    print ('data: ', p.team, type(data), data)
    if data == 1:
        f = 'fav'
    elif data == 2:
        f = 'dog'
    else:
        raise Exception ('bad')
    print (p.team, f)
    if p.data.get('from_ele')[:2] == 'm2':
        p.data = {'from_ele': 'm3_' + f}
        print ('M2 - M3', p.data)
        p.save()
    elif p.data.get('from_ele')[:2] == 'm3':
        p.data = {'from_ele': 'm4_' + f}
        print ('M3 - M4', p.data)
        p.save()
    elif p.data.get('from_ele')[:2] == 'm4':
        p.data = {'from_ele': 'm2_' + f}
        print ('M4 - M2', p.data)
        p.save()
    print ('--------------------------------------------')




#e = wbc_group_standings.ESPNData()
#data = e.get_team_data()
#print(data)
# pool = e.teams_by_pool()
# for p, v in pool.items():
#     print (p)
#     for key, team_d in v.items():
#         print (team_d)

print (datetime.now() - start)


exit()

#usa = [data.get('rank') for key, team_info in e.get_team_data() for team_name, data in team_info.items() if team_name == t.get('full_name')][0]
#print (data)

#for t in Team.objects.filter(group__stage__current=True, group__group="Pool A"):
for t in Team.objects.filter(group__stage__current=True):
    print (e.get_rank(t, data=data))

print ('dur: ', datetime.now() - start)

exit()

pcts = [{'abbr':v.get('abbr'), 'pct': v.get('pct')} for k, v in e.get_team_data().items() if v.get('pool') == t.group.group]

sorted_pcts = sorted(pcts, key=lambda x:x.get('pct'))
print (sorted_pcts)
#print (sorted_pcts.index([v for v in sorted_pcts if v.get('abbr') == t.name]))
idx = next((index for (index,d ) in enumerate(sorted_pcts) if d['abbr'] == t.name)) 
print (idx)

while True:
    if idx != 1 and sorted_pcts[idx].get('pct') == sorted_pcts[idx-1].get('pct'):
        idx -= 1
    else:
        if idx == 1:
            rank = 1
        else:
            rank = idx + 1
        break

print (rank)

exit()

##setup event logic
# e = Event.objects.get(current=True)
# stage, s_created = Stage.objects.get_or_create(event=e, current=True)
# stage.name = "Group Stage"
# stage.curret = True
# stage.pick_type = 1
# stage.score_url = 'https://www.espn.com/world-baseball-classic/standings'
# stage.save()
# espn = wbc_group_standings.ESPNData()

# #for k, v in d.items():
# #    print(k, v)
# #    print ('----')

# #print (datetime.now() - start)

# data = {}
# data['group_stage_rules'] = ['<ul> \
#     <li>Choose the rank within the group for each team</li> \
#     <li>If your #1 or #2 pick finishes in first or second place: +3 points</li> \
#     <li>If your first place pick finishes in first place: +2 points - not available in case of a tie</li> \
#     <li>All picks in Group correct (1st, 2nd, 3rd, 4th, 5th): +5 points </li> \
#     <li>Upset bonus:  if the 3rd, 4th or 5th ranked teams finishes first or second, bonus points = (team rank - second best rank) *.3.  Rounded to 2 decimal places (if you picked one of those teams in 1st and they finish 1st you also get the first place bonus)</li> \
#     <li>Tie breaker - applied in this order: winning %, highest runs scored, lowest runs against.  If all are equal, then it is a tie and picks will be correct for either rank of the tied teams.</li> \
#     </ul>' ]
# data['group_stage_ranks_msg'] = ['<p>Current WBC Rankings taken from <a href="https://en.wikipedia.org/wiki/2023_World_Baseball_Classic">HERE</a> as of 3/1/2023</p>'] 
# data['group_stage_group_count'] = 4
# data['group_stage_teams_per_group'] = 5

# e.data = data
# e.save()

# pools = espn.get_pool_names()
# print ('pools: ', pools)

# for p in pools:
#     g, g_created = Group.objects.get_or_create(stage=stage, group=p)

# d = espn.get_team_data()
# wbc = wbc_group.TeamData()
# teams = wbc.data
# print (teams)

# for key, t in d.items():
#     team, t_created = Team.objects.get_or_create(group=Group.objects.get(stage=stage, group=t.get('pool')), name=t.get('abbr'))
#     team.name = t.get('abbr')
#     team.full_name = t.get('full_name')
#     team.flag_link = t.get('flag')
#     try:
#         rank = [data.get('rank') for pool, team_info in teams.items() for team_name, data in team_info.items() if team_name == t.get('full_name')][0]
#     except Exception as e:
#         print ('fix Korea')
#         rank = [data.get('rank') for pool, team_info in teams.items() for team_name, data in team_info.items() if team_name == "South Korea"][0]
#     print (t.get('full_name'), rank)
#     team.rank = int(rank)
#     team.save()



# exit()
##end setup event logic


web_url = 'https://en.wikipedia.org/wiki/2023_World_Baseball_Classic'
context = ssl._create_unverified_context()
headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
#url =  "https://site.web.api.espn.com/apis/site/v2/sports/golf/leaderboard?league=pga"

#html = get(web_url, headers=headers)


html = urlopen(web_url, context=context)
#html = get(web_url)
soup = BeautifulSoup(html, 'html.parser')

tables = soup.find_all('table', {'class': 'wikitable'})

table = tables[4]
data = {}
for i, row in enumerate(table.find_all('tr')):
    if i == 0:
        for j, th in enumerate(row.find_all('th')):
            t = th.text.split('(')[0].strip()
            data[t] = {}
            if j == 0:
                a = t
            elif j == 1: 
                b = t
            elif j == 2:
                c = t
            elif j == 3:
                d = t
            else:
                raise Exception('I index error, why are we here')
    else:
        for k, td in enumerate(row.find_all('td')):
            country = td.text.split('(')[0].strip()
            rank = td.text.split('(')[1].strip()
            if k == 0:
                data[a].update({country: {'rank': rank}})
            elif k == 1:
                data[b].update({country: {'rank': rank}})
            elif k == 2:
                data[c].update({country: {'rank': rank}})
            elif k == 3:
                data[d].update({country: {'rank': rank}})
            else:
                raise Exception('J index issue, why here')

print (data)





exit()

for u in e.get_users():
    print (u)
# stage = Stage.objects.get(name="Knockout Stage")

# e = wc_ko_data.ESPNData()
# espn = e.api_winners_losers()

# print (espn)
# print (e.stage_complete())

# print (datetime.now() - start)

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
 