import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
 
from fb_app.models import Season, Week, Games, Teams, Picks, League, Player,  MikeScore, WeekScore, PickPerformance, PlayoffStats, PickMethod, SeasonPicks
from django.contrib.auth.models import User
from datetime import datetime, timedelta, timezone, tzinfo
from django.db.models import Min, Q, Count, Sum, Max, F
from django.db.models.functions import ExtractWeek, ExtractYear
import time
import urllib
from urllib import request
import json
from fb_app import fb_serializers
#from fb_app.scores import Scores
#from urllib.request import Request, urlopen
#from selenium.webdriver import Chrome, ChromeOptions
#

#
import requests
#from linebot import LineBotApi
#from linebot.models import TextSendMessage
#from linebot.exceptions import LineBotApiError
from bs4 import BeautifulSoup
from fb_app import scrape_cbs, scrape_cbs_playoff, playoff_stats, espn_data 
from user_app import espn_baseball
import pytz
from django.core import serializers
#import docx2txt
from math import ceil
from fb_app import views
from django.http import HttpRequest
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
import pprint
#import tabula

#headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
#url = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"

#payload = {'week': str(1)}
    #print ('payload ', payload)
    #payload = {}  #works for pre season/current week?
#else:
#    payload = {}  #works for preseason and post season
#json_data = requests.get(url, headers=headers, params=payload).json()
#print (json_data)
#print (json_data.keys())
#print ('espn week: ', json_data.get('week'))
#print (json.dumps(json_data, indent=4, sort_keys=True))


#f = open('espn_schedule.json', "w")
#f.write(json.dumps(json_data, indent=5))
#f.close()


start = datetime.now()
#headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
#url = 'https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard'
#data = requests.get(url, headers=headers).json() 

#for game in data.get('events'):
#    print (game.get('name'), game.get('status').get('period'), game.get('status').get('type').get('completed'))
#    for competition in game.get('competitions'):
#        for competitor in competition.get('competitors'):
#            print (competitor.get('team').get('name'), competitor.get('score'), competitor.get('winner') )

s = Season.objects.get(season=2021)
pp = PickPerformance.objects.get(season=s, league=League.objects.get(league='Golfers'))
d = json.loads(pp.data)
r = {'tot_win': 0,
    'tot_loss': 0}
for u, stats in d.items():
    r[u] = {'win': 0,
            'loss': 0
            }
    win = 0
    loss = 0
    for team, data in d.get(u).items():
        win += data.get('right')
        loss += data.get('wrong')
    r.get(u).update({'win': r.get(u).get('win') + win,
                    'loss': r.get(u).get('loss') + loss,
                                              })
    r.update({'tot_win': r.get('tot_win') + win}) 
    r.update({'tot_loss':   r.get('tot_loss') + loss})

print (r)
print ('R: ', datetime.now() - start)

print (Games.objects.filter(week__season_model=s, week__week__lte=18, home=F('winner')).count())
print (Games.objects.filter(week__season_model=s, week__week__lte=18, away=F('winner')).count())
print (Games.objects.filter(week__season_model=s, week__week__lte=18, tie=True).count())


print (SeasonPicks.objects.filter(season__current=True, player=Player.objects.get(name=User.objects.get(pk=1)), pick=F('game__home')).count())
print (SeasonPicks.objects.filter(season__current=True, player=Player.objects.get(name=User.objects.get(pk=1)), pick=F('game__away')).count())

print (s.home_wins())
print (s.away_wins())

print (Player.objects.get(name=User.objects.get(pk=1)).home_season_picks(Season.objects.get(current=True)))
print (Player.objects.get(name=User.objects.get(pk=1)).away_season_picks(Season.objects.get(current=True)))

exit()

espn = espn_baseball.ESPNData()
print (espn.get_score(['21']))
print (datetime.now() - start)

exit()

start = datetime.now()
d = {}
for p in Player.objects.filter(league__league='Golfers', active=True):
    d.update({p.name.username: {'score': 0, 'proj_score': 0}})
espn = espn_data.ESPNData()
#first_game = espn.first_game_of_week()[0]
for g in Games.objects.filter(week__current=True):
    #print (espn.get_team(g.eid, 'home'),
    home_score =  espn.get_team_score(g.eid, 'home')
    #print (espn.get_team(g.eid, 'away'), 
    away_score = espn.get_team_score(g.eid, 'away')
    winner = espn.game_winner(g.eid)
    loser = espn.game_loser(g.eid)
    if espn.game_complete(g.eid):
        for pick in Picks.objects.filter(team=Teams.objects.get(nfl_abbr=loser), week=g.week, player__league=League.objects.get(league="Golfers"), player__active=True):
            d.get(pick.player.name.username).update({'score': d.get(pick.player.name.username).get('score') + pick.pick_num})


