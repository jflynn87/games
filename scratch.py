import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from fb_app.models import Week, WeekScore, Player, League, Games, User, Picks, Player
from golf_app.models import BonusDetails, Tournament, Field, Picks, Group, TotalScore
#from datetime import datetime, timedelta
import datetime
import sqlite3
from django.db.models import Min, Q, Count
from golf_app import calc_score


def getRanks(tournament):
            '''takes a dict with a touenamnet number. goes to the PGA web site and pulls back json file of tournament ranking/scores'''
            start = datetime.datetime.now()
            print ('start_time', start)
            import urllib.request
            import json
            #print (tournament.get('pk'))
            json_url = Tournament.objects.get(pk=tournament.get('pk')).score_json_url
            #print (json_url)

            with urllib.request.urlopen(json_url) as field_json_url:
                    data = json.loads(field_json_url.read().decode())

            ranks = {}

            if data['leaderboard']['cut_line']['paid_players_making_cut'] == None:
                ranks['cut number']=len(data["leaderboard"]['players'])
                #ranks['cut number']=0
                cut_score = None
                cut_state = "No cut this week"
                #print ("cut num = " + str(ranks))
            else:
                cut_section = data['leaderboard']['cut_line']
                cut_players = cut_section["cut_count"]
                ranks['cut number']=cut_players
                cut_score = data['leaderboard']['cut_line']['cut_line_score']
                cut_status = data['leaderboard']['cut_line']['show_projected']
                if cut_status is True:
                    cut_state = "Projected"
                else:
                    cut_state = "Actual"
            ranks['cut_status'] = cut_state, cut_score

            round = data['debug']["current_round_in_setup"]
            ranks['round']=round

            #started = data['leaderboard']['is_started']
            #ranks['started'] = started

            finished = data['leaderboard']['is_finished']
            ranks['finished']=finished

            #tournament = Tournament.objects.get(pk=tournament.get('pk'))
            #if tournament.complete is False and finished:
            #    tournament.complete = True
            #    tournament.save()

            #print ('finished = ' + str(finished))


            for row in data["leaderboard"]['players']:
                last_name = row['player_bio']['last_name'].replace(', Jr.', '')
                first_name = row['player_bio']['first_name']
                player = (first_name + ' ' + last_name)
                if (row["current_position"] is '' and round in (2,3,4)) and row['status'] != 'mdf' or row["status"] == "wd":
                    rank = 'cut'
                    if row['status'] == 'wd':
                        score = "WD"
                        sod_position = ''
                    else:
                        score = format_score(row["total"])
                        sod_position = 'cut'
                    today_score = 'cut'
                    thru = ''

                else:
                    if row['status'] == 'mdf':
                        score = format_score(row["total"])
                        rank = 'mdf'
                        sod_position = row["start_position"]
                        today_score = "mdf"
                    else:
                        rank = row["current_position"]
                        score = format_score(row["total"])
                        today_score = format_score(row["today"])
                    if today_score == 'not started':
                        thru = ''
                    else:
                        thru = row['thru']
                    sod_position = row["start_position"]

                #trying to speed up scores
                #if Picks.objects.filter(playerName__playerName=player, playerName__tournament__pk=tournament.get('pk')).exists():
                ranks[player] = rank, score, today_score, thru, sod_position

            #print ('field size from json', len(data["leaderboard"]['players']))
            #print ('field size from db ', len(Field.objects.filter(tournament__pk=tournament.get('pk'))))

            lookup_errors = []
            #if len(ranks) - 4 == len(Field.objects.filter(tournament__pk=tournament.get('pk'))):
            #    print ("no WDs")
            #else:
            for golfer in Field.objects.filter(tournament__pk=tournament.get('pk')):
                    if golfer.formatted_name() not in ranks.keys():
                        #ranks[golfer.formatted_name()] = ('cut', 'WD', 'cut', '', 'cut')
                        lookup_errors.append(golfer.formatted_name())

            end = datetime.datetime.now()
            print ('total', end-start)
            return ranks, lookup_errors

def format_score(score):
    '''takes in a sting and returns a string formatted for the right display or calc'''
    if score == None:
        return "not started"
    if score == 0:
        return 'even'
    elif score > 0:
        return ('+' + str(score))
    else:
        return score


def formatRank(rank):
    '''takes in a sting and returns a string formatted for the right display or calc'''
    if rank == '':
       return rank
    elif rank[0] != 'T':
       return rank
    elif rank[0] == 'T':
       return rank[1:]
    else:
       return rank

def getCutNum(ranks):
    """takes in a dict made from the PGA json file and returns an int of the cut
    number to apply to cut picks.  also applies for witdrawls"""
    if ranks.get('cut_status')[0] == "No cut this week":
        #print ('adjusting for withdrawls')
        wd = 0
        for key, value in ranks.items():
            if key not in ['cut number', 'cut_status', 'round', 'finished']:
                 if value[0] == 'cut':
                     wd += 1
        cutNum = (len(ranks) - 4) - wd  # -4 non players in dict then -WD
    else:
        if ranks.get('round') == 1:
            cutNum = 70
        else:
            cutNum = ranks.get('cut number')

    #print ('cut num function', cutNum)
    return cutNum

print (Picks.objects.filter(playerName__tournament__pk=23).values('playerName').distinct().count())

ranks = getRanks({'pk': 23})
print (len(ranks[0]))
