from golf_app.models import Field, Group, Tournament, Season, Golfer, ScoreDict, StatLinks, FedExSeason
import urllib3
from django.core.exceptions import ObjectDoesNotExist
from golf_app import scrape_cbs_golf, scrape_espn, utils, scrape_scores_picks, populateMPField, populateZurichField, espn_api, pga_t_data
from django.db import transaction
import urllib
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import json
import datetime
import unidecode 
#import collections
from collections import OrderedDict
import csv
import string
from operator import itemgetter
from requests import get
import time


@transaction.atomic
def create_groups(tournament_number, espn_t_num=None):

    '''takes in 2 tournament numbers for pgatour.com and espn.com to get json files for the field and score.  initializes all tables for the tournament'''
    print ('starting populte field', tournament_number)
    season = Season.objects.get(current=True)

    t_data = update_t_data(season)
    if Tournament.objects.filter(season=season).count() > 0 and tournament_number != '999':  #skip for olympics
        try:
            last_tournament = Tournament.objects.get(current=True, complete=True, season=season)
            last_tournament.current = False
            last_tournament.save()
            key = {}
            key['pk']=last_tournament.pk

            for sd in ScoreDict.objects.filter(tournament__season=season):
                if not sd.data_valid():
                    sd.update_sd_data()


        except ObjectDoesNotExist:
            print ('no current tournament')
    else:
        print ('setting up first tournament of season - make sure last season not marketed as current')
        
        #if FedExSeason.objects.filter(season=Season.objects.get(current=True)).exists():
        #    FedExSeason.objects.filter(season=Season.objects.get(current=True)).delete()
        #fs = FedExSeason()
        #fs.season = Season.objects.get(current=True)
        #fs.allow_picks = True
        #fs.prior_season_data = get_fedex_data()
        #fs.save()

    print ('going to get_field')
    tournament = setup_t(tournament_number, espn_t_num)

    owgr_rankings =  get_worldrank()

    field = get_field(tournament, owgr_rankings)
    print ('field length: ', len(field))
    #OWGR_rankings = {}
   
    if tournament.pga_tournament_num not in ['470', '018', '999', '468']:  #Match Play and Zurich (team event)  
        groups = configure_groups(field, tournament)
        prior_year = prior_year_sd(tournament)  #diff sources for MP & Zurich so don't use this func for those events
    elif tournament.pga_tournament_num == '470':
        groups = configure_mp_groups(tournament) #configure MP groups - 16 groups of 4 based on MP groupings
    elif tournament.pga_tournament_num == '018':
        groups = configure_zurich_groups(tournament)
    elif tournament.pga_tournament_num == '999': # my code for olymics
        groups = configure_groups(field, tournament)
    elif tournament.pga_tournament_num == '468': # Ryder Cup
        groups = configure_ryder_cup_groups(tournament)
    else:
        #shouldnt get here
        print ('populate field bad pga number')
        raise Exception ('Bad PGA tournament number: ', tournament.pga_tournament_num)
    
    if tournament.pga_tournament_num == '999':
        create_olympic_field(field, tournament)
    elif tournament.pga_tournament_num == '468':
        create_ryder_cup_field(field, tournament)
    else:
        create_field(field, tournament)
    return ({'msg: ', tournament.name, ' Field complete'})


def update_t_data(season):
    t_data = pga_t_data.PGAData()
    if season.data:
        if season.data == t_data:
            return t_data
        
    print ("UPDATING PGA T DATA")
    new_t_data = pga_t_data.PGAData(update=True)

    return new_t_data
        

def get_womans_rankings():

    #req = Request("https://www.lpga.com/players", headers={'User-Agent': 'Mozilla/5.0'})
    #html = urlopen(req).read()
   
    #soup = BeautifulSoup(html, 'html.parser')
    #print (soup)
    #rankslist = (soup.find("div", {'id': 'topMoneyListTable'}))
    #rankslist = (soup.find("table"))
    #print (rankslist)
    owgr_dict = {}

    with open('rolexrankings_2021-07-19.csv', newline='') as csvfile:
        data = csv.reader(csvfile, delimiter=',', quotechar='|')
        next(data)
        for row in data:
            #print (row[0])
            owgr_dict[string.capwords(row[2].lower())] = {'rank': row[0]}
    #for row in rankslist.find_all('tr')[1:]:
           #try:
            #    player = row[0]
            #    rank = row[1]
            #    ranks[player] = rank
           #except Exception as e:
           #     print('exeption 1',row,e)
    
    return owgr_dict


