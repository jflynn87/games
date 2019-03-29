import urllib3
from golf_app.models import Field, Tournament, Picks, Group, TotalScore, ScoreDetails, BonusDetails, mpScores
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Sum, Q
import datetime
from django.db import transaction
import urllib
import json

@transaction.atomic
def mp_calc_scores(tournament, request=None):
    '''takes a tournament object and option request and returns a dict.  used to calculate
    scores for match play format tournaments'''
    json_url = tournament.score_json_url
    print (json_url)

    with urllib.request.urlopen(json_url) as field_json_url:
        data = json.loads(field_json_url.read().decode())

    field = data['rounds']
    #print (field)

    round = 1
    cur_round = data.get('curRnd')
    round_status = data.get('curRndState')
    if round_status == 'Official':
        max_round = int(cur_round)
    else:
        max_round = int(cur_round) - 1

    print (round, max_round)
    while round <= max_round:
        print ('round', round)
        if mpScores.objects.filter(round=round).exists():
            print ('scores exist', round)
        else:
            i = 0
            print ('calculating scores', round)
            while i < 4:
                bracket = field[round-1].get('brackets')[i]
                print ("Bracket: ", bracket.get('bracketNum'), bracket.get('name'))
                j = 0
                while j < 8:
                    match_num = bracket.get('groups')[j].get('matchNum')
                    match_score = bracket.get('groups')[j].get('players')[0].get('finalMatchScr')

                    player_name =  bracket.get('groups')[j].get('players')[0].get('fName') + ' ' + bracket.get('groups')[j].get('players')[0].get('lName')
                    player_winner_flag = bracket.get('groups')[j].get('players')[0].get('matchWinner')

                    player2_name =  bracket.get('groups')[j].get('players')[1].get('fName') + ' ' + bracket.get('groups')[j].get('players')[1].get('lName')
                    player2_winner_flag = bracket.get('groups')[j].get('players')[1].get('matchWinner')
                    print (tournament)
                    player_names = []
                    player_names.append(player_name)
                    player_names.append(str(player_name) + ' ')
                    player_names.append(player2_name)
                    player_names.append(str(player2_name) + ' ')
                    #print (player_name, player2_name, len(Picks.objects.filter(playerName__tournament=tournament, playerName__playerName__in=player_names)))

                    for golfer in Field.objects.filter(tournament=tournament, playerName__in=player_names):

                        if golfer.playerName in [player_name, str(player_name + ' ')]:
                            score = mpScores()
                            score.bracket = bracket.get('bracketNum')
                            score.round = round
                            score.match_num = match_num
                            score.player = golfer
                            score.result = player_winner_flag
                            score.score = match_score
                            score.save()
                            print ('saving', golfer.playerName)
                        elif golfer.playerName in [player2_name, str(player2_name + ' ')]:
                            score2 = mpScores()
                            score2.bracket = bracket.get('bracketNum')
                            score2.round = round
                            score2.match_num = match_num
                            score2.player = golfer
                            score2.result = player2_winner_flag
                            score2.score = match_score
                            score2.save()
                            print ('saving', golfer.playerName)
                        else:
                            print ('in mp_calc else', golfer.playerName)

                    j +=1
                i += 1
#            else:
#             print (round, 'round already exists')

        round += 1

    return