print (d)

w = Week.objects.get(current=True)
print (datetime.now() - start)
by_pick_start = datetime.now()
e = {}
for p in Player.objects.filter(league__league='Golfers', active=True):
    e.update({p.name.username: {'score': 0, 'proj_score': 0}})
espn = espn_data.ESPNData()
#values('user_id').distinct().order_by('user_id'):
for p in Picks.objects.filter(week=w, league=League.objects.get(league="Golfers")):
    pass




exit()

espn = espn_data.ESPNData()
print (espn.regular_week())
exit()

week = Week.objects.get(current=True)
d = sorted(week.get_spreads().items(), key=lambda x: x[1][2],reverse=True)
new_d = [x for x in d if x[0] != espn.first_game_of_week()[0]]

print (len(d), len(new_d))
print (new_d)
exit()


#espn.get_data()
print (datetime.now() - start)
est = pytz.timezone('US/Eastern')
utc = pytz.utc

for g in Games.objects.filter(week__current=True):

    print (g ,espn.started(g.eid))
    print (espn.game_date_utc(g.eid), espn.game_date_est(g.eid), espn.game_dow(g.eid))
    #d_utc = utc.localize(datetime.strptime(espn.game_date(g.eid)[:-1], '%Y-%m-%dT%H:%M'))
    #d_est = d_utc.astimezone(est)

#print (Games.objects.get(eid=espn.first_game_of_week()))
start_f = datetime.now()
f = espn.first_game_of_week()
print (datetime.now() - start_f)
print (Games.objects.get(eid=f[0]))
exit()

espn = espn_data.ESPNData().get_orig_data()

with open('data.txt', 'w') as outfile:
    json.dump(espn, outfile)




exit()


pdf = open('Football Fools week 12.pdf', 'rb')
data = tabula.read_pdf('Football Fools week 12.pdf', pages=1)
print (data)
exit()
pdfReader = PyPDF4.PdfFileReader(pdfFileObj)
print (pdfReader.numPages)
pageObj = pdfReader.getPage(0)
#print (pageObj)
print(pageObj.extractText())
pdfFileObj.close()

exit()


for t in Teams.objects.all():
    t.pic = 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/nfl/500/' + str(t.nfl_abbr.lower()) +  '.png'
    t.save()

exit()


view_start = datetime.now()
i = 16
while i >= 1:
    
    req = HttpRequest()
    req.method = 'GET'
    req.data = {'week': '5',
            #'pick_num': str(i),
           'pick_num': i,
            'league': 'Football Fools'}
    view = views.GetPick().post(req)
    #print (view.data)
    i -= 1
    print ('loop: ', datetime.now() - view_start)
print ('view dur: ', datetime.now() - view_start)
exit()


start = datetime.now()
#data = Picks.objects.filter(week__season_model__current=True, week__week=5, player__league__league='Football Fools')
#cProfile.run("fb_serializers.PicksSerializer(Picks.objects.filter(week__season_model__current=True, week__week=5, player__league__league='Golfers'), many=True).data")
data = fb_serializers.PicksSerializer(Picks.objects.filter(week__season_model__current=True, week__week=5, player__league__league='Golfers'), many=True).data

#data = serializers.serialize(queryset=Picks.objects.filter(week__season_model__current=True, week__week=5, player__league__league='Golfers'), format='json')
#week = Week.objects.get(season_model__current=True, week=4)
#load_sheet.readSheet('FOOTBALL FOOLS week 4.xml', 25, week)
#week.update_scores(League.objects.get(league="Football Fools"),  recalc=True)
#for d in data:
print (data)
print ('serializer: ', datetime.now() - start)

view_start = datetime.now()
i = 16
while i >= 1:
    req = HttpRequest()
    req.method = 'GET'
    req.data = {'week': '5',
            'pick_num': str(i),
            'league': 'Golfers'}
    view = views.GetPick().post(req)
    #print (view.data)
    i -= 1
#print (view.__dict__)
print ('view dur: ', datetime.now() - view_start)
exit()

#league = League.objects.get(league="Golfers")
#season = Season.objects.get(current=True)


#stats, created = PickPerformance.objects.get_or_create(season=season, league=league)
#print (stats.team_results('NYG', 'john'))
#stats.calculate()
for score in MikeScore.objects.filter(week__season_model__current=True, player__name__username="JABO"):
    print (score.week, score.total)
    ws = WeekScore.objects.get(player__name__username="JABO", week=score.week)
    print (ws.score)