def get_worldrank():
    '''Goes to OWGR web site takes no input, goes to web to get world golf rankings and returns a dictionary with player name as a string and key, ranking as a string in values'''

    print ('start owgr.com lookp')
    
    url = 'https://apiweb.owgr.com/api/owgr/rankings/getRankings?pageSize=10411&pageNumber=1&regionId=0&countryId=0&sortString=Rank+ASC'
    with urllib.request.urlopen(url) as schedule_json_url:
        data = json.loads(schedule_json_url.read().decode())

    d = {x.get('player').get('fullName').split('(')[0]: [x.get('rank'), x.get('lastWeekRank'), x.get('endLastYearRank')] for x in data.get('rankingsList')}

    return d

    #keep for pga if neeeded  - issue is it only has top 1000
    html = urllib.request.urlopen("https://www.pgatour.com/stats/stat.186.html")
    soup = BeautifulSoup(html, 'html.parser')

    players = (soup.find("table", {'id': 'statsTable'}))

    ranks = {}
    for row in players.find_all('tr')[1:]:
        rank_list = []
        try:
            pga_num = row.get('id').strip('playerStatsRow')
            current_rank = row.find_all('td')[0].text.strip().strip('T')
            last_week = row.find_all('td')[1].text.strip().strip('T')
            soy = '0'
            rank_list = [current_rank, last_week, soy]
            if row.find('a'):
                ranks[row.find('a').text.strip()] = rank_list
            else:
                ranks[row.find('td', {'class': 'player-name'}).text.strip()] = rank_list

        except Exception as e:
            print ('player owgr scrape issue', e)
            print ('row: ', row)

    return ranks

    # for old OWGR website - commented on 8/10/2022 - delete at some point
    # html = urllib.request.urlopen("http://www.owgr.com/ranking?pageNo=1&pageSize=All&country=All")
    # soup = BeautifulSoup(html, 'html.parser')

    # rankslist = (soup.find("div", {'class': 'table_container'}))
    # ranks = {}

    # for row in rankslist.find_all('tr')[1:]:
    #     try:
    #         rank_data = row.find_all('td')
            
    #         rank_list = []
    #         i = 0
    #         for data in rank_data:
    #             if data.text != '':
    #                 rank_list.append(int(data.text))
    #             else:
    #                 rank_list.append(9999)
    #             i += 1
    #             if i == 3:
    #                 break
    #         player = (row.find('td', {'class': 'name'})).text.split('(')[0]
            
    #         ranks[player] = rank_list
    #     except Exception as e:
    #         print('exeption 1',row,e)

    # print ('end owgr.com lookup')
    
    # return ranks

def setup_t(tournament_number, espn_t_num=None):
    '''takes a t number as a string, returns a tournament object'''
    season = Season.objects.get(current=True)
    print ('getting field')
    if tournament_number != '999': #olympics
        json_url = 'https://statdata-api-prod.pgatour.com/api/clientfile/Field?T_CODE=r&T_NUM=' + str(tournament_number) +  '&YEAR=' + str(season) + '&format=json'
        print (json_url)
        tourny = Tournament()    
        try:
                
            req = Request(json_url, headers={'User-Agent': 'Mozilla/5.0'})
            data = json.loads(urlopen(req).read())
            
            print (data["Tournament"]["T_ID"][1:5], str(season))
            if data["Tournament"]["T_ID"][1:5] != str(season):
                print ('check field, looks bad!')
                raise LookupError('Tournament season mismatch: ', data["Tournament"]["T_ID"]) 
            tourny.name = data["Tournament"]["TournamentName"]
        except Exception as e:
            print ('PGA lookup issue, going to espn', e)
            url = 'https://www.espn.com/golf/leaderboard?tournamentId=' + str(espn_t_num)
            espn = scrape_espn.ScrapeESPN(tournament=tourny, setup=True, url=url)
            print ('espn T Name: ', espn.get_t_name())
            tourny.name = espn.get_t_name()

        tourny.season = season
        start_date = datetime.date.today()
        print (start_date)
        while start_date.weekday() != 3:
            start_date += datetime.timedelta(1)
        tourny.start_date = start_date
        tourny.field_json_url = json_url
        tourny.score_json_url = 'https://statdata.pgatour.com/r/' + str(tournament_number) +'/' + str(season) + '/leaderboard-v2mini.json'
        
        tourny.pga_tournament_num = tournament_number
        tourny.current=True
        tourny.complete=False
        tourny.score_update_time = datetime.datetime.now()
        tourny.cut_score = "no cut info"
        tourny.saved_cut_num = 65
        tourny.saved_round = 1
        tourny.saved_cut_round = 2
        if espn_t_num:
            tourny.espn_t_num = espn_t_num
        else:    
            tourny.espn_t_num = scrape_espn.ScrapeESPN(tourny).get_t_num()
        tourny.save()
    elif tournament_number == '999':
        json_url = ''
  
        tourny = Tournament()    
        tourny.name = "Olympic Golf"

        tourny.season = season
        start_date = datetime.date.today()
        
        while start_date.weekday() != 3:
            start_date += datetime.timedelta(1)
        tourny.start_date = start_date
        tourny.field_json_url = json_url
        tourny.score_json_url = ''
        
        tourny.pga_tournament_num = tournament_number
        tourny.current=True
        tourny.complete=False
        tourny.score_update_time = datetime.datetime.now()
        tourny.cut_score = "no cut info"
        tourny.saved_cut_num = 60
        tourny.saved_round = 1
        #tourny.saved_cut_round = 2 
        tourny.has_cut = False
        tourny.espn_t_num = '401285309'
        tourny.save()

       # Ryder cup: tourny.espn_t_num = '401219595'

    else:
        raise Exception('Unknown T Num logic, pls check')
        
    return tourny

