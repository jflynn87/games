import urllib3
from golf_app.models import Field, Tournament, Picks, Group, TotalScore, ScoreDetails, BonusDetails, mpScores, PickMethod
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Sum, Q
from datetime import datetime
from django.db import transaction
import urllib
import json
from golf_app.templatetags import golf_extras
from golf_app import utils

@transaction.atomic
def mp_calc_scores(tournament, request=None):
    '''takes a tournament object and option request and returns a dict.  used to calculate
    scores for match play format tournaments'''
    json_url = tournament.score_json_url
    print (json_url)

    with urllib.request.urlopen(json_url) as field_json_url:
        data = json.loads(field_json_url.read().decode())

    field = data['rounds']
    #print (field[3].get('roundNum'))

    round = 1
    cur_round = data.get('curRnd')

    round_status = data.get('curRndState')
    if round_status == 'Official':
        max_round = int(cur_round)
    else:
        max_round = int(cur_round) - 1

    print (round, max_round)

    #print (field[4].get('brackets')[2])
    #print ((field[6]))
    #print ((field[7]))

    #if int(cur_round) < 4:
    while round <= max_round:
        print ('round', round)
        #if round
        if mpScores.objects.filter(round=round).exists():
            print ('scores exist', round)
        else:
            i = 0
            print ('calculating scores', round)
            if round < 4:
                max_i = 4
            elif round == 4:
                max_i = 4
            elif round == 5:
                max_i = 4
            elif round == 6:
                max_i = 1
            elif round == 7:
                max_i = 2
            while i < max_i:
                if round < 4:
                    bracket = field[round-1].get('brackets')[i]
                else:
                    bracket = field[round].get('brackets')[i]
                print ("Bracket: ", bracket.get('bracketNum'), bracket.get('name'))
                j = 0
                if round < 4:
                    max_j = 8
                elif round == 4:
                    max_j = 2
                elif round == 5:
                    max_j = 1
                elif round == 6:
                    max_j = 2
                elif round == 7:
                    max_j =1
                else:  #need to update as i understand bracket format for last 8 and semis/final
                    max_j = 1
                print ('max j', max_j)
                while j < max_j:
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
        round += 1


# for round 1 results
    winners = {}
    winners_list = []
    for group in Group.objects.filter(tournament=tournament):
        player = golf_extras.leader(group.number)
        winners[group]=player
        winners_list.append(player[0])

    if ScoreDetails.objects.filter(pick__playerName__tournament=tournament).exists():
        ScoreDetails.objects.filter(pick__playerName__tournament=tournament).delete()
    for pick in Picks.objects.filter(playerName__tournament=tournament).order_by('user'):
        if pick.playerName.playerName in winners_list:
            #print ('winner', pick.user, pick.playerName.playerName)
            sd = ScoreDetails()
            sd.user = pick.user
            sd.pick = pick
            sd.score = 0
            sd.save()
        #elif str(pick.playerName.playerName) + ' ' in winners_list:
        #    print ('winner 1', pick.user, pick.playerName.playerName)
        else:
            sd = ScoreDetails()
            sd.user = pick.user
            sd.pick = pick
            sd.score = 17
            sd.save()
            #print ('not winner', pick.user, pick.playerName.playerName)