exit()

for stats in PickPerformance.objects.filter(season__current=True):
    for k,v in json.loads(stats.data).items():
        print (k, v)
    
print (datetime.now() - start)
exit()

week = Week.objects.get(current=True)
print (week.started())
exit()
headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
url = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
payload = {'week':'2'}
#payload = {}
jsonData = requests.get(url, headers=headers, params=payload).json()
print (jsonData.keys())
print (jsonData.get('week'))

f = open('espn_nfl_api.json', "w")
f.write(json.dumps(jsonData))
f.close()

#print (jsonData.get('events'))
for e in jsonData.get('events'):
    print ('-------------------')
    print (e)
exit()

w = Week.objects.get(current=True)
print (w.started())
games = Games.objects.filter(week=w, qtr__isnull=False).exclude(qtr__in=['pregame', 'postponed']).exclude(qtr__icontains='AM').exclude(qtr__icontains='PM')
for g in games:
    print (g.home, g.qtr)
exit()
sched = espn_data.ESPNData().get_data()
print ('dur: ', datetime.now() - start)
print (sched)
exit()


headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
url = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
#payload = {'week':'1'}
payload = {}
jsonData = requests.get(url, headers=headers, params=payload).json()
print (jsonData.keys())
print (jsonData.get('week'))
for l in jsonData.get('events'):
    print (l.get('name'))
    for competition in l.get('competitions'):
        print (competition.get('id'))
        for c in competition.get('competitors'):
            print (c.get('homeAway'), c.get('team').get('name'))
    print ('--------')
exit()
stats_dict = {}

html = urllib.request.urlopen("https://www.cbssports.com/nfl/stats/team/team/total/nfl/regular/")

soup = BeautifulSoup(html, 'html.parser')

teams = soup.find('div', {'id': 'TableBase'})
stats = teams.find_all('tr', {'class': 'TableBase-bodyTr'})

for data in stats:
    row = data.find_all('td')
    team = row[0].a['href'].split('/')[3]
    if team == 'LAR':
        team = "LA"
    gp = row[1].text.strip()
    yards = row[2].text.strip()
    yards_per_game = row[3].text .strip()
    pass_yards = row[4].text.strip()
    pass_yards_per_game = row[5].text.strip()
    rush_yards = row[6].text.strip()
    rush_yards_per_game = row[7].text.strip()
    points = row[8].text.strip()
    points_per_game = row[9].text.strip()

    stats_dict[team] = {
                            'gp': gp, 
                            'yards': yards,
                            'yards_per_game': yards_per_game,
                            'pass_yards': pass_yards,
                            'pass_yards_per_game': pass_yards_per_game,
                            'rush_yards': rush_yards,
                            'rush_yards_per_game': rush_yards_per_game,
                            'points': points,
                            'points_per_game': points_per_game,
                    
    }

#print (stats_dict)
print (datetime.now() - start)

html = urllib.request.urlopen("https://www.cbssports.com/nfl/stats/team/team/defense/nfl/regular/")  # defense

soup = BeautifulSoup(html, 'html.parser')

teams = soup.find('div', {'id': 'TableBase'})
stats = teams.find_all('tr', {'class': 'TableBase-bodyTr'})

for data in stats:
    row = data.find_all('td')
    team = row[0].a['href'].split('/')[3]
    if team == 'LAR':
        team = "LA"
    stats_dict[team].update({
                             'solo tackles': row[2].text.strip(),
                             'assisted tackles': row[3].text.strip(),
                             'combined_tackles': row[4].text.strip(),
                             'ints': row[5].text.strip(),
                             'int_yards': row[6].text.strip(),
                             'int_td': row[7].text.strip(),
                             'fumble_forced': row[8].text.strip(),
                             'fumble_recovered': row[9].text.strip(),
                             'fumble_td': row[10].text.strip(),
                             'sacks': row[11].text.strip(),
                             'passed_defensed': row[12].text.strip(),


    })

print (stats_dict['MIA'])
print (datetime.now() - start)
exit()





game= Games.objects.get(week__current=True, playoff_picks=True)
web = scrape_cbs_playoff.ScrapeCBS()
#d = web.get_data()
#print (d)




#p_stats = PlayoffStats()
#game = Games.objects.get(week__current=True, playoff_picks=True)
#stats = PlayoffStats.objects.get(game=game)
#print (stats.data)
for k, v in stats.data.items():
    print ('=====================')
    print (k, v)