def get_field(t, owgr_rankings):
    '''takes a tournament object, goes to web to get field and returns a dict'''
    print ('getting field get_field func')        
    field_dict = {}
    if t.pga_tournament_num == '470':
        print ('match play')
        mp_dict = scrape_scores_picks.ScrapeScores(t, 'https://www.pgatour.com/competition/' + str(t.season.season) + '/wgc-dell-technologies-match-play/group-stage.html').mp_brackets()
        for player, data in mp_dict.items():
            ranks = utils.fix_name(player, owgr_rankings)
            field_dict[player] = {'pga_num': data.get('pga_num'),
                                  'curr_owgr': ranks[1][0],
                                  'soy_owgr': ranks[1][2],
                                  'sow_owgr': ranks[1][1]
                                }
        print ('mp field dict: ', field_dict)
    elif t.pga_tournament_num == '999': #Olympics
        # update this to use the class from olympics_sd.py
        mens_field = scrape_espn.ScrapeESPN(tournament=t, url='https://www.espn.com/golf/leaderboard?tournamentId=401285309', setup=True).get_data()    
        womens_field = scrape_espn.ScrapeESPN(tournament=t, url="https://www.espn.com/golf/leaderboard/_/tour/womens-olympics-golf", setup=True).get_data()
        
        for man, data in mens_field.items():
            if man != 'info':
                ranks = utils.fix_name(man, owgr_rankings)
                field_dict[man] = {'espn_num': data.get('pga_num'),
                                    'sex': 'dude',
                                  'curr_owgr': ranks[1][0],
                                  'soy_owgr': ranks[1][2],
                                  'sow_owgr': ranks[1][1], 
                                  'flag': data.get('flag')
                                }
        womens_ranks = get_womans_rankings()

        for woman, stats in womens_field.items():
            
            if woman != 'info':
                rank = utils.fix_name(woman, womens_ranks)
                field_dict[woman] ={'espn_num': stats.get('pga_num'),
                                    'sex': 'chick',
                                    'curr_owgr': int(rank[1].get('rank')) + 1000,
                                    'flag': stats.get('flag')}
        #field_dict['info'] = mens_field.get('info')
    #elif t.pga_tournament_num == 'RYDCUP':
    else:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
            json_url = 'https://statdata-api-prod.pgatour.com/api/clientfile/Field?T_CODE=r&T_NUM=' + str(t.pga_tournament_num) +  '&YEAR=' + str(t.season.season) + '&format=json'
            print (json_url)

            req = Request(json_url, headers=headers)
            data = json.loads(urlopen(req).read())
            print ('data', len(data))
            for player in data["Tournament"]["Players"][0:]:
                if player["isAlternate"] == "Yes":
                        #exclude alternates from the field
                        continue

                name = (' '.join(reversed(player["PlayerName"].rsplit(', ', 1))))
                playerID = player['TournamentPlayerId']
                if player.get('TeamID'):
                    team = player.get('TeamID')
                elif player.get('cupTeam'):
                    team = player.get('cupTeam')
                else:
                    team = None

                ranks = utils.fix_name(name, owgr_rankings)
                field_dict[name] = {'pga_num': playerID,
                                    'team': team,
                                    'curr_owgr': ranks[1][0],
                                    'soy_owgr': ranks[1][2],
                                    'sow_owgr': ranks[1][1]}
        except Exception as e:
            print ('pga scrape failed: ', e)   #to use this need to update to key everything from espn_num
            data = espn_api.ESPNData(t=t, force_refresh=True, setup=True).field()

            for golfer in data:
                name = golfer.get('athlete').get('displayName')
                ranks = utils.fix_name(name, owgr_rankings)
                #need this for now, fix rest of code to use ESPN
                try:
                    g_obj = Golfer.objects.get(espn_number=golfer.get('athlete').get('id'))
                    print ('build field found golfer', g_obj)
                except Exception as f:
                    print ('build field cant find: ', name, ' trying setup')
                    pga_num = find_pga_num(name)
                    
                    if not pga_num:
                        g_obj = get_golfer(player=name, pga_num=None, espn_num=golfer.get('athlete').get('id'))
                    elif len(pga_num) == 1:
                        g_obj = get_golfer(player=name, pga_num=pga_num[0], espn_num=golfer.get('athlete').get('id') )
                    else:
                        g_obj = get_golfer(player=name, pga_num=None, espn_num=golfer.get('athlete').get('id'))

                ranks = utils.fix_name(name, owgr_rankings)
                field_dict[name] = {'pga_num': g_obj.golfer_pga_num, 
                                    'team': None,
                                    'curr_owgr': ranks[1][0],
                                    'soy_owgr': ranks[1][2],
                                    'sow_owgr': ranks[1][1]}


    print (field_dict)
    return field_dict


