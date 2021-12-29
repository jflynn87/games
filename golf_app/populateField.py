#from gamesProj.golf_app.models import FedExSeason
from golf_app.models import (Picks, Field, Group, Tournament, TotalScore,
    ScoreDetails, Name, Season, User, BonusDetails, Golfer, ScoreDict, StatLinks, FedExSeason)
import urllib3
from django.core.exceptions import ObjectDoesNotExist
from golf_app import scrape_cbs_golf, scrape_espn, utils, scrape_scores_picks, populateMPField, populateZurichField, espn_api
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


@transaction.atomic
def create_groups(tournament_number):

    '''takes in a tournament number for pgatour.com to get json files for the field and score.  initializes all tables for the tournament'''
    print ('increate groups')
    season = Season.objects.get(current=True)

    if Tournament.objects.filter(season=season).count() > 0 and tournament_number != '999':  #skip for olympics
        try:
            last_tournament = Tournament.objects.get(current=True, complete=True, season=season)
            last_tournament.current = False
            last_tournament.save()
            key = {}
            key['pk']=last_tournament.pk

        except ObjectDoesNotExist:
            print ('no current tournament')
    else:
        print ('setting up first tournament of season')

    print ('going to get_field')
    tournament = setup_t(tournament_number)
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

    html = urllib.request.urlopen("http://www.owgr.com/ranking?pageNo=1&pageSize=All&country=All")
    soup = BeautifulSoup(html, 'html.parser')

    rankslist = (soup.find("div", {'class': 'table_container'}))
    ranks = {}

    for row in rankslist.find_all('tr')[1:]:
        try:
            rank_data = row.find_all('td')
            
            rank_list = []
            i = 0
            for data in rank_data:
                if data.text != '':
                    rank_list.append(int(data.text))
                else:
                    rank_list.append(9999)
                i += 1
                if i == 3:
                    break
            player = (row.find('td', {'class': 'name'})).text.split('(')[0]
            
            ranks[player] = rank_list
        except Exception as e:
            print('exeption 1',row,e)

    print ('end owgr.com lookup')
    
    return ranks

def setup_t(tournament_number):
    '''takes a t number as a string, returns a tournament object'''
    season = Season.objects.get(current=True)
    print ('getting field')
    if tournament_number != '999': #olympics
        json_url = 'https://statdata-api-prod.pgatour.com/api/clientfile/Field?T_CODE=r&T_NUM=' + str(tournament_number) +  '&YEAR=' + str(season) + '&format=json'
        print (json_url)

        req = Request(json_url, headers={'User-Agent': 'Mozilla/5.0'})
        data = json.loads(urlopen(req).read())
        
        print (data["Tournament"]["T_ID"][1:5], str(season))
        if data["Tournament"]["T_ID"][1:5] != str(season):
            print ('check field, looks bad!')
            raise LookupError('Tournament season mismatch: ', data["Tournament"]["T_ID"]) 

        tourny = Tournament()    
        tourny.name = data["Tournament"]["TournamentName"]

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
        tourny.espn_t_num = scrape_espn.ScrapeESPN(tourny).get_t_num()
        tourny.save()
    elif tournament_number == '999':
        json_url = ''
  
        #req = Request(json_url, headers={'User-Agent': 'Mozilla/5.0'})
        #data = json.loads(urlopen(req).read())
        
        #print (data["Tournament"]["T_ID"][1:5], str(season))
        
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
        
    field_dict = {}
    if t.pga_tournament_num == '470':
        print ('match play')
        mp_dict = scrape_scores_picks.ScrapeScores(t, 'https://www.pgatour.com/competition/2021/wgc-dell-technologies-match-play/group-stage.html').mp_brackets()
        for player, data in mp_dict.items():
            ranks = utils.fix_name(player, owgr_rankings)
            field_dict[player] = {'pga_num': data.get('pga_num'),
                                  'curr_owgr': ranks[1][0],
                                  'soy_owgr': ranks[1][2],
                                  'sow_owgr': ranks[1][1]
                                }
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

            #req = Request(json_url, headers={'User-Agent': 'Mozilla/5.0'})
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
            data = espn_api.ESPNData().field()

            for golfer in data:
                name = golfer.get('athlete').get('displayName')
                ranks = utils.fix_name(name, owgr_rankings)
                #need this for now, fix rest of code to use ESPN
                g_obj = Golfer.objects.get(espn_number=golfer.get('athlete').get('id'))

                field_dict[name] = {'pga_num': g_obj.golfer_pga_num, 
                                    'team': None,
                                    'curr_owgr': ranks[1][0],
                                    'soy_owgr': ranks[1][2],
                                    'sow_owgr': ranks[1][1]}


    print (field_dict)
    return field_dict


def configure_groups(field_list, tournament):
    '''takes a list, calculates the number of groups and players per group, returns a dict'''
    print ('config groups')
    group_cnt = 1
    groups = {}
    if len(field_list) > 64:
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
            remainder =  int(len(field_list) % (50 + (group_size *4)))
            print ('remainder ', remainder)
            while group_cnt > 5 and group_cnt < 9:
                groups[group_cnt] = group_size
                group_cnt += 1
            #added to dict at end of funciton
            #group_size = len(field_list) - 50
            #remainder = 0

    elif len(field_list) > 29 and len(field_list) < 65 :
        print ('bet 30 - 64, 10 groups')
        total_groups = 10
        group_size = int(len(field_list) / total_groups)
        remainder = len(field_list) % (total_groups*group_size)
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
    espn_data = get_espn_players()
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

    for g in Golfer.objects.all():
        g.results = g.get_season_results()
        g.save()


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
    espn_data = get_espn_players()
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


def get_individual_stats():
    d = {}
    try: 
        for stat in StatLinks.objects.all():
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

    except Exception as e:
        print ('get_individual_stats exception ', e)

    return d


def get_fedex_data(tournament):
    data = {}
    try:
        link = 'https://www.pgatour.com/fedexcup/official-standings.html'
        fed_ex_html = urllib.request.urlopen(link)
        fed_ex_soup = BeautifulSoup(fed_ex_html, 'html.parser')
        rows = fed_ex_soup.find('table', {'class': 'table-fedexcup-standings'}).find_all('tr')
        try:
            for row in rows[1:]:
                tds = row.find_all('td')
                if not tds[0].get('class'):
                #    print (tds[2].text.strip())
                    data[tds[2].text.replace(u'\xa0', u' ')] = {'rank': tds[0].text, 
                                         'last_week_rank': tds[1].text,
                                        'points': tds[4].text.strip()}
        except Exception as e:
            print ('fedex mapping issue ', e)
    except Exception as ex:
        print ('fedex overall issue ', ex)

    tournament.fedex_data = data
    tournament.save()

    fedex_season = FedExSeason.objects.get(season=tournament.season).update_player_points()

    return data

def get_golfer(player, pga_num, espn_data):
    '''takes a pga_num string, returns a golfer object.  creates golfer if it doesnt exist'''
    golfer, created = Golfer.objects.get_or_create(golfer_pga_num=pga_num)
    golfer.golfer_name = player
    golfer.pic_link = golfer.get_pic_link()
    if golfer.flag_link in [' ', None]:
        golfer.flag_link = golfer.get_flag()
    if golfer.espn_number in [' ', None]:
        golfer.espn_number = get_espn_num(player, espn_data)

    golfer.save() 
    
    return golfer


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


def get_espn_players():
    espn_data = scrape_espn.ScrapeESPN(None, None, True, True).get_data()
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

    if (not created and (not sd.data or len(sd.data) == 0 or len(pga_nums) == 0)) or created:
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
    

    