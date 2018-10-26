import urllib3
from golf_app.models import Field, Tournament, Picks, Group, TotalScore, ScoreDetails, BonusDetails
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist

def calc_score(t_args, request=None):
        '''takes in a request, caclulates and returns the score to the web site.
            Deletes all before starting'''

        #TotalScore.objects.all().delete()
        #ScoreDetails.objects.all().delete()
        scores = {}
        totalScore = 0
        cut_bonus = True
        winner_bonus = False
        picked_winner = False

        picks = getPicks(t_args)
        ranks = getRanks(t_args)

        if ranks.get('round') == 1:
            cutNum = 0
        else:
            if 'cut number' in ranks:
                cutNum = ranks.get('cut number')
            else:
                print ("no cut line")

        leaders = {}
        for player, rank in ranks.items():
            if player not in ('cut number', 'round', 'cut_status', 'finished'):
                if rank[0] in ('1', 'T1'):
                    leaders[player]=(rank[1])

        cut_data = {}
        if ranks.get('round') != 1:
            cut_info = ranks.get("cut_status")
            cut_data[cut_info[0]]=cut_info[1]

        lookup_errors_dict = {}
        display_detail = {}

        for player, picks in picks.items():
            user = User.objects.get(username=player)
            tournament = Tournament.objects.get(pk=t_args.get('pk'))
            lookup_errors_list = []
            display_list = []
            for pick in picks:
                try:
                    if ranks[pick][0] == 'cut':
                        cut_bonus = False
                        if ranks.get('round') == 1:
                            pickRank = 71
                        else:
                            pickRank = cutNum +1
                    elif ranks[pick][0]== '':
                        pickRank = 0

                    else:
                        pickRank_str = (formatRank(ranks[pick][0]))
                        pickRank = int(pickRank_str)
                        if ranks.get('round') == 1 and pickRank > 70:
                            pickRank = 71
                            cut_bonus = False
                        elif ranks.get('round') == 2 and pickRank >cutNum:
                            pickRank = cutNum +1
                            cut_bonus = False
                    totalScore += pickRank

                    #if ScoreDetails.objects.filter(user=user, pick__playerName__tournament=tournament, pick__playerName__playerName=pick).exists():
                    #print (user, pick, tournament)
                    pick_obj = Picks.objects.get(user=user, playerName__playerName=pick, playerName__tournament=tournament)
                    score_detail, created = ScoreDetails.objects.get_or_create(user=user, pick__playerName__tournament=tournament, pick=pick_obj)

                    #score_detail.user = user
                    #score_detail.pick = Picks.objects.get(user=user, playerName__playerName=pick)
                    score_detail.score = pickRank
                    score_detail.toPar = ranks[pick][1]
                    score_detail.today_score = ranks[pick][2]
                    score_detail.thru = ranks[pick][3]
                    score_detail.sod_position = ranks[pick][4]
                    score_detail.save()
                    display_list.append(score_detail)

                    if pickRank == 1 and ranks.get('finished'):
                        picked_winner = True
                        winner_group = pick_obj.playerName.group.number


                except (ObjectDoesNotExist, KeyError) as e:
                    print (pick + ' lookup failed', e)
                    lookup_errors_list.append(pick)
                    lookup_errors_dict[user]=lookup_errors_list

                    if ranks.get('round') == 1:
                        pickRank = 71
                    else:
                        pickRank = cutNum +1
                    cut_bonus = False
                    totalScore += pickRank


            base_bonus = 50

            if picked_winner:
                #picks_obj = Picks.objects.get(user=user, playerName__playerName=pick)
                #group = Field.objects.get(playerName=picks_obj.playerName)
                winner_bonus = base_bonus + (winner_group * 2)
                print ('winner bonus', winner_bonus)
                totalScore -= winner_bonus
            else:
                winner_bonus = 0

            if ranks.get('cut_status')[0] != "No cut this week":
                if cut_bonus and ranks.get('round') >2:
                    cut = base_bonus
                    totalScore -= cut
                else:
                    cut = 0
            else:
                cut = 0

            bonus_detail, created = BonusDetails.objects.get_or_create(user=user, tournament=tournament, winner_bonus=winner_bonus, cut_bonus=cut)
            display_list.append(bonus_detail)
            scores[user] = totalScore
            totalScore = 0
            picked_winner = False
            cut_bonus = True

            display_detail[user]=display_list

        for k, v in sorted(scores.items(), key=lambda x:x[1]):
            total_score, created = TotalScore.objects.get_or_create(user=User.objects.get(username=k), tournament=tournament)
            #total_score.user = User.objects.get(username=k)
            #player = User(request.user.id)
            print (total_score)
            total_score.score = int(v)
            total_score.save()


        display_scores = TotalScore.objects.filter(tournament=tournament).order_by('score')

        print ("scores dict:")
        print (display_detail)

        return display_scores, display_detail, leaders, cut_data, lookup_errors_dict


def getPicks(tournament):
            '''retrieves pick objects and returns a dictionary'''
            picks_dict = {}
            pick_list = []

            tournament = Tournament.objects.get(pk=tournament.get('pk'))
            users = User.objects.all()

            for user in User.objects.all():
                if Picks.objects.filter(user=user, playerName__tournament__name=tournament):
                    for pick in Picks.objects.filter(user=user, playerName__tournament__name=tournament).order_by('playerName__group__number'):
                        pick_list.append(str(pick.playerName))
                    picks_dict[str(user)] = pick_list
                    pick_list = []

            return (picks_dict)


def getRanks(tournament):
            '''takes no input. goes to the PGA web site and pulls back json file of tournament ranking/scores'''

            import urllib.request
            import json

            json_url = Tournament.objects.get(pk=tournament.get('pk')).score_json_url
            print (json_url)

            with urllib.request.urlopen(json_url) as field_json_url:
              data = json.loads(field_json_url.read().decode())

            ranks = {}

            if data['leaderboard']['cut_line']['paid_players_making_cut'] == None:
                ranks['cut number']=Field.objects.count()
                cut_score = None
                cut_state = "No cut this week"
                print ("cut num = " + str(ranks))
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

            finished = data['leaderboard']['is_finished']
            ranks['finished']=finished
            tournament = Tournament.objects.get(pk=tournament.get('pk'))
            if tournament.complete is False and finished:
                tournament.complete = True
                tournament.save()

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

            print (ranks)
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