def configure_groups(field_list, tournament):
    '''takes a list, calculates the number of groups and players per group, returns a dict'''
    ## try to simplify this 10 picks (9 or 10 groups) for any tournament over 30 and dynamic gruoups of 3 for smaller.  
    print ('config groups')
    group_cnt = 1
    groups = {}
    #if len(field_list) > 64:
    if len(field_list) > 89:
        group_size = 10

        if tournament.pga_tournament_num == '999':
            print ('setting up olympics')
            group_size = 12
            while group_cnt < 10:
                groups[group_cnt] = group_size
                group_cnt += 1
            remainder = 0
        else:
            while group_cnt <6:
                groups[group_cnt] = group_size
                group_cnt += 1

            group_size = int(round((len(field_list) - 50)/4, 0))
            print ('group size 6-8: ', group_size)
            if (group_size * 4) + 50 >= len(field_list):
                remainder = len(field_list) - (50 + 4*group_size)
            else:
                remainder =  int(len(field_list) % (50 + (group_size *4)))
            print ('remainder ', remainder)
            while group_cnt > 5 and group_cnt < 9:
                groups[group_cnt] = group_size
                group_cnt += 1
            #added to dict at end of funciton
            #group_size = len(field_list) - 50
            #remainder = 0

    #elif len(field_list) > 29 and len(field_list) < 65 :
    elif len(field_list) > 29 and len(field_list) < 90:
        ## change this to just spread the field.  Don't forget you need specific logic for the hero (18 golfer field)
        print ('bet 30 - 69, 10 groups')
        total_groups = 10
        group_size = int(round(len(field_list) / total_groups, 0))  #if you round this you need to cope wiht a negative remainder and smaller last group.
        if len(field_list) > total_groups*group_size:
            remainder = len(field_list) % (total_groups*group_size)
        else:
            remainder = len(field_list) - (total_groups*group_size)
        
        while group_cnt < total_groups:
            groups[group_cnt] = group_size
            group_cnt +=1
    else:
        #should only be here for fields less than 30 golfers
        print ('field less than 30')
        group_size = 3
        remainder = len(field_list) % (group_size)     
        total_groups = (len(field_list)-(remainder))/group_size

        while group_cnt < total_groups:
            groups[group_cnt] = group_size
            group_cnt +=1
    print ('XXX ', group_size, remainder)
    if remainder == 0:
        groups[group_cnt] = group_size
    else:
        groups[group_cnt] = group_size + remainder

    for k,v in groups.items():
        Group.objects.get_or_create(tournament=tournament, number=k,playerCnt=v)[0]

    print ('Configured Groups: ', groups)
    return groups

def configure_mp_groups(tournament):
    '''takes a tournament, creates 12 groups of 4,  assumes 64 player tournament.  retruns a dict'''
    print ('config MP groups')
    #print ('len field list in configure_groups: ', len(field_list))
    group_dict = {}

    group = 1
    while group < 17:
        #Group.objects.get_or_create(tournament=Tournament.objects.get(current=True, season__current=True), number=group,playerCnt=4)
        Group.objects.get_or_create(tournament=tournament, number=group,playerCnt=4)
        group_dict[group] = '4' #hardcode to 4 as MP has 4 per group
        group += 1

    print (group_dict)
    return group_dict

def configure_zurich_groups(tournment):
    '''takes a tournament.  updates groups for the tournament, retruns a dict'''
    group_dict = {}
    i = 1
    while i < 9:
        group = Group()
        group.tournament = tournment
        group.number = i
        group.playerCnt = 10
        group.save()
        group_dict[i]=10 #hard coded to 10, assumes 80 teams.  
        i +=1
    
    return group_dict


def configure_ryder_cup_groups(tournment):
    '''takes a tournament.  updates groups for the tournament, retruns a dict'''
    group_dict = {}
    i = 1
    while i < 7:
        group = Group()
        group.tournament = tournment
        group.number = i
        group.playerCnt = 4
        group.save()
        group_dict[i]=4 
        i +=1
    
    return group_dict


