import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")
import django
django.setup()
from golf_app.models import Tournament, TotalScore, ScoreDetails, Picks, PickMethod, BonusDetails, \
        Season, Golfer, Group, Field, ScoreDict, AuctionPick, AccessLog, StatLinks, CountryPicks, \
         FedExSeason, FedExField, FedExPicks
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from golf_app import populateField, calc_leaderboard, manual_score, bonus_details, espn_api, \
                     round_by_round, scrape_espn, utils, golf_serializers, espn_schedule, \
                     scrape_scores_picks, espn_ryder_cup, withdraw, fedex_email
from django.db.models import Count, Sum
from unidecode import unidecode as decode
import json
from requests import get
from collections import OrderedDict
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from golf_app import views
from django.core import serializers
from django.db.models import  Q, Min, Max
import urllib
from pprint import pprint
import csv
from rest_framework.request import Request
from django.http import HttpRequest

start = datetime.now()
t = Tournament.objects.get(current=True)
#sd = ScoreDict.objects.get(tournament=t)

mail = fedex_email.send_summary_email()
exit()


r = HttpRequest()
s = views.FedExDetailAPI()

print (json.loads(s.get(r, 1).content))

exit()

#context = req.get_context_data()
#print (context)

exit()


t = Tournament.objects.get(current=True)
t = Tournament.objects.get(pga_tournament_num='010', season__season=2022)
print (t)
for u in t.season.get_users('obj'):
    picks = {}
    for p in FedExPicks.objects.filter(pick__season__season__current=True, user=u):
        picks.update({k:v for k,v in t.fedex_data.items() if k == p.pick.golfer.golfer_name})
    into_top30 = {k:v for k,v in picks.items() if int(v.get('rank')) < 31 and int(v.get('last_week_rank')) > 30}
    out_top30 = {k:v for k,v in picks.items() if int(v.get('rank')) > 30 and int(v.get('last_week_rank')) < 31}

print (datetime.now() - start)
exit()


# fix MP results data
t_list = [Tournament.objects.get(pga_tournament_num='470', season__season=2022), Tournament.objects.get(pga_tournament_num='470', season__season=2021)]


mp_golfers = list(Field.objects.filter(tournament__in=t_list).values_list('golfer__pk', flat=True))
g_list = list(set(mp_golfers))

print (len(g_list), g_list)

for g in Golfer.objects.filter(pk__in=g_list):
    g.get_season_results(rerun=True)

print (datetime.now() - start)
exit()
#end fix MP results data

for f in Field.objects.filter(tournament=t):
    #print (f.golfer)
    f.golfer.get_season_results(rerun=True)
    #print (f, f.get_mp_result(t))
#for f in Field.objects.filter(tournament=t):
#    print (f.golfer.results.get('153'))
 
t1 = Tournament.objects.get(pga_tournament_num='470', season__season=2021)

for f in Field.objects.filter(tournament=t1):
    f.golfer.get_season_results(rerun=True)

for g in Golfer.objects.all():
    if g.results.get('153').get('rank') == None:
        g.results.get('153').update({'rank': 'n/a',
                                    'season': g.results.get('153').get('season'),
                                    't_name': g.results.get('153').get('t_name')})

print (datetime.now() - start)
exit()

for f in Field.objects.filter(tournament=t, playerName__in=["Bryson Dechambeau","Abraham Ancer", "Rory Mcilroy"]):
    #print (f, f.prior_year_finish(), f.recent_results(), type(f.recent_results()))
    print (f, f.golfer.summary_stats(t.season) 
 )
exit()


for g in Golfer.objects.filter(pk__lte=511):
    print (g, g.get_season_results())

exit()

#t = Tournament.objects.get(season__season='2021', pga_tournament_num='470') 

#t = Tournament.objects.get(season__current=True, name="Ryder Cup")

#score_dict = espn_ryder_cup.ESPNData(t=t).field()

#print (score_dict)

d = {}
for u in Season.objects.get(current=True).get_users('obj'):
    #d[u.username] = {}
    picks =  AccessLog.objects.filter(user=u, page__in=['picks', 'new_picks']).values('page').annotate(Sum('views'))
    p_total = picks[0].get('views__sum') + picks[1].get('views__sum')  
    curr_scores = AccessLog.objects.filter(user=u, page__in=['current week scores', 'API current week scores']).values('page').annotate(Sum('views'))
    c_total = curr_scores[0].get('views__sum') + curr_scores[1].get('views__sum')  
    total_scores = AccessLog.objects.filter(user=u, page='total scores').values('page').annotate(Sum('views'))
    print (total_scores[0])
    d[u.username] = {'picks': p_total,
                    'weekly_score': c_total,
                    'total_score': total_scores[0].get('views__sum')}

for k, v in d.items():
    print (k, v)
exit()


for f in FedExField.objects.all().order_by('soy_owgr'):
        print (f.golfer.golfer_name, f.soy_owgr)