# for final 16 results
    r4_loser_list = mpScores.objects.filter(round=4, result="No").values('player__playerName')
    print (r4_loser_list)

    r5_loser_list = mpScores.objects.filter(round=5, result="No").values('player__playerName')
    print (r5_loser_list)

    finalist = mpScores.objects.filter(round=6.0, result="Yes")
    for player in finalist:
        if mpScores.objects.filter(player=player.player, round=7.0, result="Yes"):
            winner = player
        else:
            second_place = player

    consolation = mpScores.objects.filter(round=6.0, result="No")
    for player in consolation:
        if mpScores.objects.filter(player=player.player, round=7.0, result="Yes"):
            third_place = player
        else:
            forth_place = player


    #forth_place = mpScores.objects.filter(round=6.0, result="No").filter(round=7.0, result = "No")
    #third_place = mpScores.objects.filter(round=6.0, result="No").filter(round=7.0, result = "Yes")
    #second_place = mpScores.objects.filter(round=6.0, result="Yes").filter(round=7.0, result = "No")
    #winner = mpScores.objects.filter(round=6.0, result="Yes").filter(round=7.0, result = "Yes")

    print ('winner', winner)
    print ('2', second_place)
    print ('3', third_place)
    print ('4', forth_place)


    for pick in Picks.objects.filter(playerName__tournament=tournament):
        if r4_loser_list.filter(player__playerName=pick.playerName).exists():
            sd = ScoreDetails.objects.get(pick=pick)
            #sd.user = pick.user
            #sd.pick = pick
            sd.score = 9
            sd.save()

        if r5_loser_list.filter(player__playerName=pick.playerName).exists():
            sd = ScoreDetails.objects.get(pick=pick)
            #sd.user = pick.user
            #sd.pick = pick
            sd.score = 5
            sd.save()

        if forth_place.player.playerName == str(pick.playerName):
            sd = ScoreDetails.objects.get(pick=pick)
            #sd.user = pick.user
            #sd.pick = pick
            sd.score = 4
            sd.save()

        if third_place.player.playerName == str(pick.playerName):
            sd = ScoreDetails.objects.get(pick=pick)
            #sd.user = pick.user
            #sd.pick = pick
            sd.score = 3
            sd.save()

        if second_place.player.playerName == str(pick.playerName):
            sd = ScoreDetails.objects.get(pick=pick)
            #sd.user = pick.user
            #sd.pick = pick
            sd.score = 2
            sd.save()

        if winner.player.playerName == str(pick.playerName):
            sd = ScoreDetails.objects.get(pick=pick)
            #sd.user = pick.user
            #sd.pick = pick
            sd.score = 1
            sd.save()
            bd = BonusDetails.objects.get(user=sd.user, tournament=tournament)
            bd.winner_bonus = 50
            bd.save()


    score = ScoreDetails.objects.filter(pick__playerName__tournament=tournament).values('user_id').annotate(score=Sum('score'))
    #remaining = ScoreDetails.objects.filter(pick__playerName__tournament=tournament, score=0).values('user').annotate(playing=Count('pick'))

    for sd in score:
        user = User.objects.get(pk=sd.get('user_id'))
        bd, created = BonusDetails.objects.get_or_create(user=user, tournament=tournament)
        if created:
            bd.winner_bonus = 0
            bd.cut_bonus = 0
            bd.save()
        ts, created = TotalScore.objects.get_or_create(user=user, tournament=tournament)
        ts.score = sd.get('score') - bd.winner_bonus

        ts.save()


    return


def espn_calc(sd):
    
    # if len(sd) == 64:
    #     round = 1
    # elif len(sd) == 17:
    #     round = 2
    # elif len(sd) == 9:
    #     round = 3
    # elif len(sd) == 5:
    #     round = 4
    # else:
    #     print ('MP calc scores score dict len not expected: ', len(sd))
    #     return 
    
    t = Tournament.objects.get(pga_tournament_num='470', season__current=True)
    if t.saved_round == 1:
        for p in Picks.objects.filter(Q(playerName__tournament=t) & (Q(score__isnull=True) |  Q(score=0))).values('playerName').distinct():
        #for p in Picks.objects.filter(playerName__tournament=t).values('playerName').distinct():
            print ('calc mp score loop', p)
            pick_loop_start = datetime.now()
            print (p)
            pick = Picks.objects.filter(playerName__pk=p.get('playerName')).first()
            #print ('ccc', pick.playerName.playerName)
            #d = utils.fix_name(pick.playerName.playerName, sd)
            #print ('mp scores pick lookup: ', p, d)
            print ('round: ', t.saved_round)
            if sd.get(pick.playerName.golfer.espn_number).get('pos') in ["1", "T1"]:
                score = 0
            else:
                score = 17
            Picks.objects.filter(playerName__tournament=t, playerName=pick.playerName).update(score=score)

            ScoreDetails.objects.filter(pick__playerName__tournament=t, pick__playerName=pick.playerName).update(
                                            score=score,
                                            gross_score=score,
                                            today_score=None,
                                            thru=None,
                                            toPar=None,
                                            sod_position=None
                                        )
    else:
        for round, matches in sd.items():
            print ('mp dict round: ', round)
            for match_num , match in matches.items():
                print ('mp match: ', match)
                if match.get('loser'):                
                    if Picks.objects.filter(playerName__tournament=t, playerName__playerName=match.get('loser')).exists():
                        pick = Picks.objects.filter(playerName__tournament=t, playerName__playerName=match.get('loser')).first()
                        if round == 'Round of 16':
                            score = 9
                        elif round == 'Quarterfinals':
                            score = 5
                        elif round == '3rd Place':
                            score = 4 
                        elif round == 'Finals':
                            score = 2
                        Picks.objects.filter(playerName__tournament=t, playerName=pick.playerName).update(score=score)

                        ScoreDetails.objects.filter(pick__playerName__tournament=t, pick__playerName=pick.playerName).update(
                                                score=score,
                                                gross_score=score,
                                                today_score=None,
                                                thru=None,
                                                toPar=None,
                                                sod_position=None
                                            )
                if round == 'Finals':
                    if Picks.objects.filter(playerName__tournament=t, playerName=match.get('winner')).exists():
                        pick = Picks.objects.filter(playerName__tournament=t, playerName=match.get('winner')).first()
                    
                        Picks.objects.filter(playerName__tournament=t, playerName=pick.playerName).update(score=1)

                        ScoreDetails.objects.filter(pick__playerName__tournament=t, pick__playerName=pick.playerName).update(
                                                score=1,
                                                gross_score=1,
                                                today_score=None,
                                                thru=None,
                                                toPar=None,
                                                sod_position=None
                                            )

                if round == '3rd Place':
                    if  Picks.objects.filter(playerName__tournament=t, playerName=match.get('winner')).exists():
                        pick = Picks.objects.filter(playerName__tournament=t, playerName=match.get('winner')).first()
                        Picks.objects.filter(playerName__tournament=t, playerName=pick.playerName).update(score=3)

                        ScoreDetails.objects.filter(pick__playerName__tournament=t, pick__playerName=pick.playerName).update(
                                                score=3,
                                                gross_score=3,
                                                today_score=None,
                                                thru=None,
                                                toPar=None,
                                                sod_position=None
                                            )

                

    return

