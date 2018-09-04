import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","golfProj.settings")

import django
django.setup()
import urllib3
from golf_app.models import Field, Group, Tournament

from django.shortcuts import render, get_object_or_404, redirect

def calc_score():
       '''takes no input, loops thru groups to find low scores'''

       scores = {}
       totalScore = 0
       score_list = {}

       ranks = getRanks()
       field = Field.objects.all()

       for group in Group.objects.all():
           for player in Field.objects.filter(group=group):
               if str(player) in ranks.keys():  #needed to deal wiht WD's before start of tourn.
                  #if ranks[player.playerName][0] != "cut":
                    if ranks[player.playerName][0] != "cut":
                        print (player)
                        score_list[str(player)] = int(formatRank(ranks[player.playerName][0]))
               else:
                    continue


           scores[group]=score_list
           score_list = {}
           total_score = 0

       for group, golfers in scores.items():
                    #print (group, golfers)
                leader = (min(golfers, key=golfers.get))
                #print ("Group " + str(group) + ": " + "pos: " + str(golfers.get(leader)) + "   " +str(leader))
                print ("Group ", str(group), ": " , "pos: ", str(golfers.get(leader)), "   ", str(leader))
                total_score += golfers.get(leader)

       print ("Total Score: " + str(total_score))
            #print ("Group: " + str(group) + ' players making cut: ' + str(len(golfers)))
            #print ("Best Pick: " + str(min(golfers, key=golfers.get)))
            #print (golfers)










def getRanks():
            '''takes no input. goes to the PGA web site and pulls back json file of tournament ranking/scores'''

            import urllib.request
            import json

            json_url = Tournament.objects.filter().first().score_json_url


            with urllib.request.urlopen(json_url) as field_json_url:
              data = json.loads(field_json_url.read().decode())

            ranks = {}

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

            finished = data['leaderboard']['is_finished']
            ranks['finished']=finished
            print ('finished = ' + str(finished))


            for row in data["leaderboard"]['players']:
                last_name = row['player_bio']['last_name'].replace(', Jr.', '')
                first_name = row['player_bio']['first_name']
                player = (first_name + ' ' + last_name)
                if (row["current_position"] is '' and round in (2,3,4)) or row["status"] == "wd":
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
                    rank = row["current_position"]
                    score = format_score(row["total"])
                    today_score = format_score(row["today"])
                    if today_score == 'not started':
                        thru = ''
                    else:
                        thru = row['thru']
                    sod_position = row["start_position"]

                ranks[player] = rank, score, today_score, thru, sod_position

            #print (ranks)
            return ranks

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


calc_score()