def create_field(field, tournament):
    '''takes a dict and tournament object, updates creates field database, returns a dict'''
    sorted_field = {}
    espn_data = get_espn_players(tournament)
    if tournament.pga_tournament_num == '470':
        sorted_field = field
    elif tournament.pga_tournament_num == '018':
        sorted_field = zurich_field(field) #Zurich team logic
    else:
        sorted_field = OrderedDict({k:v for k,v in sorted(field.items(), key=lambda item: int(item[1].get('curr_owgr')))})
        #print (sorted_field)
    player_cnt = 1
    group_num = 1

    for player, info in sorted_field.items():
        print (player, info)
        golfer = get_golfer(player, info.get('pga_num'), espn_data)
        group = Group.objects.get(tournament=tournament, number=group_num)
        #print (player, info)
        f = Field()

        f.tournament = tournament
        f.playerName = player
        f.alternate = False
        f.playerID = info.get('pga_num')
        f.golfer = golfer
        f.group = group
        if info.get('team'):
            f.teamID = info.get('team')
            f.partner = info.get('partner')
            f.partner_golfer = get_golfer(info.get('partner'), info.get('partner_pga_num'), espn_data)
            f.partner_owgr = info.get('partner_owgr')
            f.currentWGR = info.get('team_owgr')
        else:
            f.currentWGR = info.get('curr_owgr')
            f.sow_WGR = info.get('sow_owgr')
            f.soy_WGR = info.get('soy_owgr')

        f.save()
    
        if player_cnt < group.playerCnt:
            player_cnt += 1
        elif player_cnt == group.playerCnt:
            group_num += 1
            player_cnt = 1

    # doing here to save this data before updating the field by field records
    fed_ex = get_fedex_data(tournament)
    individual_stats = get_individual_stats()


    #need to do this after full field is saved for the calcs to work.  No h/c in MP
    # Move to separate functions for performance
    # fed_ex = get_fedex_data(tournament)
    # individual_stats = get_individual_stats()

    # for f in Field.objects.filter(tournament=tournament):
        
    #     if tournament.pga_tournament_num not in ['470', '018']:
    #         f.handi = f.handicap()
    #     else:
    #         f.handi = 0
        
    #     f.prior_year = f.prior_year_finish()
    #     recent = OrderedDict(sorted(f.recent_results().items(), reverse=True))
    #     f.recent = recent
    #     f.season_stats = f.golfer.summary_stats(tournament.season) 

    #     #print (fed_ex)
    #     if fed_ex.get(f.playerName):
    #        f.season_stats.update({'fed_ex_points': fed_ex.get(f.playerName).get('points'),
    #                               'fed_ex_rank': fed_ex.get(f.playerName).get('rank')})
    #     else:
    #        f.season_stats.update({'fed_ex_points': 'n/a',
    #                               'fed_ex_rank': 'n/a'})

    #     if individual_stats.get(f.playerName):
    #         player_s = individual_stats.get(f.playerName)
    #         for k, v in player_s.items():
    #             if k != 'pga_num':
    #                 f.season_stats.update({k: v})
        
    #     f.save()

    # for g in Golfer.objects.all():
    #     g.results = g.get_season_results()
    #     g.save()


    print ('saved field objects')


def create_olympic_field(field, tournament):
    '''takes a dict and tournament object, updates creates field database, returns a dict'''
    sorted_field = {}
    #espn_data = get_espn_players()
    sorted_field = OrderedDict({k:v for k,v in sorted(field.items(), key=lambda item: int(item[1].get('curr_owgr')))})

    player_cnt = 1
    group_num = 1

    for player, info in sorted_field.items():
        print (player, info)
        if info.get('espn_num') and Golfer.objects.filter(espn_number=info.get('espn_num')).exists():
            golfer = Golfer.objects.get(espn_number=info.get('espn_num'))
        elif Golfer.objects.filter(golfer_name=player).exists():
            golfer = Golfer.objects.get(golfer_name=player)
            golfer.espn_number = info.get('espn_num')
            if not golfer.flag_link or golfer.flag_link == '':
                golfer.flag_link = info.get('flag')
            golfer.save()
        else:
            golfer = Golfer()
            golfer.golfer_name=player
            golfer.espn_number = info.get('espn_num')
            golfer.flag_link = info.get('flag')
            golfer.save()


        #golfer = get_golfer(player, info.get('pga_num'), espn_data)
        group = Group.objects.get(tournament=tournament, number=group_num)
        #print (player, info)
        f = Field()

        f.tournament = tournament
        f.playerName = player
        f.alternate = False
        #f.playerID = info.get('pga_num')
        f.golfer = golfer
        f.group = group
        f.currentWGR = info.get('curr_owgr')

        f.save()
    
        if player_cnt < group.playerCnt:
            player_cnt += 1
        elif player_cnt == group.playerCnt:
            group_num += 1
            player_cnt = 1

    #need to do this after full field is saved for the calcs to work.  No h/c in MP
    fed_ex = get_fedex_data(tournament)
    individual_stats = get_individual_stats()

    for f in Field.objects.filter(tournament=tournament):
        if tournament.pga_tournament_num not in ['470', '018']:
            f.handi = f.handicap()
        else:
            f.handi = 0

        f.prior_year = f.prior_year_finish()
        recent = OrderedDict(sorted(f.recent_results().items(), reverse=True))
        f.recent = recent
        f.season_stats = f.golfer.summary_stats(tournament.season) 

       # print (fed_ex)#
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

    for g in Golfer.objects.all():
        g.results = g.get_season_results()
        g.save()


    print ('saved field objects')