def total_scores():
    start = datetime.now()
    t = Tournament.objects.get(pga_tournament_num='470', season__current=True)
    TotalScore.objects.filter(tournament=t).delete()
    ts_dict = {}

    for player in t.season.get_users():
        ts_loop_start = datetime.now()
        user = User.objects.get(pk=player.get('user'))
        picks = Picks.objects.filter(playerName__tournament=t, user=user)
        gross_score = picks.aggregate(Sum('score'))
        #handicap = picks.aggregate(Sum('playerName__handi'))
        #net_score = gross_score.get('score__sum') - handicap.get('playerName__handi__sum')
        net_score = gross_score.get('score__sum')
        cuts = ScoreDetails.objects.filter(pick__playerName__tournament=t, pick__user=user, today_score__in=t.not_playing_list()).count()
        print ('player/score : ', player, gross_score, cuts) 
        ts, created = TotalScore.objects.get_or_create(user=user, tournament=t)
        ts.score = net_score
        ts.cut_count = cuts

        ts.save()

        if PickMethod.objects.filter(tournament=t, user=user, method='3').exists():
            message = "- missed pick deadline (no bonuses)"
        else:
            message = ''


        ts_dict[ts.user.username] = {'total_score': ts.score, 'cuts': ts.cut_count, 'msg': message}
        print ('ts loop duration', datetime.now() - ts_loop_start)
    # if self.tournament.complete:
    #     if self.tournament.major: 
    #         winning_score = TotalScore.objects.filter(tournament=self.tournament).aggregate(Min('score'))
    #         print (winning_score)
    #         winner = TotalScore.objects.filter(tournament=self.tournament, score=winning_score.get('score__min'))
    #         print ('major', winner)
    #         for w in winner:
    #             if not PickMethod.objects.filter(tournament=self.tournament, user=w.user, method=3).exists():
    #                 bd, created = BonusDetails.objects.get_or_create(user=w.user, tournament=self.tournament)
    #                 bd.major_bonus = 100/self.tournament.num_of_winners()
    #                 w.score -= bd.major_bonus
    #                 bd.save()
    #                 w.save()
    
    # for ts in TotalScore.objects.filter(tournament=self.tournament):
    #     bd = BonusDetails.objects.get(tournament=ts.tournament, user=ts.user)
    #     ts_dict[ts.user.username].update({'total_score': ts.score, 'winner_bonus': bd.winner_bonus, 'major_bonus': bd.major_bonus, 'cut_bonus': bd.cut_bonus,
    #         'best_in_group': bd.best_in_group_bonus, 'playoff_bonus': bd.playoff_bonus, 'handicap': ts.total_handicap()})

    
    sorted_ts_dict = sorted(ts_dict.items(), key=lambda v: v[1].get('total_score'))
    print (ts_dict)
    print ('total_scores duration', datetime.now() - start)
    return json.dumps(dict(sorted_ts_dict))