exit()
#p_stats.game = game
#p_stats.data = d
#p_stats.save()
#exit()
#r = HttpRequest.method="GET"

#started = views.PlayoffGameStarted().get(r)
#scores = views.UpdatePlayoffScores().get(r)
#print ('started', scores_._container)
#print (datetime.now() - start)

exit()
stats = PlayoffStats.objects.get(game=game)
data = stats.data
#print (data['home']['team_stats'])
qb = data['away']['passing']
print (qb)

for k, v in qb.items():
    comp = int(v['cp/att'].split('/')[0])
    att = int(v['cp/att'].split('/')[1])
    
    rating_a = ((comp/att) - .3) * 5
    rating_b = ((int(v['yards'])/att) -3) *.25
    rating_c = (int(v['tds'])/att) *20
    rating_d = 2.375 - ((int(v['ints'])/att) *25)

    multiplier = 10 ** 1
    
    final_rating = ceil((((rating_a + rating_b + rating_c + rating_d) / 6) * 100) * multiplier) / multiplier

    print (k, final_rating)




#winner = max(home_score, away_score)

#return max(float(f['rating']) for f in self.stats.data['away']['passing'].values())
#print (winner)
#print (stats.total_passing_yards())

print (datetime.now() - start)


exit()

#print (stats.all_team_results())

data = json.loads(stats.data)
print (type(data))

player_data = data.get(player.name.username)
print (type(player_data))
player_d = [{k: {'wrong': d['wrong'], 'right': d['right'], 'win_percent': "{:.0%}".format(round(int(d['right'])/(int(d['right'])+int(d['wrong'])),2))}} for k, d in player_data.items()]

print (player_d)

#perf.player_results(player)
#player_data = [{'team': d['team'],  'wrong': d['wrong'], 'right': d['right']} for p, d in json.loads(stats.data)[player.name.username]]
print ('dur: ', datetime.now()- start)

exit()

for p in league.player:
    print (p)

exit()


def parse_sheet(sheet, players=None):
    
    if players == None:
        players = 26

    row_len = players + 2
    sheet_dict = {}
    player_list = []
    sheet_list = []
    row = 0

    doc = docx2txt.process(sheet)
    l = doc.split('\n')
    ps = ([x for x in l if x not in ['', '  ']])
    sheet_dict['week'] = ps[0]
    print (ps)
    #build player name keys in dict
    for s in ps[1:players+1]:
        try:
            if s not in  ['', '  ']:
                sheet_dict['picks'].update({fix_name(s): {}})
                sheet_dict['totals'].update({fix_name(s): {}})
                player_list.append(fix_name(s))
        except KeyError:
            sheet_dict['picks'] = {fix_name(s): {}}
            sheet_dict['totals'] = {fix_name(s): {}}
            player_list.append(fix_name(s))
    
    #add picks to dict
    player_i = -1
    for i, pick in enumerate(ps[players+1:]):
        #print ('i: ', i, 'row: ', row, 'pick: ', pick, 'player_i: ', player_i)
        #print (pick, ps[i-1]) 
        if i == len(ps) - ((players*2)+1) or row > 15:  # break after scanning picks, skipping totals in this loop
            print ('break')
            break
        if i == 0:
            player_i = 0
        elif player_i == 26:  #last col in row, setting for next row
            row +=1
            player_i = 27
        elif player_i == 27:  #first col in new row, skipping pick number
            player_i = 0
        else:
            if pick == ps[(players+1 +i)-1]:
                print ('A', pick, ps[(players+1 +i)-1])
                try: #detecting no pick rows on bye weeks
                  int(pick)
                  int(ps[(players+1 +i)-1])
                  print ('break 1')
                  continue
                except Exception as e:
                  print ('passing', e)
            sheet_dict['picks'][player_list[player_i]].update({16-(row): pick})
            player_i = (i - (row*row_len)) 
                
    #add season totals to dict
    for i, total in enumerate(ps[-players:]):
        sheet_dict['totals'][player_list[i]]=total
            
    
    print (sheet_dict)
    
        
    
    
    


def fix_name(name):
    fix_name = ''
    for i, c in enumerate(name):
        if c != ' ':
            fix_name += c
        elif name[i-1] != ' ':
            fix_name += c

    return fix_name.rstrip()



# #parse_sheet('20-21 FOOTBALL FOOLS-week14.docx')
# print ('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
# parse_sheet('THANKSGIVING.docx')
# print ('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
# parse_sheet('week14-sheet.docx')
# print ('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
# parse_sheet('20-21 FOOTBALL FOOLS-wek13.docx')
# print ('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')