def create_ryder_cup_field(field, tournament):
    '''takes a dict and tournament object, updates creates field database, returns a dict'''
    sorted_field = {}
    espn_data = get_espn_players(tournament)
    intl_d = {k:v for k,v in field.items() if v.get('team') == "INTL"}
    sorted_intl = OrderedDict({k:v for k,v in sorted(intl_d.items(), key=lambda item: int(item[1].get('curr_owgr')))})
    usa_d = {k:v for k,v in field.items() if v.get('team') == "USA"}
    sorted_usa = OrderedDict({k:v for k,v in sorted(usa_d.items(), key=lambda item: int(item[1].get('curr_owgr')))})

    player_cnt = 1
    group_num = 1

    for player, info in sorted_intl.items():
        print (player, info)
        golfer = get_golfer(player, info.get('pga_num'), espn_data)
        golfer = Golfer.objects.get(golfer_pga_num=info.get('pga_num'))  #assume any ryder cup golfer already set up
        group = Group.objects.get(tournament=tournament, number=group_num)
        #print (player, info)
        f = Field()
        print ('saving field')
        f.tournament = tournament
        f.playerName = player
        f.alternate = False
        f.playerID = info.get('pga_num')
        f.golfer = golfer
        f.group = group
        f.teamID = info.get('team')
        f.currentWGR = info.get('curr_owgr')
        f.sow_WGR = info.get('sow_owgr')
        f.soy_WGR = info.get('soy_owgr')
        f.handi = 0

        f.save()
        #print ('saved field')
        if player_cnt < 2:  #hard code ok, just 2 per team per group
            player_cnt += 1
        elif player_cnt == 2:
            group_num += 1
            player_cnt = 1
        #f.save()

    #need to do this after full field is saved for the calcs to work.  No h/c in MP
    #print ('thru field')

    player_cnt = 1
    group_num = 1

    for player, info in sorted_usa.items():
        print (player, info)
        golfer = get_golfer(player, info.get('pga_num'), espn_data)
        group = Group.objects.get(tournament=tournament, number=group_num)
        #print (player, info)
        f = Field()

        f.tournament = tournament
        f.playerName = player
        f.alternate = False
        f.playerID = info.get('pga_num')
        f.golfer = golfer
        f.group = group
        f.teamID = info.get('team')
        f.currentWGR = info.get('curr_owgr')
        f.sow_WGR = info.get('sow_owgr')
        f.soy_WGR = info.get('soy_owgr')
        f.handi = 0

        f.save()
    
        if player_cnt < 2:  #hard code ok, just 2 per team per group
            player_cnt += 1
        elif player_cnt == 2:
            group_num += 1
            player_cnt = 1

    #need to do this after full field is saved for the calcs to work.  No h/c in MP
    fed_ex = get_fedex_data(tournament)
    individual_stats = get_individual_stats()

    for f in Field.objects.filter(tournament=tournament):

        f.prior_year = 'n/a'
        recent = OrderedDict(sorted(f.recent_results().items(), reverse=True))
        f.recent = recent
        f.season_stats = f.golfer.summary_stats(tournament.season) 

        # print (fed_ex)#
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

    for g in Golfer.objects.all():
        g.results = g.get_season_results()
        g.save()


    print ('saved Ryder Cup field objects')


def get_individual_stats(t=None):
    start = datetime.datetime.now()
    d = {}

    if not t:
        t= Tournament.objects.get(current=True)

    if t.individual_stats and len(t.individual_stats) > 0:
        return t.individual_stats
    for stat in StatLinks.objects.all():
        print (stat.link)
        try: 
            html = urllib.request.urlopen(stat.link)
            soup = BeautifulSoup(html, 'html.parser')

            for row in soup.find('table', {'id': 'statsTable'}).find_all('tr')[1:]:
                if d.get(row.find('td', {'class': 'player-name'}).text.strip()):
                    d[row.find('td', {'class': 'player-name'}).text.strip()].update({stat.name: {
                                                                        'rank': row.find_all('td')[0].text.strip(),
                                                                        #'rounds': row.find_all('td')[3].text,
                                                                        'average': row.find_all('td')[4].text,
                                                                        'total_sg': row.find_all('td')[5].text,
                                                                        #'measured_rounds': row.find_all('td')[6].text
                                                                        }})
                else:
                    d[row.find('td', {'class': 'player-name'}).text.strip()] = {'pga_num': row.get('id').strip('playerStatsRow'),
                                                                                'stats_rounds': row.find_all('td')[3].text,
                                                                                'stats_measured_rounds': row.find_all('td')[6].text
                                                                                }
                    d[row.find('td', {'class': 'player-name'}).text.strip()].update( 
                                                                        {stat.name: {'rank': row.find_all('td')[0].text.strip(),
                                                                        #'rounds': row.find_all('td')[3].text,
                                                                        'average': row.find_all('td')[4].text,
                                                                        'total_sg': row.find_all('td')[5].text,
                                                                        #'measured_rounds': row.find_all('td')[6].text
                                                                        }})

            t.individual_stats = d
            t.save()

        except Exception as e:
            print ('get_individual_stats exception ', stat.link, e)
    print ('individual stats calc duraion: ', datetime.datetime.now() - start)
    return d