with open('fedex_baseline.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for f in FedExField.objects.all().order_by('soy_owgr'):

        csvwriter.writerow([f.golfer.golfer_name, f.soy_owgr])

csvfile.close()


exit()



t = Tournament.objects.get(current=True) 
print (t)
sd = ScoreDict.objects.get(tournament=t)
data = sd.espn_api_data

espn = espn_api.ESPNData(t=t, data=data)
print (espn.tournament_complete())

print (datetime.now() - start)
exit()

picks = list(Picks.objects.filter(playerName__tournament=t).order_by('playerName__golfer__espn_number').values_list('playerName__golfer__espn_number', flat=True).distinct())
#print ('picks: ', picks, len(picks))
#print ('picks cnt: ', Picks.objects.filter(playerName__golfer__espn_number__in=picks, playerName__tournament=t).values('playerName__golfer__espn_number').distinct().count())

# c = competition, s= session, m = match, 
c  = espn.event_data.get('competitions')
print (type(c))
print (len(c))
d = {'Wednesday Group Play': {'winners': [], 'losers': [], 'draws': []},
    'Thursday Group Play': {'winners': [], 'losers': [], 'draws': []},
    'Friday Group Play': {'winners': [], 'losers': [], 'draws': []},
    }

for s in c:
    for m in s:
        print (m.get('description'))
        #print (m.get('score').get('draw'))
        if m.get('competitors')[0].get('status').get('type').get('id') == '2' and m.get('competitors')[0].get('score').get('draw'):
            d.get(m.get('description')).get('draws').append(m.get('competitors')[0].get('athlete').get('id'))
            d.get(m.get('description')).get('draws').append(m.get('competitors')[1].get('athlete').get('id'))
            #print (m.get('competitors')[0].get('athlete').get('displayName'), 'halved')
            #print (m.get('competitors')[1].get('athlete').get('displayName'), 'halved')
        elif m.get('competitors')[0].get('score').get('winner'):
            d.get(m.get('description')).get('winners').append(m.get('competitors')[0].get('athlete').get('id'))
            d.get(m.get('description')).get('losers').append(m.get('competitors')[1].get('athlete').get('id'))
        elif m.get('competitors')[1].get('score').get('winner'):
            d.get(m.get('description')).get('winners').append(m.get('competitors')[1].get('athlete').get('id'))
            d.get(m.get('description')).get('losers').append(m.get('competitors')[0].get('athlete').get('id'))


print (d)    
print (datetime.now() - start)
exit()        

for pick in Picks.objects.filter(playerName__golfer__espn_number__in=picks, playerName__tournament=t).values('playerName__golfer__espn_number').distinct():
    p = Picks.objects.filter(playerName__golfer__espn_number=pick.get('playerName__golfer__espn_number'), playerName__tournament=t).first()
        # for m in o:
        #     #print (len(m), type(m))
        #     for competitors in m.get('competitors'):
        #         #print (competitors.get('id'), competitors.get('score'))
        #         if competitors.get('athlete').get('id') == p.playerName.golfer.espn_number:
        #             if m.get('competitors')[0].get('status').get('type').get('id') == 2 and m.get('score').get('draw') == 'true':
        #                 print (m.get('competitors')[0].get('athlete').get('displayName'), 'halved')
        #                 print (m.get('competitors')[1].get('athlete').get('displayName'), 'halved')
        #             else:         
        #                 print (m.get('competitors')[0].get('athlete').get('displayName'), m.get('competitors')[0].get('score').get('winner'))
        #                 print (m.get('competitors')[1].get('athlete').get('displayName'), m.get('competitors')[1].get('score').get('winner'))




print (datetime.now() - start)

exit()



print ('complete: ', espn.tournament_complete())

#pprint(rounds, indent=2)
exit()




espn = espn_api.ESPNData(t=t)
print (len(espn.field_data))
exit()

t = Tournament.objects.get(current=True)
sd = ScoreDict.objects.get(tournament=t)
espn = espn_api.ESPNData(force_refresh=True)
print (espn.post_cut_wd_score())

#print (data.get('status').get('type').get('id'))
#print (data.get('linescores').get('period'))
#print (data.get('status').get('type').get('shortDetail'))
#print (data)
#ls = data.get('status')
#print (ls)
#print (espn.get_thru('1651'))
#for f in Field.objects.filter(tournament=t).exclude(withdrawn=True):
    #print (f, f.calc_score(api_data=espn), [x for x in espn.golfer_data(f.golfer.espn_number).get('linescores') if x.get('period') == 3])
#    print (f, f.calc_score(api_data=espn), f.post_cut_wd(sd=None, api_data=espn))

print ('dur: ', datetime.now() - start)
#min_key = 310
#max_key = 510

#print (Golfer.objects.filter(pk__gte=min_key, pk__lte=max_key))

exit()
first_g = Golfer.objects.first()
print (first_g, first_g.pk)

last_g = Golfer.objects.last()
print (last_g, last_g.pk)


print (datetime.now() - start)

exit()


# print ('espn all: ',  type(espn.all_data))
# print ('espn event: ',  type(espn.event_data))
# print ('espn field: ',  type(espn.field_data))
# print ('espn competition: ',  type(espn.competition_data))

pre_data = datetime.now()
#headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
#url =  "https://site.web.api.espn.com/apis/site/v2/sports/golf/leaderboard?league=pga"

#all_data = get(url, headers=headers).json()

sd = ScoreDict.objects.get(tournament=tournament)
all_data = sd.espn_api_data
#print ('post refresh data dur: ', datetime.now() - pre_data)
field_start = datetime.now()
#print ('all data: ', len(all_data), type(all_data), len(all_data.get('events')))
#event_data = [v for k,v in all_data.items() if k == 'events' and [v for x in v if x.get('id') == tournament.espn_t_num]]         # self.event_data = {}
event_data = [v for v in all_data.get('events') if v.get('id') == tournament.espn_t_num][0]         # self.event_data = {}
#print ('event data: ', len(event_data), type(event_data))
#comp_data = [c.get('competitions') for c in event_data]
comp_data = event_data.get('competitions')[0]
#print ('comp data: ', len(comp_data), type(comp_data))
field_data = comp_data.get('competitors')
print ('field ', len(field_data), type(field_data))

 
print ('field dur: ', datetime.now() - pre_data)
espn = espn_api.ESPNData()
exit()
        # self.competition_data = {}
        # self.field_data = {}
        # event_found = False
        # for event in self.all_data.get('events'):
        #     print (event.get('id'), self.t.espn_t_num)
        #     if event.get('id') == self.t.espn_t_num:
        #         event_found = True
        #         #pre_name_check = datetime.now()
        #         #if utils.check_t_names(event.get('name'), self.t) or self.t.ignore_name_mismatch: 
        #         self.event_data = event
        #         sd, created = ScoreDict.objects.get_or_create(tournament=self.t)
        #         sd.espn_api_data = self.all_data
        #         sd.save()
        #         if self.t.pga_tournament_num not in ['468', '999', '470']:
        #             for c in self.event_data.get('competitions'):
        #                 self.competition_data = c
        #                 self.field_data = c.get('competitors')
        #         #else:
        #         #    print ('tournament mismatch: espn name: ', event.get('name'), 'DB name: ', self.t.name)
        #         #break 
        # if not event_found:
        #     print ('ESPN API didnt find event, PGA T num: ', self.t.pga_tournament_num)







espn = espn_api.ESPNData()

started_golfers = []
lock_groups = []

if not espn.started() or tournament.late_picks:
    t_started = False
else:
    t_started = espn.started()
    started_golfers = espn.started_golfers_list()
    for g in Group.objects.filter(tournament=tournament):
        if g.lock_group(espn, u):
            lock_groups.append(g.number) 

p_s = datetime.now()
picks = Picks.objects.filter(playerName__tournament=tournament, user=u).values_list('playerName__pk', flat=True)
print ('p dur: ', datetime.now() - p_s)
f_s = datetime.now()
field = serializers.serialize('json', Field.objects.filter(tournament=tournament))
print ('f dur: ', datetime.now() - f_s)
e_s = datetime.now()
#espn_nums = Field.objects.filter(tournament=tournament).values_list('golfer__espn_number', flat=True)
espn_nums = Field.objects.filter(tournament=tournament).values_list('golfer__pk', flat=True)
print ('e dur: ', datetime.now() - e_s)
g_s = datetime.now()
#golfers = serializers.serialize('json', Golfer.objects.filter(espn_number__in=espn_nums))        
golfers = serializers.serialize('json', Golfer.objects.filter(pk__in=espn_nums))        
print ('g dur: ', datetime.now() - g_s)
print ('duration: ', datetime.now() - start)
exit()

t = Tournament.objects.get(current=True)

fed = populateField.get_fedex_data(t)
print (fed.get('Hideki Matsuyama'))

exit()
sd = ScoreDict.objects.get(tournament=t)
sd.update_sd_data()

#print (sd.data.get('Brian Harman'))
mdf = [v.get('pga_num') for k,v in sd.data.items() if k != 'info' and v.get('rank') in ['T65', '-']] 


for g in Golfer.objects.filter(espn_number__in=mdf):
    g.get_season_results(rerun=True)

for x in Golfer.objects.filter(espn_number__in=mdf):
    print (x, x.results.get('206'))

exit()

espn = espn_api.ESPNData()

context = {'espn_data': espn, 'user': User.objects.get(pk=1)}
data= golf_serializers.NewFieldSerializer(Field.objects.filter(tournament=t, group__number=9), context=context, many=True).data

print ('dur',  datetime.now() - start)

exit()



for g in Golfer.objects.filter(golfer_name__in=['Jon Rahm', 'Justin Thomas']):
    g.get_season_results()

print ('duration: ', datetime.now() - start)
exit()

t = Tournament.objects.filter(season__current=True).exclude(current=True).last()
sd = ScoreDict.objects.get(tournament=t)
print (sd.data.get('Brian Harman'))
mdf_golfers = ([v.get('pga_num') for k,v in sd.data.items() if k != 'info' and v.get('rank') in ['-']])

sd.update_sd_data()

for g in Golfer.objects.filter(espn_number__in=mdf_golfers):
    print (g)
    start_loop = datetime.now()
    g.get_season_results(rerun=True)
    print ('dur: ', datetime.now() - start_loop)    


for x in Golfer.objects.filter(espn_number__in=mdf_golfers):
    print (x, len(x.results), x.results.get('206'))

exit()

res = g.get_season_results()
print (res)
exit()
espn = espn_api.ESPNData()

print (espn.started())

exit()

for f in Field.objects.filter(tournament=t, group__number=3):
    e_num = f.golfer.espn_number
    print (f, espn.get_rank(e_num))


exit()
for p in Picks.objects.filter(playerName__tournament=t, user__pk=1):
    print (p.playerName.calc_score(api_data=espn))

exit()



pre_fedex = datetime.now()
fed_ex = populateField.get_fedex_data(tournament)
print ('post fedex: ', datetime.now() - pre_fedex)

pre_indiv = datetime.now()
individual_stats = populateField.get_individual_stats()
print ('post individual: ', datetime.now() - pre_indiv)

pre_recent = datetime.now()
for f in Field.objects.filter(tournament=tournament):
    
    if tournament.pga_tournament_num not in ['470', '018']:
        f.handi = f.handicap()
    else:
        f.handi = 0
    
    f.prior_year = f.prior_year_finish()
    recent = OrderedDict(sorted(f.recent_results().items(), reverse=True))
    f.recent = recent
    f.season_stats = f.golfer.summary_stats(tournament.season) 

    #print (fed_ex)
    if fed_ex.get(f.playerName):
        f.season_stats.update({'fed_ex_points': fed_ex.get(f.playerName).get('points'),
                                'fed_ex_rank': fed_ex.get(f.playerName).get('rank')})
    else:
        f.season_stats.update({'fed_ex_points': 'n/a',
                                'fed_ex_rank': 'n/a'})

    if individual_stats.get(f.playerName):
        player_s = individual_stats.get(f.playerName)
        for k, v in player_s.items():
            if k != 'pga_num':
                f.season_stats.update({k: v})
    
    f.save()

print ('post recent : ', datetime.now() - pre_recent )    
pre_season_results = datetime.now()

for g in Golfer.objects.all():
    g.results = g.get_season_results()
    g.save()

print ('post season results: ', datetime.now() - pre_season_results)

exit()

t = Tournament.objects.get(current=True)
owgr = populateField.get_worldrank()
field = populateField.get_field(t, owgr)

print (field)

exit()

t = Tournament.objects.get(pk=198)
print (t)

sd = ScoreDict.objects.get(tournament=t)
print (json.loads(sd.pick_data).get('display_data').keys())
exit()


if not sd.validate_sd():
    sd.update_sd_data()

data =json.loads(sd.pick_data)
optimal = json.loads(data.get('display_data').get('optimal'))
d = {}

for k, v in optimal.items():
    d[str(k)] = {'golfers': [],
                'golfer_espn_nums': [],
                'cuts': v.get('cuts'),
                'total_golfers': v.get('total_golfers')}
    print (v.get('golfer'))
    for num, name in v.get('golfer').items():
        d.get(str(k)).get('golfer_espn_nums').append(num)
        d.get(str(k)).get('golfers').append(name)

espn = espn_api.ESPNData(t=t)
print (espn.group_stats() == d)

print (espn.group_stats())
print('-------------------------------')
print (d)

exit()

season = Season.objects.get(current=True)

start_ts = datetime.now()
d = {}

for p in FedExPicks.objects.filter(pick__season__season=season):
    if d.get(p.user.username):
        d.get(p.user.username).update({p.pick.golfer.espn_number: {'golfer_name': p.pick.golfer.golfer_name,
                                                            'score': p.score}})
    else:
        d[p.user.username] = {p.pick.golfer.espn_number: {'golfer_name': p.pick.golfer.golfer_name,
                                                            'score': p.score}}
print ('ts duration: ', datetime.now() - start_ts)
print (d)
exit()

total_scores = json.loads(season.get_total_points())
for user in total_scores.keys():
    user_start = datetime.now()
    data = golf_serializers.FedExPicksSerializer(FedExPicks.objects.filter(pick__season__season=season, user=User.objects.get(username=user)), many=True).data
    print ('user end ', user, '  ', datetime.now() - user_start, len(data))


exit()


for t in Tournament.objects.filter(pk=198):
    print (t)
    if not t.special_field():
        print (t)
        sd = ScoreDict.objects.get(tournament=t)
        if not sd.validate_sd():
            print (sd.update_sd_data())
exit()


with open('Sony_mid_r2.json') as json_file:
    data = json.load(json_file)

espn = espn_api.ESPNData(t=t, data=data)
start = datetime.now()
#stats = espn.group_stats()
print (espn.tournament_complete(), espn.cut_num())

exit()
print ('api dur: ', datetime.now() - start)


optimal_picks = {}
sd = ScoreDict.objects.get(tournament=t)
score_dict = sd.data
scores = manual_score.Score(score_dict, t, 'json')
start_old = datetime.now()
for g in Group.objects.filter(tournament=t):
    opt = scores.optimal_picks(g.number)
    optimal_picks[str(g.number)] = {
                                    'golfer': opt[0],
                                    'rank': opt[1],
                                    'cuts': opt[2],
                                    'total_golfers': g.playerCnt
    } 

print ('scrape dur: ', datetime.now() - start_old)

exit()

espn = espn_api.ESPNData()
#print (espn.field())
print (espn.leaders())
print (espn.leader_score())
print (espn.cut_line())
exit()


espn = espn_api.ESPNData().all_data
with open('Sony_mid_r4.json', 'w') as outfile:
    json.dump(espn, outfile)

with open('Sony_mid_r4.json') as json_file:
    data = json.load(json_file)


espn_1 = espn_api.ESPNData(data=data)
print (espn_1.field())

exit()


t= Tournament.objects.get(pk=199, season__current=True)
owgr = populateField.get_worldrank()
field = populateField.get_field(t, owgr)
groups = populateField.configure_groups(field, t)

for g in Group.objects.filter(tournament=t):
    print (g.number, g.playerCnt)
    print ('field cnt: ', Field.objects.filter(tournament=t, group=g).count())
exit()



espn_data = espn_api.ESPNData()
group_stats = espn_data.group_stats()
#print (group_stats)
start = datetime.now()
big = [v.get('golfer_espn_nums') for k,v in group_stats.items()]

print ([num for sublist in big for num in sublist])
print (datetime.now() - start)
# context = {'espn_data': espn_data, 'user': User.objects.get(pk=1)}
# for g in Group.objects.filter(tournament=t):
#     data= golf_serializers.NewFieldSerializer(Field.objects.filter(tournament=t, group__number=g.number), context=context, many=True).data

# print (datetime.now() - start)




exit()


t = Tournament.objects.get(current=True)
start = datetime.now()
espn = espn_api.ESPNData()
group_stats = espn.group_stats()
print (group_stats)

for u in t.season.get_users('obj'):
    #print (u)
    u_score = 0
    for pick in Picks.objects.filter(playerName__tournament=t, user=u):
        score = pick.playerName.calc_score(api_data=espn)
        #print (pick, score)
        u_score += score
        bd_start = datetime.now()
        bd = bonus_details.BonusDtl(espn_api=espn, espn_scrape_data=None, tournament=t, inquiry=True)
        big = bd.best_in_group(group_stats, pick)
        if big:
           print ('big', pick)
        print ('bd dur: ', pick, datetime.now() - bd_start)


    print (u, u_score)

print ('dur: ', datetime.now() - start)
exit()

# for f in Field.objects.filter(tournament=t, playerName="Sam Burns"):
#     f.withdrawn=True
#     f.save()
#     print (f, f.recent)

exit()

t = Tournament.objects.get(name="The RSM Classic", season__current=True)
#print (calc_leaderboard.LeaderBoard(t, 4).get_leaderboard().get('Louis Oosthuizen'))
#exit()
d = round_by_round.RoundData(t).update_data()

r4 = d.get('round_4')
db = d.get('db_scores')
bd = d.get('bonuses')
print (bd)
for u, score in db.items():
    if bd.get(u):
        print (u, db.get(u), r4.get('scores').get(u) - bd.get(u))
    else:
        print (u, db.get(u), r4.get('scores').get(u))

exit()



d = {}
leaders_d = {}
optimal_picks = {}
for u in Season.objects.get(current=True).get_users('obj'):
    leaders_d[u.username] = {'lead': 0}
start = datetime.now()

#for t in Tournament.objects.filter(season__current=True):
for t in Tournament.objects.filter(current=True):
    if not t.special_field():
        print (t)
        d[t.name] = {}
        sd = ScoreDict.objects.get(tournament=t)
        for r in range(1,5):
            round_start = datetime.now()
            print ('ROUND ', r)
            d.get(t.name).update({'round_' + str(r):{'scores': {}, 'leaders': {}}})
            lb = calc_leaderboard.LeaderBoard(t, r).get_leaderboard()
            if int(t.season.season) > 2019:
                optimal_start = datetime.now()

                for g in Group.objects.filter(tournament=t):
                    #optimal = g.optimal_pick(sd.data)
                    optimal = g.optimal_pick(lb)
                    #print (lb)
                    optimal_picks[str(g.number)] = {}
                    for espn_num, golfer in optimal.items():
                        optimal_picks.get(str(g.number)).update({espn_num: golfer}) 
                d.get(t.name).get('round_' + str(r)).update({'optimal_picks': optimal_picks})
               
                print ('optimal duration: ', datetime.now() - optimal_start)
                
            #for u in t.season.get_users('obj'):
            pick_loop_start = datetime.now()
            for pick in Picks.objects.filter(playerName__tournament=t):

                if d.get(t.name).get('round_' + str(r)).get('scores').get(pick.user.username):
                    d.get(t.name).get('round_' + str(r)).get('scores').update({pick.user.username: d.get(t.name).get('round_' + str(r)).get('scores').get(pick.user.username) + \
                    [v.get('rank') - pick.playerName.handi for v in lb.values() if v.get('espn_num') == pick.playerName.golfer.espn_number][0]})
                else:
                    d[t.name]['round_' + str(r)]['scores'].update({pick.user.username: [v.get('rank') - pick.playerName.handi for v in lb.values() if v.get('espn_num') == pick.playerName.golfer.espn_number][0]})
                
                bd = bonus_details.BonusDtl(espn_scrape_data=sd.data, tournament=t, inquiry=True)
                if bd.best_in_group(d.get(t.name).get('round_' + str(r)).get('optimal_picks').get(str(pick.playerName.group.number)) , pick):
                    d.get(t.name).get('round_' + str(r)).get('scores').update({pick.user.username: d.get(t.name).get('round_' + str(r)).get('scores').get(pick.user.username) -10})
            print ('pick loop dur: ', datetime.now() - pick_loop_start)
            low_score = min(d.get(t.name).get('round_' + str(r)).get('scores').items(), key=lambda v: v[1])[1]
            
            leaders = {k:v for k,v in d.get(t.name).get('round_' + str(r)).get('scores').items() if v == low_score}

            for l, s in leaders.items():
                leaders_d[l].update({'lead': leaders_d[l].get('lead') + 1})        

            print ('round dur: ', datetime.now() - round_start)
    for k,v in d.items():
        for key, val in v.items():
            print (key, val)
    print ('--------------------------------------')
    print (leaders_d)

print ('dur: ', datetime.now() - start)

exit()

#r1_leaderboard = {k:v.get('r1') for k,v in sd.data.items() if k != 'info'}
#r2_leaderboard = {k:score(v.get('r1')) + int(v.get('r2')) for k,v in sd.data.items() if k != 'info'}
#print (r2_leaderboard)

print ('befor loop', datetime.now() - start)

def score(pick, score_dict, t_round):
    if t_round == 1:
        return [int(v.get('r1')) for k,v in sd.data.items() if v.get('pga_num') == pick.playerName.golfer.espn_number][0]
    elif t_round == 2:
        return [int(v.get('r2')) for k,v in sd.data.items() if v.get('pga_num') == pick.playerName.golfer.espn_number][0]
    elif t_round == 3:
        return [int(v.get('r3')) for k,v in sd.data.items() if v.get('pga_num') == pick.playerName.golfer.espn_number][0]
    elif t_round == 4:
        return [int(v.get('r4')) for k,v in sd.data.items() if v.get('pga_num') == pick.playerName.golfer.espn_number][0]

def leaderboard(score_dict, r):
    for g in score_dict:
        p = Picks.objects.get()
        s = score()

t = Tournament.objects.get(current=True)
sd = ScoreDict.objects.get(tournament=t)

#for u in t.season.get_users('obj').exclude(username='Hiro'):
for u in User.objects.filter(pk=1):
    r1_score = 0
    r2_score = 0
    r3_score = 0
    r4_score = 0
    for pick in Picks.objects.filter(user=u, playerName__tournament=t):
        pick_start = datetime.now()
        #r1_scores = {k:v.get('r1') for k,v in sd.data.items() if v.get('pga_num') == pick.playerName.golfer.espn_number}
        #r1_scores = [v.get('r1') for k,v in sd.data.items() if v.get('pga_num') == pick.playerName.golfer.espn_number][0]
        r1_score = score(pick, sd, 1)
        r2_score = score(pick, sd, 2) + r1_score
        r3_score = score(pick, sd, 3) + r2_score
        r4_score = score(pick, sd, 4) + r3_score

        print (r1_score, r2_score, r3_score, r4_score)
        print ('pick loop duration: ', datetime.now() - pick_start)

print ('duration: ', datetime.now() - start)


exit()

print ('pre update Null : ', Field.objects.filter(golfer__isnull=True).count())

start = datetime.now()
c = 0
d = {}
for g in Golfer.objects.all(): 
    d[g.golfer_name] = g.golfer_pga_num

for f in Field.objects.filter(golfer__isnull=True):
#t = Tournament.objects.first()
#for f in Field.objects.filter(tournament=t):
    if f.golfer:
        continue
    elif f.playerID:
        try:
            g = Golfer.objects.get(golfer_pga_num=f.playerID)
            f.golfer = g
            f.save()
        except Exception as e:
            g, created = Golfer.objects.get_or_create(golfer_name = f.playerName)
            g.golfer_pga_num = f.playerID
            g.save()
            f.golfer = g
            f.save()
            #print ('PLAYER ID but NO GOLFER  ', f.tournament, f)
    else:
        #print (f, 'in first else')
        # not checking if linked, need to check that
        #print (f.playerName)
        if Golfer.objects.filter(golfer_name=f.playerName).exists():
            g = Golfer.objects.get(golfer_name=f.playerName)
            #print (('in if', f, g))
        elif Golfer.objects.filter(golfer_name=f.playerName.title()).exists():
            g = Golfer.objects.get(golfer_name=f.playerName.title())
            print ('in elif', f, g)
        else:
            found = utils.fix_name(f.playerName.title().rstrip(' '), d)
            if not found[0]:
                g, created = Golfer.objects.get_or_create(golfer_name=f.playerName)
                g.save()
                #print (f.tournament.season, f.tournament, f.playerName, f.playerName.title(), Picks.objects.filter(playerName=f))  
                c += 1
                #print ( 'in not found', f, found)
            else:
                print ( 'in else 2', f.tournament, f.tournament.season, f, found)
                g = Golfer.objects.get(golfer_pga_num=found[1])
        f.golfer = g
        f.save()

#print (c)
print ('orphan field count: ', Field.objects.filter(golfer__isnull=True).count())
total_score = 0
for t in Tournament.objects.filter(season__current=True):
     avg_score = TotalScore.objects.filter(tournament=t).aggregate(Avg('score'))
     print (t, avg_score)
     #total_score += avg_score.get('score__avg')
     ts, created = TotalScore.objects.get_or_create(user=User.objects.get(username="Hiro"), tournament=t)
     ts.score = avg_score.get('score__avg')
     ts.save()

# for p in FedExPicks.objects.filter(user__username='john'):
#     print (p.pick.golfer)
#     fedex = FedExPicks()
#     fedex.user = User.objects.get(username="Hiro")
#     fedex.pick = p.pick 
#     fedex.save()
#print (total_score)
exit()


d = {}
s = Season.objects.get(current=True)
for u in s.get_users('obj'):
    winner_picks = ScoreDetails.objects.filter(user=u, score=1).count()
    d[u.username] = {'played': 0,
                    'total_score': 0,
                    'winner_picks': winner_picks}
    

for s in Season.objects.all():
    score = TotalScore.objects.filter(tournament__season=s).aggregate(Sum('score'))
    print (s.season,  round((score.get('score__sum') / Tournament.objects.filter(season=s).count())/len(s.get_users()),0))

for t in Tournament.objects.all().order_by('pk'):
    #print (t.winner())
#for t in Tournament.objects.filter(season__season__gte=2020).order_by('pk'):
    for ts in TotalScore.objects.filter(tournament=t).order_by('score'):
        if ts.score != 999:
            if ts in t.winner():
                ww = 1
            else:
                ww = 0
           
            try:
                d.get(ts.user.username).update({'played': d.get(ts.user.username).get('played') + 1,
                                                'total_score': d.get(ts.user.username).get('total_score') + ts.score,
                                                'weekly_winner': d.get(ts.user.username).get('weekly_winner') + ww,
                 })

            except Exception as e:
                #print (e, ts.tournament, ts.user)
                d.get(ts.user.username).update({'played': 1,
                'total_score':ts.score,
                'weekly_winner': ww,
                 })

for user, data in d.items():
    d.get(user).update({'average': round(d.get(user).get('total_score')/d.get(user).get('played'), 0)})


print (sorted(d.items(), key=lambda v:v[1].get('average')))

print (datetime.now() - start)
exit()




t = Tournament.objects.get(current=True)

espn = espn_api.ESPNData()
print ('round: ', espn.get_round())
print ('complete: ', espn.tournament_complete())
print ('pre cut wd: ', espn.pre_cut_wd())
print ('post cut wd: ', espn.post_cut_wd())
print ('cut num: ', espn.cut_num())
start = datetime.now()
print ('first tee time: ', espn.first_tee_time())
print ('round: ', espn.get_round(), espn.get_round_status())
print ('1: ', datetime.now() - start)
print ('winner: ', espn.winner())
print ('second: ', espn.second_place())
print ('third: ', espn.third_place())

bd = bonus_details.BonusDtl(espn, t)

tri_start = datetime.now()
for u in t.season.get_users('obj'):
    print ('trifecta: ', u, bd.trifecta(u))
print ('tri dur: ', datetime.now() - start)
exit()

f = open('espn_api_r1_complete.json',)

data = json.load(f)

t_1 = Tournament.objects.get(pk=192)
print (t_1)
espn_1 = espn_api.ESPNData(t=t_1, data=data)
print ('round: ', espn_1.get_round())
print ('complete: ', espn_1.tournament_complete())
start_1 = datetime.now()
print ('first tee time: ', espn_1.first_tee_time())
print ('round: ', espn_1.get_round(), espn_1.get_round_status())
print ('2: ',datetime.now() - start_1)
#print (datetime.now() > espn_1.first_tee_time())
exit()

for g in Golfer.objects.filter(golfer_name__in=['Sam Burns', 'Lee Westwood', 'Sung Kang', 'Francesco Molinari']):
    print (g, espn.golfer_data(g.espn_number).get('status'))
    print (len(espn.golfer_data(g.espn_number).get('linescores')))
    for l in espn.golfer_data(g.espn_number).get('linescores'): 
        print (l)
    print ('xxxxxxxxxxxxxxxxxxxxxxxxxxxxx') 
exit()

f = open('espn_api_r1_started.json',)
#print (type(f))
data = json.load(f)

espn = espn_api.ESPNData(t=t, data=data)
print (espn.field()[0].get('linescores'))
#times = [datetime.strptime(x.get('linescores')[0].get('teeTime'), '%Y-%m-%dT%H:%M%fZ') for x in espn.field() if x.get('status').get('period') == 1]
times = [datetime.strptime(x.get('linescores')[0].get('teeTime')[:-1], '%Y-%m-%dT%H:%M') for x in espn.field() if x.get('status').get('period') == 1]
raw_times = [x.get('linescores')[0].get('teeTime') for x in espn.field() if x.get('status').get('period') == 1]
print (times[0])
print (raw_times[0])
#print (espn.field()[0].get('linescores'))
print (min(times), type(min(times)))

#print (datetime.strptime(espn.field()[0].get('linescores')[0].get('teeTime'), '%Y-%m-%dT%H:%M%fZ'))

exit()

if os.environ.get('DEBUG'):
    domain = '127.0.0.1:8000'
else:
    domain = 'jflynn87.pythonanywhere.com'

req = Request('http://' + domain + '/golf_app/espn_api_scores/' + t.pga_tournament_num)

#data = views.EspnApiScores().get(req, t.pga_tournament_num)
#d = json.loads(data.content)
#print (d)

for ts in TotalScore.objects.filter(tournament=t):
    if ts.score == d.get(ts.user.username).get('score'):
        print (ts.user, ' : match')
    else:
        print (ts.user, ': mismatch : ', ts.score, d.get(ts.user.username).get('score'))

# espn = espn_api.ESPNData().all_data

# with open('espn_api_r1_complete.json', 'w') as convert_file:
#      convert_file.write(json.dumps(espn))


exit()

# start = datetime.now()

# t = Tournament.objects.get(current=True)
# api_start = datetime.now()
# espn = espn_api.ESPNData()

# #print ('api dur: ', datetime.now() - api_start)

# start_big = datetime.now()

# big = espn.group_stats()

# print ('big dur ', datetime.now() - start_big)

# start_calc_score  = datetime.now()

# d = {}
# for u in t.season.get_users('obj'):
#     d[u.username] = {'score': 0}

# for golfer in Picks.objects.filter(playerName__tournament=t).values('playerName__golfer__espn_number').distinct():
#     pick = Picks.objects.filter(playerName__tournament=t, playerName__golfer__espn_number=golfer.get('playerName__golfer__espn_number')).first()
#     if espn.golfer_data(pick.playerName.golfer.espn_number):
#         if espn.golfer_data(pick.playerName.golfer.espn_number).get('status').get('type').get('id') == "3":
#             #print ('cut logic', pick.playerName)
#             score = (int(espn.cut_num()) + 1) - int(pick.playerName.handi) + espn.cut_penalty(pick) 
#         else: 
#             score = int(espn.get_rank(pick.playerName.golfer.espn_number)) - int(pick.playerName.handi)
#     else:
#         print ('WD? not found in espn: ', pick.playerName, pick.playerName.golfer.espn_number) 
#         score = (int(espn.cut_num()) + 1) - int(pick.playerName.handi) + espn.cut_penalty(pick)

#     bd_start = datetime.now()
#     bd = bonus_details.BonusDtl(espn, t)
#     bd_big = bd.best_in_group(big, pick)
#     #if big.get(pick.playerName.golfer.espn_number):
#     if bd_big:
#         score -= 10 
#     if bd.winner(pick):
#         score -= bd.winner_points(pick)

#         #print ('db class dur: ', pick, datetime.now() - bd_start)
#     for p in Picks.objects.filter(playerName__tournament=t, playerName__golfer__espn_number=pick.playerName.golfer.espn_number):
#         d.get(p.user.username).update({'score': d.get(p.user.username).get('score') + score})
    
#     #print (d.get('jcarl62'), score)

# if espn.tournament_complete():
#     print ('a')
#     ww_bd = bonus_details.BonusDtl(espn, t)
#     winner_list = ww_bd.weekly_winner(d)
#     print ('b', winner_list)
#     for winner in winner_list:
#         d.get(winner).update({'score': d.get(winner).get('score') - ww_bd.weekly_winner_points()})

# print (d)
# print ('calc score dur: ', datetime.now() - start_calc_score)
# #print ('cut num ', espn.cut_num())
# print ('total time: ', datetime.now() - start)

# for ts in TotalScore.objects.filter(tournament=t):
#     if ts.score == d.get(ts.user.username).get('score'):
#         print (ts.user, ' : match')
#     else:
#         print (ts.user, ': mismatch : ', ts.score, d.get(ts.user.username).get('score'))

exit()

#for c in espn.event_data.get('competitions'):
#    for k,v in c.items():
#        if k != 'competitors':
#            print (k, v)
#cut_num = espn.cut_num()
print ('round: ', espn.get_round())
print ('state: ', espn.get_round_status())
print ('started ', espn.started())
#print (espn.event_data.get('status'))
#print (espn.event_data.get('competitions')[0].get('status'))
#print (espn.event_data.get('competitions')[0].keys())
print ('cut num', espn.cut_num())
print (datetime.now() - start)
exit()
espn_data = scrape_espn.ScrapeESPN().get_data()
user = User.objects.get(pk=1)
context = {'espn_data': espn_data, 'user': user}
data= golf_serializers.NewFieldSerializer(Field.objects.filter(tournament=t, group__number=1), context=context, many=True).data

print (data)

exit()
#for k, v in espn.field().items():
#    print (k, v)
score = ryder_cup_scores.Score(espn.field()).update_scores()
total_scores = ryder_cup_scores.Score(espn.field()).total_scores()

exit()
for session, matches in espn.field().items():
    print (session)
    if session != 'overall':
        for m_id, m_data in matches.items():
            for espn_num, info in m_data.items():
                print (m_id, info.get('golfer'), info.get('score'))
                print ('-----')         
print (espn.field().get('overall'))
print (espn.field())
print (datetime.now() - start)
exit()

#espn = espn_ryder_cup.ESPNData(espn_t_num='401025269')


for session, matches in espn.field.items():
    print (session, matches)



exit()
sd = ScoreDict.objects.get(tournament=t)
if espn.field() == sd.cbs_data:
    print ("No change in ryder cup score DATA")
else:
    print ('different ryder cup data')
    sd.cbs_data = espn.field()
    sd.save()
 
ryder_cup_scores.Score(espn.score_dict()).update_scores()
exit()
#print (espn.field())
#exit()
headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
score_dict = {}
for match, info in espn.field().items():
    score_dict[match] = {}
    if match != 'overall':
        if info.get('type') != 'singles':
            for t in ['USA', 'EURO']:
                url =  info.get(t).get('golfers_link')
                golfers = get(url, headers=headers).json()
                for entry in golfers.get('entries'):
                    golfer_obj = Golfer.objects.get(espn_number=entry.get('playerId'))
                    score_url = info.get(t).get('score_link')
                    score_data = get(score_url, headers=headers).json()
                    #print (t, info.get('type'), golfer_obj, score_data.get('winner'), score_data.get('value'), score_data.get('holesRemaining'), score_data.get('displayValue'), score_data.get('draw'))
                    score_dict[match].update({t: {'type': info.get('type'),
                                                  'golfer_pk': golfer_obj.pk, 
                                                  'winner': score_data.get('winner'),
                                                  'value': score_data.get('value'),
                                                  'holes_remaining': score_data.get('holesRemaining'),
                                                  'display_value': score_data.get('displayValue'),
                                                  'draw': score_data.get('draw')
                                                  }})
        elif info.get('type') == 'singles':
            for t in ['USA', 'EURO']:
                url =  info.get(t).get('golfers_link')
                golfer = get(url, headers=headers).json()
                #print (golfer)
                golfer_obj = Golfer.objects.get(espn_number=golfer.get('id'))
                score_url = info.get(t).get('score_link')
                score_data = get(score_url, headers=headers).json()
                #print (t, info.get('type'), golfer_obj, score_data.get('winner'), score_data.get('value'), score_data.get('holesRemaining'), score_data.get('displayValue'), score_data.get('draw'))
                score_dict[match].update({t: {'type': info.get('type'),
                            'golfer_pk': golfer_obj.pk, 
                            'winner': score_data.get('winner'),
                            'value': score_data.get('value'),
                            'holes_remaining': score_data.get('holesRemaining'),
                            'display_value': score_data.get('displayValue'),
                            'draw': score_data.get('draw')
                            }})

    
print (score_dict)
print (datetime.now() - start)
exit()
print (espn.get_all_data().keys())
print ('competitions')
print (espn.get_all_data().get('competitions')[0].keys(), len(espn.get_all_data().get('competitions')[0]))

for c in espn.get_all_data().get('competitions'):
    print ('=============================================================')
    print (c)

print ('competitors')
print (espn.get_all_data().get('competitions')[0].get('competitors')[0].keys())
print ("Teams")
print (espn.get_all_data().get('competitions')[0].get('competitors')[0].get('team'))
print (espn.get_all_data().get('competitions')[0].get('competitors')[0].get('score'))

exit()
#f = open('owgr.json',)
#print (type(f))
#owgr = json.load(f)

for golfer in Golfer.objects.filter()[1:5]:
    rank = utils.fix_name(golfer.golfer_name, owgr)
    if int(rank[1][0]) < 30:
        print (golfer, rank[0])
exit()
#owgr = populateField.get_worldrank()
f = open('owgr.json',)
print (type(f))
owgr = json.load(f)
#field = populateField.get_field(t, owgr)


#sorted_intl_team = sorted({k:v for k,v in field.items() if v.get('team') == 'INTL'}, key=lambda item: item[1].get('curr_owgr'))
#sorted_usa_team = sorted({k:v for k,v in field.items() if v.get('team') == 'USA'}, key=lambda item: item[1].get('curr_owgr'))

headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
#url =  "https://site.web.api.espn.com/apis/site/v2/sports/golf/leaderboard?league=pga"
#url = 'http://sports.core.api.espn.com/v2/sports/golf/leagues/pga/events/401025269'
espn = espn_ryder_cup.ESPNData(espn_t_num='401025269').field()

print (espn)

# print ('--------------------------------------------------------')

# for key, match in espn.items():
#     print (key, match)
#     try:
#         print (match.get('id'), match.get('description'))
#     except Exception as e:
#         continue

exit()  
s = Season.objects.get(current=True)
f, created = FedExSeason.objects.get_or_create(season=s, allow_picks=True)
f.prior_season_data = populateField.get_fedex_data()

f.save()

fed = fedexData.FedEx(s).create_field()
#owgr = populateField.get_worldrank()
#top_200 = {k:v for k,v in owgr.items() if int(v[2] <= 201)}





#espn_data = espn_api.ESPNData().get_all_data()
#context = {'espn_data': espn_data, 'user': User.objects.get(pk=1)}
#data= golf_serializers.NewFieldSerializer(Field.objects.filter(tournament=t, group__number=2), context=context, many=True).data
#d = json.loads(data[0])
print (datetime.now() - start)

#f = open('owgr.json',)
#print (type(f))
#owgr = json.load(f)
#field_dict = populateField.get_field(t, owgr)
#print (len(field_dict))
#populateField.configure_groups(field_dict, t)
#for k, v in sorted(field.items(), key=lambda v:v[1].get('soy_owgr')):
#    print (k, v)
#print (len(field))
exit()


t= Tournament.objects.get(current=True)
d = {}
for g in range(1,11):
    print (g)
    group_data = ScoreDetails.objects.filter(pick__playerName__tournament__season=season, pick__playerName__group__number=g).order_by('user').values('user__username').annotate(Sum('score'))
    for gd in group_data:
        #print (gd)
        if d.get(gd.get('user__username')):
            d.get(gd.get('user__username')).update({g: gd.get('score__sum')})
        else:
            d[gd.get('user__username')] = {g: gd.get('score__sum')}
    
    
for k, v in d.items():
    print (k, v)

for f in Field.objects.filter(tournament__current=True).order_by('soy_WGR'):
    print (f, ',', f.soy_WGR, ',', f.season_stats.get('fed_ex_rank'))


owgr = populateField.get_worldrank()
top_30 = {k:v for k,v in owgr.items() if int(v[2] <= 30)}
print (top_30, len(top_30))
fed_ex = populateField.get_fedex_data()

for k, v in top_30.items():
    print (k, ',', v[2], ',', fed_ex.get(k).get('rank'))


exit()
d = {'weak': {},
    'strong': {},
    'major': {}}

e = {}

for sd in ScoreDict.objects.filter(tournament__season__current=True).exclude(tournament__pga_tournament_num__in=['999', '470', '028']):  #018 zurich
    if sd.tournament.last_group_multi_pick():
        winner = [v.get('pga_num') for k,v in sd.data.items() if k != 'info' and v.get('rank') == '1']
        
        f = Field.objects.get(golfer__espn_number=winner[0], tournament=sd.tournament)
        #print (f, f.group.number)
        if d.get(sd.tournament.field_quality()).get(f.group.number):
            c = d.get(sd.tournament.field_quality()).get(f.group.number) + 1
            d.get(sd.tournament.field_quality()).update({f.group.number: c})
            
        else:
            d[sd.tournament.field_quality()][f.group.number] = 1
            
        if f.group.number == 6:
            if ScoreDetails.objects.filter(gross_score=1, pick__playerName__tournament=sd.tournament).exists():
                print ('G6 winner: ', sd.tournament, ScoreDetails.objects.filter(gross_score=1, pick__playerName__tournament=sd.tournament))
        if e.get(f.group.number):
            e.update({f.group.number: e.get(f.group.number) + 1 })
        else:
            e[f.group.number] = 1

        if f.group.number == 6:
            print (f.playerName, f.tournament)

for k, v in d.items():
    print(k, v)
print (e)

s = Season.objects.get(current=True)
users = s.get_users()
totals = {}

for u in users:
    u_obj = User.objects.get(pk=u.get('user'))
    g1 = ScoreDetails.objects.get(pick__)


exit()    
#t = Tournament.objects.get(current=True)
start = datetime.now()
espn_data = espn_api.ESPNData().get_all_data()

data= golf_serializers.NewFieldSerializer(Field.objects.filter(tournament=t, group__number=1), context={'espn_data': espn_data}, many=True).data
#print (datetime.now() - start)
print (data)

exit()
start1 = datetime.now()
espn_data = espn_api.ESPNData().get_all_data()

data= golf_serializers.NewFieldSerializer(Field.objects.filter(tournament=t), context={'espn_data': espn_data}, many=True).data
#print (datetime.now() - start)
print (len(data), datetime.now() - start1)

exit()

for k,v  in data.items():
    print (k)

exit()
espn = espn_api.ESPNData(mode='setup')
#print (espn.player_started('10548'))

for g in espn.field():
    print (g.get('athlete').get('displayName'))

#field = espn.field()
#print (field[0].get('id') == '10548')
owgr = populateField.get_worldrank()

field = populateField.get_field(t, owgr)

exit()
espn_data = espn_api.ESPNData().get_all_data()
start = datetime.now()
data= golf_serializers.NewFieldSerializer(Field.objects.filter(tournament=t), context={'espn_data': espn_data}, many=True).data
print (datetime.now() - start)
print (len(data))
 

golfers = espn_api.ESPNData().field()

#for g in golfers:
 #   print (g, g.get('status').get('period'), g.get('status').get('type').get('name'), g.get('status').get('type').get('shortDetail'))

exit() 

#     f_len = Field.objects.filter(tournament=t).count()
#     owgr_sum = Field.objects.filter(tournament=t).exclude(currentWGR=9999).aggregate(Sum('currentWGR'))
#     unranked = Field.objects.filter(tournament=t, currentWGR=9999).count()
#     top_100 = round(Field.objects.filter(tournament=t, currentWGR__lte=100).count()/f_len,2)
#     d[t.name] = {'avg_rank': round(int(owgr_sum.get('currentWGR__sum') + (unranked*2000))/f_len,0),
#                  'unranked_golfers': unranked,
#                  'top_100': top_100}

# sorted_d = sorted(d.items(), key=lambda v:v[1].get('avg_rank'))
# for k, v in sorted_d:
#     print (k,v)



sd = ScoreDict.objects.get(tournament=t)

scores = manual_score.Score(sd.data, t)
updated = scores.update_scores()
totals = scores.new_total_scores()
print (totals)
exit()



d = {}



users = season.get_users()
# tie = 0
# no_t = 0
# for sd in ScoreDict.objects.filter(tournament__season=season).exclude(tournament__current=True):
#     t2 = {k:v for k,v in sd.data.items() if k!='info' and v.get('rank') == "T2"}
#     t3 = {k:v for k,v in sd.data.items() if k!='info' and v.get('rank') == "T3"}
#     if len(t2) + len(t3) > 0:
#         tie += 1     
#         print (sd.tournament, len(t2) + len(t3))
#     else:
#         no_t += 1

# print ('tie: ', tie)
# print ('no tie:', no_t)






exit()                 

g = Golfer.objects.get(golfer_name="Hideki Matsuyama")
d = espn_api.ESPNData().player_started(g.espn_number)
e = Golfer.objects.get(golfer_name="Matt Wallace")
f = espn_api.ESPNData().player_started(e.espn_number)
#p = espn_api.ESPNData().picked_golfers()
#print (d)
print (f)
exit()

#golfer detail link  11098 is the espn_id
#http://sports.core.api.espn.com/v2/sports/golf/leagues/pga/events/401243408/competitions/401243408/competitors/11098/status?lang=en&region=us

#historic tournamanet link
#http://sports.core.api.espn.com/v2/sports/golf/leagues/pga/events/401243408

#current event 
#https://site.web.api.espn.com/apis/site/v2/sports/golf/leaderboard?league=pga

#info
#https://gist.github.com/akeaswaran/b48b02f1c94f873c6655e7129910fc3b

#t = Tournament.objects.get(current=True)
#print (t.get_country_counts())

espn_num = '401243404'  #Northern Trust

headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
url =  "https://site.web.api.espn.com/apis/site/v2/sports/golf/leaderboard?league=pga"

#payload = {'week':'1'}
jsonData = get(url, headers=headers).json()

#print ('dur ', datetime.now() - start)

f = open('espn_api.json', "w")
f.write(json.dumps(jsonData))
f.close()

#print('A', jsonData.get('events')[0].keys())
print ('start events keys')
for k, v in jsonData.get('events')[0].items():
    if k != 'competitions':
        print (k, v)
print ('end events keys')
for event in jsonData.get('events'):
    if event.get('id') == espn_num:
        #print (event)
        #continue

        for row in event.get('competitions'):
            print ('start Competions keys')
            print ('field len', len(row.get('competitors')))
            for k, v in row.items():
                if k != 'competitors':
                    print (k, v)
                    print ('================================================')
            print ('end Competions keys')
        
            #print ('B', row.items())
            #print ('status', row.get('holeByHoleSource'))
            for c in row.get('competitors'):
                continue
                #print (c.get('id'), ' ', c.get('athlete').get('displayName'))
                #print (c.get('status'))
                #if c.get('athlete').get('displayName') in ["Hideki Matsuyama", "Abraham Ancer"]:
                #    print (c)
                #    for k, v in c.items():
                #        if k == 'linescores':
                #            for l in v:
                #                #print (l) 
                #                print (' ')
                ##        else:
                #           print (k, v)
                #print  (c)
        #print ('------------------------------------')
    
exit()

d = {}
for sd in ScoreDict.objects.filter(tournament__season__current=True).exclude(tournament__pga_tournament_num__in=['470', '999']):
    winner = [v.get('pga_num') for k,v in sd.data.items() if k != 'info' and v.get('rank') == '1'][0]
    
    golfer  = Golfer.objects.get(espn_number=winner)
    if d.get(golfer.country()):
        d.update({golfer.country(): d.get(golfer.country()) + 1})
    else:
        d[golfer.country()] = 1
print (d)

pd = {}
c = {}
s = Season.objects.get(current=True)
users = s.get_users()
for u in users:
    pd[User.objects.get(pk=u.get('user'))] = {}
try:
    for p in Picks.objects.filter(playerName__tournament__season__current=True):
        f = Field.objects.get(playerName=p.playerName, tournament=p.playerName.tournament)
        if pd.get(p.user).get(f.golfer.country()):
            pd.get(p.user).update({f.golfer.country(): pd.get(p.user).get(f.golfer.country()) + 1})
        else:
            pd.get(p.user).update({f.golfer.country(): 1})

        if c.get(f.golfer.country()):
            c.update({f.golfer.country(): c.get(f.golfer.country()) + 1})
        else:
            c[f.golfer.country()] = 1
except Exception as e:
    print ('failed ', p, p.user)

print (pd)
print (c)

exit()

mens_field = scrape_espn.ScrapeESPN(tournament=t, url='https://www.espn.com/golf/leaderboard?tournamentId=401285309', setup=True).get_data() 
mens_field['mens_info'] = mens_field.get('info')   
womens_field = scrape_espn.ScrapeESPN(tournament=t, url="https://www.espn.com/golf/leaderboard/_/tour/womens-olympics-golf", setup=True).get_data()
womens_field['womens_info'] = womens_field.get('info')

#mens_field = scrape_espn.ScrapeESPN(tournament=t, url='https://www.espn.com/golf/leaderboard?tournamentId=401285309', setup=True).get_data()    
#womens_field = scrape_espn.ScrapeESPN(tournament=t, url="https://www.espn.com/golf/leaderboard/_/tour/womens-olympics-golf", setup=True).get_data()
score_dict = {**mens_field, **womens_field}
if not mens_field.get('info').get('complete'):
    if mens_field.get('info').get('round') > 1:
        info = mens_field.get('info')
        score_dict['info'] = mens_field.get('info')
        score_dict['info']['round_status'] = score_dict.get('info').get('round_status') + " - Mens"

#score_dict.get('info') = mens_field.get('info')
#print (score_dict)
#print (score_dict.get('info'))
#print (mens_field.get('info'))
print (womens_field)
print (score_dict.get('info'))
print (score_dict.get('mens_info'))
print (score_dict.get('womens_info'))
exit()

f = open('lpga_links.json',)
print (type(f))
lpga_data = json.load(f)

for g in Golfer.objects.filter(golfer_pga_num=''):
    print (g)
    link = [v for k,v in lpga_data.items() if g.golfer_name == k.replace('\xa0', ' ')]

    if len(link) == 1:
        print (link)
        pic_link = link[0].get('pic_link')
        print (g, pic_link)
        g.pic_link = pic_link
        g.save()
    else:
        print (g, 'no pic')

exit()

req = Request("https://www.lpga.com/players", headers={'User-Agent': 'Mozilla/5.0'})
html = urlopen(req).read()
   
soup = BeautifulSoup(html, 'html.parser')
#print (soup)
golfers = (soup.find("div", {'id': 'topMoneyListTable'}))
d = {}

for row in golfers.find_all('tr')[1:]:
    try:
        name = row.find_all('td')[1].text.strip()
        lpga_link = str('https://lpga.com/') + row.find_all('td')[1].find('a')['href'].replace(' ', '%20')
        
        
        dtl_req = Request(lpga_link, headers={'User-Agent': 'Mozilla/5.0'})
        dtl_html = urlopen(dtl_req).read()
    
        dtl_soup = BeautifulSoup(dtl_html, 'html.parser')
        #print (soup)
        try:
            pic = str('https://lpga.com') + dtl_soup.find("div", {'class': 'player-banner-gladiator'}).find('img')['src']
        except Exception:
            pic = ''
            print ('no picture', name)
        print (name, pic)
        d[name] = {'link': str('https://www.lpga.com/') + str(lpga_link), 'pic_link': pic}
    except Exception as e:
        print (e)        
with open('lpga_links.json', 'w') as convert_file:
     convert_file.write(json.dumps(d))

#with open('lpga_links.csv', 'w', newline='') as csvfile:
#    csvwriter = csv.writer(csvfile, delimiter=',',
#                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
#    for k, v in d.items():

#        csvwriter.writerow([k, v.link, v.pic_link])

#csvfile.close()


exit()
    

#t = populateField.setup_t('999')
t = Tournament.objects.get(pga_tournament_num='999')
#print (scrape_espn.ScrapeESPN(tournament=t, url="https://www.espn.com/golf/leaderboard/_/tour/womens-olympics-golf", setup=True).get_data())

for f in Field.objects.filter(tournament__pga_tournament_num='999').order_by('currentWGR'):
    print (f, f.currentWGR)
    print (f.golfer, f.golfer.espn_number)
exit()
print (Field.objects.filter(tournament__pga_tournament_num='999').count())

for g in Group.objects.filter(tournament=t):
    print (g, g.playerCnt)
    print (Field.objects.filter(group=g).count())
exit()
#t = populateField.setup_t('999')
#print (scrape_espn.ScrapeESPN(tournament=t, url='https://www.espn.com/golf/leaderboard?tournamentId=401285309', setup=True).get_data())
print (scrape_espn.ScrapeESPN(tournament=t, url="https://www.espn.com/golf/leaderboard/_/tour/womens-olympics-golf", setup=True).get_data())
#print (populateField.get_womans_rankings())
#exit()
#t = populateField.setup_t('999')
t = Tournament.objects.get(pga_tournament_num=999)
ranks = populateField.get_worldrank()
field = populateField.get_field(t,ranks)
#print (field, len(field))
print (len(field))
exit()

f = Field.objects.get(playerName="Dustin Johnson", tournament__current=True)
for k, v in f.season_stats.items():
    print (k, v)

# d = {}

# for stat in StatLinks.objects.all():
#     #url = 'https://www.pgatour.com/stats/stat.02569.html'

    
#     html = urllib.request.urlopen(stat.link)
#     soup = BeautifulSoup(html, 'html.parser')
            
#     for row in soup.find('table', {'id': 'statsTable'}).find_all('tr')[1:]:
#     #print (row)
#     #print(row.find('td', {'class': 'player-name'}).text.strip())
#         if d.get(row.find('td', {'class': 'player-name'}).text.strip()):
#             d[row.find('td', {'class': 'player-name'}).text.strip()].update({stat.name: {
#                                                                 'rank': row.find_all('td')[0].text.strip(),
#                                                                 'rounds': row.find_all('td')[3].text,
#                                                                 'average': row.find_all('td')[4].text,
#                                                                 'total_sg': row.find_all('td')[5].text,
#                                                                 'measured_rounds': row.find_all('td')[6].text}})
#         else:
#             d[row.find('td', {'class': 'player-name'}).text.strip()] = {'pga_num': row.get('id').strip('playerStatsRow')}
#             d[row.find('td', {'class': 'player-name'}).text.strip()].update( 
#                                                                 {stat.name: {'rank': row.find_all('td')[0].text.strip(),
#                                                                 'rounds': row.find_all('td')[3].text,
#                                                                 'average': row.find_all('td')[4].text,
#                                                                 'total_sg': row.find_all('td')[5].text,
#                                                                 'measured_rounds': row.find_all('td')[6].text}})


# print (d['Kevin Na'], len(d))

exit()


#season = Season.objects.get(current=True)
#t = Tournament.objects.get(current=True)
#print (season.get_total_points(t))
#exit()

for t in Tournament.objects.filter(season__current=True):
    #picks = Picks.objects.filter(playerName__tournament=t).values('playerName__playerName').annotate(count=Count('playerName')).order_by('-count')
    #for p in picks:
    #    print (p)
    all_picks = Picks.objects.filter(playerName__tournament=t).aggregate(Count('playerName', distinct=True))
    tot_picks = Picks.objects.filter(playerName__tournament=t).count()
    g_5 = Picks.objects.filter(playerName__tournament=t, playerName__group__number=6).aggregate(Count('playerName', distinct=True))
    tot_g5 = Picks.objects.filter(playerName__tournament=t, playerName__group__number=6).count()
    print (t, all_picks, tot_picks, g_5, tot_g5)
    #print (t, '  ', Picks.objects.filter(playerName__tournament=t).aggregate(Count('playerName', distinct=True)))
    #print (t, '  ', Picks.objects.filter(playerName__tournament=t, playerName__group__number=6).aggregate(Count('playerName', distinct=True)))
exit()

started = 0
not_start = 0
sd = scrape_espn.ScrapeESPN().get_data()
#scores = ScoreDict.objects.get(tournament__current=True)
#sd = scores.data
for f in Field.objects.filter(tournament__current=True):
    if f.started(sd):
        #print (f)
        started += 1
    else:
        print (f)
        not_start += 1

print ('started: ', started)
print ('not started: ', not_start)
exit()
for sd in ScoreDict.objects.filter(tournament__season__current=True):
    if not sd.data.get('info'):
        print ('no info ', sd.tournament)
    elif sd.data.get('info').get('source') != 'espn':
        print ('not espn ', sd.tournament)
    #else:
    #    print ('final ', sd.tournament)

exit()

sd = ScoreDict.objects.get(tournament__current=True)
print (sd.sorted_dict())
exit()
for f in Field.objects.filter(playerName__in=["Scott Brown", "Mark Hubbard", "Rickie Fowler"], tournament__current=True):
    print (f.playerName, f.playing(sd.data))
print (datetime.now() - start)



exit()
t_diff = 0

for t in Tournament.objects.filter(season__current=True):
    ts = TotalScore.objects.filter(tournament=t).order_by('score')
    if ts[1].score != ts[0].score:
        diff = ts[1].score - ts[0].score 
    else:
        diff = ts[2].score - ts[0].score 
    
    t_diff += diff
    if t.major:
        t_diff -= 100

print (t_diff, Tournament.objects.filter(season__current=True).count())
print (t_diff/Tournament.objects.filter(season__current=True).count())
exit()


for a in AccessLog.objects.filter(page='picks'):
    print (a, a.device_type)

exit()

fedex = populateField.get_fedex_data()
for golfer, data  in fedex.items():
       print (golfer, data)
exit()

g = Golfer.objects.get(golfer_name='Dustin Johnson')
print (g.get_pga_player_link())
print (g.get_fedex_stats())
exit()

flag = populateField.get_flag('45526', 'Abraham Ancer')
print (flag)
stats = populateField.get_fedex_stats('45526', 'Abraham Ancer')
print (stats)

exit()

for g in Golfer.objects.filter(golfer_name='Antoine Rozner'):
    for k, v in g.results.items():
        print (k, v)
#for g in Golfer.objects.all():
    
    #mp = g.results.get('153')
    #if mp.get('rank') != 'n/a':
    #    print (g, mp.get('rank'))
        #print (k, r.get('t_name'), r.get('rank'))

sd = ScoreDict.objects.get(tournament__pk=153)
print (sd.data.get('Antoine Rozner'))

start = datetime.now()

exit()

t = Tournament.objects.get(pga_tournament_num=538, season__current=True)
sd = ScoreDict.objects.get(tournament=t)

web = scrape_espn.ScrapeESPN(t, 'https://www.espn.com/golf/leaderboard?tournamentId=401317529', True, False).get_data()
sd.data = web
sd.save()


for f in Field.objects.filter(tournament__current=True):
    f.recent = f.recent_results()
    f.prior_year = f.prior_year_finish()
    f.save()

print ('field done')

for g in Golfer.objects.all():
    g.get_season_results(rerun=True)

print (datetime.now() - start)

exit()

for t in Tournament.objects.filter(season__current=True):
    sd = ScoreDict.objects.get(tournament=t)
    if not sd.data.get('info') and not ("Masters" in t.name or "Match Play" in t.name):
        print ('NAME: ', t.name)
        t_num = scrape_espn.ScrapeESPN(tournament=t).get_t_num(season=t.season)
        #print (t, t_num)
        # if (not created and (not sd.data or len(sd.data) == 0 or len(pga_nums) == 0)) or created:
        # print ('updating prior SD', prior_t)
        # espn_t_num = scrape_espn.ScrapeESPN().get_t_num(prior_season)
        url = "https://www.espn.com/golf/leaderboard?tournamentId=" + t_num
        score_dict = scrape_espn.ScrapeESPN(t,url, True, True).get_data()
        sd.data = score_dict
        #sd.save()
        t.espn_t_num = t_num
        #t.save()

exit()
#Masters
t = Tournament.objects.get(season__current=True, pga_tournament_num='014')
t_num = '401219478'
url = "https://www.espn.com/golf/leaderboard?tournamentId=" + t_num
score_dict = scrape_espn.ScrapeESPN(t,url, True, True).get_data()
sd.data = score_dict
sd.save()
t.espn_t_num = t_num
t.save()

#Zozo
t = Tournament.objects.get(season__current=True, pga_tournament_num='527')
t_num = '401219797'
url = "https://www.espn.com/golf/leaderboard?tournamentId=" + t_num
score_dict = scrape_espn.ScrapeESPN(t,url, True, True).get_data()
sd.data = score_dict
sd.save()
t.espn_t_num = t_num
t.save()




exit()


start = datetime.now()
g = Golfer.objects.get(golfer_name="Justin Thomas")
r= g.get_season_results(Season.objects.get(current=True), rerun=True)
for k, v in r.items():
    print (v)
exit()

#for a in AccessLog.objects.filter(user__username__startswith='j_b').order_by('updated'):
#    print (a.updated, a.page)

#print (Field.objects.filter(tournament__current=True).count())
#t_keys = list(Tournament.objects.filter(season__current=True).values_list('pk', flat=True))
#g = Golfer.objects.get(golfer_name='Justin Thomas')
#print (t_keys)
#for g in Golfer.objects.all():
#    g.results =  g.get_season_results()
#    g.save()

#data = g.get_season_results()
#print (data)
#print (164 in data.keys())
#print (127 in data.keys())

#data = golf_serializers.GolferSerializer(Golfer.objects.all(), many=True)
#print (data.data)
#for g in data.data:
#    print (g)

print (datetime.now() - start)
exit()




score_dict = scrape_espn.ScrapeESPN().get_data()
totals = {}
t = Tournament.objects.get(current=True)
for u in User.objects.filter(username__in=['john', 'jcarl62', 'ryosuke']):
    totals[u.username] = {'total': 0}
for pick in AuctionPick.objects.filter(playerName__tournament=t):
    sd = [v for v in score_dict.values() if v.get('pga_num') == pick.playerName.golfer.espn_number]
    print (pick, utils.formatRank(sd[0].get('rank')))
    if int(utils.formatRank(sd[0].get('rank'))) > score_dict.get('info').get('cut_num'):
        total = totals[pick.user.username].get('total') + int(score_dict.get('info').get('cut_num'))
        rank = rank = (score_dict.get('info').get('cut_num'))
    else:
        total = totals[pick.user.username].get('total') + int(utils.formatRank(sd[0].get('rank')))
        rank = utils.formatRank(sd[0].get('rank'))
    totals[pick.user.username].update({pick.playerName.playerName : rank,
                                        'total': total
                                         })



for k, v in sorted(totals.items(), key= lambda v:v[1].get('total')):
    print (k, v)
print (datetime.now() - start)
exit()

start = datetime.now()

with open('joe.csv', 'w', newline='') as f:
    # create the csv writer
    writer = csv.writer(f)

    header = ['Tournament', 'Group', 'Golfer', 'Current OWGR', 'Last Week OWGR', 'End of last year OWGR', 'Recent Tournament 1', 'Recent Toounament 1 result' \
                , 'Recent Tournament 2', 'Recent Toounament 2 result'
                , 'Recent Tournament 3', 'Recent Toounament 3 result'
                , 'Recent Tournament 4', 'Recent Toounament 4 result'
                ]
    writer.writerow(header)

    for t in Tournament.objects.filter(season__current=True).order_by('-pk')[:3]:
        for f in Field.objects.filter(tournament=t):
            line = []
            line.append(t.name)
            line.append(f.group.number)
            line.append(f.playerName)
            line.append(f.currentWGR)
            line.append(f.sow_WGR)
            line.append(f.soy_WGR)
            for k, v in f.recent.items():
                line.append(v.get('name'))
                line.append(v.get('rank'))
            print (line)
            writer.writerow(line)

exit()


for t in Tournament.objects.filter(season=season):
    ts = list(TotalScore.objects.filter(tournament=t).order_by('user__pk').values_list('score', flat=True))
    ranks = ss.rankdata(ts, method='min')
    for i, (k,v) in enumerate(d.items()):
        print (d[i])
    #print (t, ts)
    #print (ranks)
    
    

print (d)
exit()
g = Group.objects.filter(tournament=tournament).aggregate(Max('number'))
print (g)
exit()
t = Tournament.objects.get(current=True)
g = Golfer.objects.get(golfer_name='Ryan Palmer')
print (g.summary_stats(t.season))
exit()
for f in Field.objects.filter(tournament=t):
    loop_start = datetime.now()
    print (f.golfer.summary_stats(t.season))
    print (f, datetime.now() - loop_start)

print (datetime.now() - start)
exit()
print (web)

web1 = scrape_espn.ScrapeESPN(None, None, False, True).get_data()


#sd = ScoreDetails.objects.filter(pick__playerName__tournament=t)
#print (sd.values_list('pick__playerName__golfer__espn_number', flat=True).distinct(), len(sd.values_list('pick__playerName__golfer__espn_number', flat=True).distinct()))

exit()
for sd in ScoreDetails.objects.filter(pick__playerName__tournament=t, user__username__startswith="shi"):
    print (sd, sd.sod_position)
exit()
sd =ScoreDict.objects.get(tournament=t)
web = scrape_espn.ScrapeESPN().get_data()
print ('---------------')
print (sd.data.get('info'))
print (web.get('info'))

start_1 = datetime.now()
print ('1', {k:v for k,v in sd.data.items() if k != 'info'} == \
    {k:v for k,v in web.items() if k != 'info'})
print ('dur 1:', datetime.now() - start_1)
start_2 = datetime.now()
print ('2', {k:v for k,v in sd.data.get('info').items() if k != 'dict_status'} == \
    {k:v for k,v in web.get('info').items() if k != 'dict_status'})
print ('dur 2:', datetime.now() - start_2)
#print (sd.data == web)
#print (sd.data.get('info'))
#print (web.get('info'))
#print ({k:v for k,v in sd.data.items() if v != v.get('dict_status')})
#sorted_score_dict = {k:v for k, v in sorted(sd.data.items(), if k != 'info' key=lambda item: item[1].get(utils.formatRank(item[1].get('rank'))))}
#print (sorted_score_dict)




exit()


#for user in user_pks:
#    u = User.objects.get(pk=user.get('user'))
#    picks = manual_score.Score(None, t, 'json').get_picks_by_user(u)
#    print (u, picks)

print ('loop dur: ', datetime.now() - start)

serialize_start = datetime.now()
#models = [*ScoreDetails.objects.filter(pick__playerName__tournament=t), *Picks.objects.filter(playerName__tournament=t)]
#data = serializers.serialize('json', models)
data = golf_serializers.ScoreDetailsSerializer('json', ScoreDetails.objects.filter(pick__playerName__tournament=t), many=True)
print (type(data.data))
#for d in data.initial_data:
#    print(type(d))
#    print (d)
print ('serialize dur: ', datetime.now() - serialize_start)
exit()



web1 =  scrape_scores_picks.ScrapeScores(t, 'https://www.pgatour.com/competition/2021/wgc-dell-technologies-match-play/group-stage.html').mp_brackets() 
web = scrape_scores_picks.ScrapeScores(t, 'https://www.pgatour.com/competition/2021/wgc-dell-technologies-match-play/leaderboard.html').mp_final_16()
print (web1)
exit()
#with open('owgr.json') as f:
#  owgr = json.load(f)
for sd in ScoreDict.objects.all():
    #print (sd.tournament)
    solo_2 = {k:v for k,v in sd.data.items() if v.get('rank') =='2'}
    solo_3 = {k:v for k,v in sd.data.items() if v.get('rank') =='3'}
    if len(solo_2) > 0 and len(solo_3) > 0:
        print (sd.tournament, sd.tournament.season)
        print (solo_2)
        print (solo_3)
        print ('-----------------------')
exit()
sds = ScoreDetails.objects.filter(pick__playerName__tournament=t)
print (sd)

exit()
for t in Tournament.objects.all():
    sd = ScoreDetails.objects.filter(pick__playerName__tournament=t).values('user').annotate('score')
    print (sd)
    if len(sd) < 0:
        print (sd)

exit()
t = Tournament.objects.get(current=True)
with open('owgr.json') as f:
  owgr = json.load(f)
#owgr = populateField.get_worldrank()
#owgr = {}
field  = populateField.get_field(t, owgr)
sorted_field = {k:v for k,v in sorted(field.items(), key=lambda item:item[1].get('curr_owgr'))}
print (sorted_field)
exit()
#print (Field.objects.filter(tournament__current=True).count())
f = Field.objects.get(tournament=t, playerName__startswith="By")
print (f, f.recent_results())
exit()


#cbs_web = scrape_cbs_golf.ScrapeCBS().get_data()
#pga_web = scrape_scores_picks.ScrapeScores().scrape_zurich()
#print (pga_web)
#print ('PGA: ', pga_web['info'])
#print ('PGA: ', pga_web['Cameron Smith'])
#print ('CBS: ', cbs_web['info'])
#print ('CBS: ', cbs_web['Cameron Smith'])
#t = Tournament.objects.get(current=True)
#f_start  = datetime.now()
#for pick in Picks.objects.filter(playerName__tournament=t):
    #print (pick)
#    web.get(unidecode(pick.playerName.playerName)).update({'group': pick.playerName.group.number})
    #print (web.get(pick.playerName.playerName))
#print ('duration: ', datetime.now() - start)
#print (web['info'])
exit()





#for player in data['Tournament']['Players']:
#for player in ['Ted Potter, Jr.', ]:
#    name = (' '.join(reversed(player["PlayerName"].rsplit(', ', 1))))
#    print (player.get('PlayerName'), player.get('TournamentPlayerId'), utils.fix_name(name, owgr))
print (utils.fix_name('Ted Potter, Jr.', owgr))


exit()




field = scrape_espn.ScrapeESPN().get_field()
#players = scrape_espn.ScrapeESPN().get_espn_players()
for k, v in field.items():
    print (k, v)
print (len(field))
print (Field.objects.filter(tournament__current=True).count())

exit()

f = Field.objects.get(tournament__current=True, playerName='Matt Kuchar')
print (f.recent_results())
print (datetime.now() - start)
print (f.prior_year_finish())
print (datetime.now() - start)
exit()
def get_mp_result(f, sd):
    #winner = {k:v for k, v in sd.data.items() if k == 'Finals' and {num:match for num, match in v.items() if match.get('winner') == f.playerName}}
    if {k:v for k, v in sd.data.items() if k == 'Finals' and {num:match for num, match in v.items() if match.get('winner') == f.playerName}}:
        return 1 
    elif {k:v for k, v in sd.data.items() if k == 'Finals' and {num:match for num, match in v.items() if match.get('loser') == f.playerName}}:
        return 2
    elif {k:v for k, v in sd.data.items() if k == '3rd Place' and {num:match for num, match in v.items() if match.get('winner') == f.playerName}}:
        return 3
    elif {k:v for k, v in sd.data.items() if k == '3rd Place' and {num:match for num, match in v.items() if match.get('loser') == f.playerName}}:
        return 4
    elif {k:v for k, v in sd.data.items() if k == 'Quaterfinals' and {num:match for num, match in v.items() if match.get('loser') == f.playerName}}:
        return 5
    elif {k:v for k, v in sd.data.items() if k == 'Round of 16' and {num:match for num, match in v.items() if match.get('loser') == f.playerName}}:
        return 9
    else:
        return 17



t = Tournament.objects.get(season__current=True, pga_tournament_num='470')
sd = ScoreDict.objects.get(tournament=t)



for f in Field.objects.filter(tournament=t):
    print (f.playerName, get_mp_result(f, sd))

print (datetime.now() - start)
