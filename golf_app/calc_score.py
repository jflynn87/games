import urllib3
from golf_app.models import Field, Tournament, Picks, Group, TotalScore, ScoreDetails
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect

def calc_score(request):
        '''takes in a request, caclulates and returns the score to the web site.
            Deletes all before starting'''

        TotalScore.objects.all().delete()
        ScoreDetails.objects.all().delete()
        scores = {}
        totalScore = 0
        cut_bonus = True
        winner_bonus = False

        picks = getPicks()
        ranks = getRanks()

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


        for player, picks in picks.items():
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
                    score_detail = ScoreDetails()
                    score_detail.user = player
                    score_detail.player = pick
                    score_detail.score = pickRank
                    score_detail.toPar = ranks[pick][1]
                    score_detail.today_score = ranks[pick][2]
                    score_detail.thru = ranks[pick][3]
                    score_detail.sod_position = ranks[pick][4]
                    score_detail.save()

                    if pickRank == 1 and ranks.get('finished'):
                        winner_bonus = True
                        totalScore -= 10
                        score_detail = ScoreDetails()
                        score_detail.user = player
                        score_detail.player = "Winner Bonus"
                        score_detail.score = -10
                        score_detail.save()

                except KeyError:
                    print (pick + ' lookup failed')
                    if ranks.get('round') == 1:
                        pickRank = 71
                    else:
                        pickRank = cutNum +1
                    cut_bonus = False
                    totalScore += pickRank
                    score_detail = ScoreDetails()
                    score_detail.user = player
                    score_detail.player = pick + " score not found"
                    score_detail.score = pickRank 
                    score_detail.toPar = "0"
                    score_detail.today_score = "0"
                    score_detail.thru = "0"
                    score_detail.sod_position = "0"
                    score_detail.save()


            if cut_bonus and ranks.get('round') >2:
                totalScore -= 10
                score_detail = ScoreDetails()
                score_detail.user = player
                score_detail.player = "No Cut Bonus"
                score_detail.score = -10
                score_detail.save()

            scores[player] = totalScore
            totalScore = 0
            winner_bonus = False
            cut_bonus = True




        for k, v in sorted(scores.items(), key=lambda x:x[1]):
            total_score = TotalScore()
            total_score.user = (k)
            player = User(request.user.id)
            total_score.score = int(v)
            total_score.save()


        display_scores = TotalScore.objects.all()
        display_detail = ScoreDetails.objects.all()

        return render(request, 'golf_app/scores.html', {'scores':display_scores,
                                                        'detail_list':display_detail,
                                                        'leader_list':leaders,
                                                        'cut_data':cut_data,

                                                        })


def getPicks():
            '''retrieves pick objects and returns a dictionary'''
            picks_dict = {}
            pick_list = []

            users = User.objects.all()

            for user in User.objects.all():
                if Picks.objects.filter(user=user):
                    for pick in Picks.objects.filter(user=user):
                        pick_list.append(str(pick.playerName))
                    picks_dict[str(user)] = pick_list
                    pick_list = []

            return (picks_dict)


def getRanks():
            '''takes no input. goes to the PGA web site and pulls back json file of tournament ranking/scores'''

            import urllib.request
            import json

            json_url = Tournament.objects.filter().first().score_json_url


            with urllib.request.urlopen(json_url) as field_json_url:
              data = json.loads(field_json_url.read().decode())

            ranks = {}


            if data['leaderboard']['cut_line']['paid_players_making_cut'] == None:
                ranks['cut number']=Field.objects.count()
                print ("cut num = " + str(ranks))
            else:
                cut_section = data['leaderboard']['cut_line']
                cut_players = cut_section["cut_count"]
                ranks['cut number']=cut_players

            if data['leaderboard']['cut_line']['paid_players_making_cut'] == None:
                cut_score = None
                cut_state = "No cut this week"
            else:
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