def get_fedex_data(tournament=None):
    '''takes an optional tournament object to update/setup, returns a dict'''
    print ('updating fedex data')    
    if tournament:
        if tournament.fedex_data and len(tournament.fedex_data) > 0:
            return tournament.fedex_data

    data = {}
    try:
        season = Season.objects.get(current=True)
        link = 'https://www.pgatour.com/fedexcup/official-standings.html'
        fed_ex_html = urllib.request.urlopen(link)
        fed_ex_soup = BeautifulSoup(fed_ex_html, 'html.parser')
        rows = fed_ex_soup.find('table', {'class': 'table-fedexcup-standings'}).find_all('tr')
        fedex_data_year = fed_ex_soup.find('h2', {'class': 'title'}).text.strip()[:4]
        if Tournament.objects.filter(season__current=True).count() > 0 and not str(season.season) == str(fedex_data_year):
            print ('fedex data season mismatch')
            return {}
        try:
            for row in rows[1:]:
                tds = row.find_all('td')
                if not tds[0].get('class'):
                #    print (tds[2].text.strip())
                    data[tds[2].text.replace(u'\xa0', u' ')] = {'rank': tds[0].text, 
                                         'last_week_rank': tds[1].text,
                                        'points': tds[4].text.strip().replace(',', '')}
        except Exception as e:
            print ('fedex mapping issue ', e)
    except Exception as ex:
        print ('fedex overall issue ', ex)

    fedex_data_year = fed_ex_soup.find('h2', {'class': 'title'}).text.strip()[:4]
    if tournament:
        tournament.fedex_data = data
        tournament.save()
        fedex_season = FedExSeason.objects.get(season=tournament.season).update_player_points()

    return data

def get_golfer(player, pga_num=None, espn_data=None, espn_num=None):
    '''takes a pga_num string, returns a golfer object.  creates golfer if it doesnt exist'''
    #player is the golfer name
    if pga_num and Golfer.objects.filter(golfer_pga_num=pga_num).exists():
        golfer = Golfer.objects.get(golfer_pga_num=pga_num)
    elif Golfer.objects.filter(golfer_name=player, golfer_pga_num__in=['', None]).exists() and pga_num:
        golfer = Golfer.objects.get(golfer_name=player, golfer_pga_num__in=['', None])
        golfer.golfer_pga_num = pga_num
        golfer.save()
    else:
        g = Golfer()
        if pga_num:
            g.golfer_pga_num=pga_num
        else:
            g.golfer_pga_num = ''
        g.golfer_name = player
        g.save()
        golfer = g
    
    if golfer.pic_link in [' ', None]:
        golfer.pic_link = golfer.get_pic_link()
        golfer.save()

    if golfer.flag_link in [' ', None]:
        golfer.flag_link = golfer.get_flag()
        golfer.save()

    if espn_num:
        golfer.espn_num = espn_num
    elif golfer.espn_number in [' ', None] and espn_data:
        golfer.espn_number = get_espn_num(player, espn_data)
    #else:
    #    golfer.espn_number = ''

    golfer.save() 
    
    return golfer


