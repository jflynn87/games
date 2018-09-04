import httplib2
import os
import urllib3
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","golfProj.settings")

import django
django.setup()

from golf_app.models import Picks, Field
from django.contrib.auth.models import User

def getPicks():
    '''retrieves pick objects and returns a dictionary'''

    picks_dict = {}
    pick_list = []

    users = User.objects.all()

    for user in User.objects.all():
        for pick in Picks.objects.filter(user=user):
            pick_list.append(str(pick.playerName))
        picks_dict[str(user)] = pick_list
        pick_list = []

    return (picks_dict)


def getRanks():
    '''takes no input. goes to the PGA web site and pulls back json file of ranking'''

    import urllib.request
    import json

    try:
         f = open("config.txt", "r")
         for line in f:
             if "Score URL" in line:
                 json_url = line[12:]
                 print (json_url)
                 break

    except  Exception:
            print (e)

    with urllib.request.urlopen(json_url) as field_json_url:
      data = json.loads(field_json_url.read().decode())

    ranks = {}

    cut_section = data['leaderboard']['cut_line']
    cut_players = cut_section["cut_count"]
    ranks['cut number']=cut_players


    for row in data["leaderboard"]['players']:
        last_name = row['player_bio']['last_name'].replace(', Jr.', '')
        first_name = row['player_bio']['first_name']
        player = (first_name + ' ' + last_name)
        if row["current_position"] is '':
            rank = 'cut'
        else:
            rank = row["current_position"]
        ranks[player] = rank

    return ranks


def calcScores():

    scores = {}
    totalScore = 0

    picks = getPicks()
    ranks = getRanks()

    if 'cut number' in ranks:
        cutNum = ranks.get('cut number')
    else:
        print ("no cut line")


    for player, picks in picks.items():
        for pick in picks:
            try:
                if ranks[pick] == 'cut':
                    pickRank = cutNum +1
                else:
                    pickRank = (int(formatRank(ranks[pick])))
                totalScore += pickRank
                print (pick + '   '  + str (pickRank))
                scores[player] = pickRank
            except KeyError:
                print (pick + ' lookup failed')


        print (player + '   '  + str(totalScore))
        print ('--------------------------')
        scores[player] = totalScore
        totalScore = 0


    print(sorted(scores.items(), key=lambda x: x[1]))

def formatRank(rank):

    if rank[0] not in ('T', ''):
        return rank
    if rank[0] == 'T':
        return rank[1:]


#getRanks()
calcScores()