def find_pga_num(golfer_name):
    '''takes a string returns a string'''
    start = datetime.datetime.now()
    names = golfer_name.split(' ')
    last_name = names[len(names)-1]
    first_name = names[0]
    print (last_name)
    print (first_name)
    headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
    url =  "https://statdata.pgatour.com/players/player.json"
    data = get(url, headers=headers).json()
    
    players = [v.get('pid') for v in data.get('plrs') if v.get('nameL') == last_name and v.get('nameF') == first_name] 

    if len(players) > 1:
        print ("Multiple possible PGA numbers ", golfer_name)
        print (players)
        return None
    elif len(players) == 1:
        print ('found player pga num: ', golfer_name, players)
        return players[0]
    else:
        print ("FInd PGA numbers found none", golfer_name)
        return None

    
    ## This is incomplete, but complete and use if you need to scrape
    # start = datetime.datetime.now()
    # link = 'https://www.pgatour.com/players.html'
    # players_html = urllib.request.urlopen(link)
    # players_soup = BeautifulSoup(players_html, 'html.parser')
    # rows = players_soup.find_all('li', {'class': 'player-card'})
    # d = {}
    # for r in rows:
    #     #print (r.find('span', {'class', 'player-surname'}).text)
    #     #print (r.find('span', {'class', 'player-firstname'}).text)
    #     pga_num = str(r.find('a', {'class', 'player-link'}).get('href').split('/')[2].split('.')[1])
    #     full_name = r.find('span', {'class', 'player-firstname'}).text + ' ' + r.find('span', {'class', 'player-surname'}).text
    #     d[pga_num] = {'golfer': full_name}
    #     #d[r.find('a', {'class', 'player-link'}).get('href').split('/')[2].split('.')[1]] = {'golfer': r.find('span', {'class', 'player-firstname'}).text + ' ' + r.find('span', {'class', 'player-surname'}).text}
    # print ('find pga dur: ', datetime.datetime.now() - start)
    # print (d.get('01006'))
    return


def get_espn_num(player, espn_data):
    if espn_data.get(player):
        print ('returning found: ', player, espn_data.get(player))
        #return player, espn_data.get(player)
        return espn_data.get(player).get('pga_num')
    else:
        print ('not found, fixing: ', player)
        fixed_data = utils.fix_name(player, espn_data)
        print ('returning fixed: ',  fixed_data)
        if fixed_data[0] == None:
            #return (player, {})
            return None
        else:
            #return player, fixed_data[1]
            return fixed_data[1].get('pga_num')
        
    return


def get_espn_players(t):
    espn_data = scrape_espn.ScrapeESPN(t, None, True, True).get_data()
    return espn_data


def prior_year_sd(t, current=None):
    '''takes a tournament and bool, returns nothing.  Current skips prior year and resets the SD for that tournament'''
    if not current:
        try:
            prior_season = Season.objects.get(season=int(t.season.season)-1)
            prior_t = Tournament.objects.get(pga_tournament_num=t.pga_tournament_num, season=prior_season)
        except Exception as e:
            print ('no prior tournament, getting 2 years ago', e)
            try:
                prior_season = Season.objects.get(season=int(t.season.season)-2)
                prior_t = Tournament.objects.get(pga_tournament_num=t.pga_tournament_num, season=prior_season)
            except Exception as f:
                print ('no prior 2 years ago, returning nothing', f)
                return {}
    else:
        prior_season = t.season
        prior_t = t

    print ('proir T: ', prior_t, prior_t.season)
    sd, created = ScoreDict.objects.get_or_create(tournament=prior_t)
    if not created:
        pga_nums = [v.get('pga_num') for (k,v) in sd.data.items() if k != 'info' and v.get('pga_num')] 
        print ('prior SD # of pga nums: ', len(pga_nums))
    else:
        print ('created score dict')

    if (not created and (not sd.data or len(sd.data) == 0 or not sd.data.get('info'))) or created:  #added info check to update if not from espn
        print ('updating prior SD', prior_t)
        espn_t_num = scrape_espn.ScrapeESPN(prior_t).get_t_num(prior_season)
        print ('espn T num', espn_t_num)
        url = "https://www.espn.com/golf/leaderboard?tournamentId=" + espn_t_num
        score_dict = scrape_espn.ScrapeESPN(prior_t,url, True, True).get_data()
        print ('saving prior SD,  SD data len: ', prior_t, len(score_dict))
        sd.data = score_dict
        sd.save()
    return sd.data
                

def zurich_field(field):
    field_dict = {}
    for k, v in sorted(field.items(), key=lambda item: item[1].get('curr_owgr')):
        team= v.get('team')
        print (team)
        #print (field_dict)
        data = [k for k, v in field_dict.items() if v.get('team') == team]
        print (data)
        if len(data) > 0:
            #partner
            field_dict[data[0]].update({
                'partner': k,
                'partner_pga_num': v.get('pga_num'),
                'partner_owgr': v.get('curr_owgr'),
                'team_owgr': v.get('curr_owgr') + field_dict.get(data[0]).get('curr_owgr')
                
            })
        else:
            #main guy
            field_dict[k] = {
                'pga_num': v.get('pga_num'),
                'curr_owgr': v.get('curr_owgr'),
                'soy_owgr': v.get('soy_owgr'),
                'sow_owgr': v.get('sow_owgr'),
                'team': team
            }

    return OrderedDict(sorted(field_dict.items(), key=lambda item: item[1].get('team_owgr')))
    #return OrderedDict({k:v for k,v in sorted(field.items(), key=lambda item: item['team']['curr_wgr'] + item['team']['curr_wgr'])})
    

    