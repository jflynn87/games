import urllib3
from golf_app.models import Field, Tournament, Picks, Group, TotalScore, \
                    ScoreDetails, BonusDetails, PickMethod
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Sum, Q, Min
import datetime
#import scipy.stats as ss

def calc_score(t_args, request=None):
        '''takes in a request, caclulates and returns the score to the web site.
            Deletes all before starting'''
        #print('running calc scores')
        scores = {}
        totalScore = 0
        cut_bonus = True
        winner_bonus = False
        picked_winner = False
        ranks_start_time = datetime.datetime.now()
        ranks_tuple = getRanks(t_args)
        if ranks_tuple[0] == "score lookup fail":
            # pga lookup failed, so return
            return None, None, None, None, {'pga score file error': ranks_tuple[1]}, None

        ranks_end_time = datetime.datetime.now()
        print ('build ranks dict', ranks_end_time - ranks_start_time)

        picks_dict_start_time = datetime.datetime.now()
        picks_dict = getPicks(t_args, ranks_tuple[0])
        picks_dict_end_time = datetime.datetime.now()
        print ('build picks dict', picks_dict_end_time - picks_dict_start_time)
        #print ('tuple', ranks_tuple)
        ranks = ranks_tuple[0]
        lookup_errors = ranks_tuple[1]
        cutNum = getCutNum(ranks)
        #print ('test', cutNum)

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
        tournament = Tournament.objects.get(pk=t_args.get('pk'))
        before_score_start_time = datetime.datetime.now()
        print ('before for loops', before_score_start_time - ranks_end_time)
        pick_dict_loop_start = datetime.datetime.now()

        if not tournament.complete:
            print ('check', len(ranks))
            base_bonus = 50
            try:
                if ranks['cut_status'][0] == "Projected":
                    total_scores = ScoreDetails.objects.filter(pick__playerName__tournament=tournament).values('user').annotate(Sum('score'))\
                     .annotate(cuts=Count('score', filter=Q(score__gt=ranks['cut number'])))
                else:
                    total_scores = ScoreDetails.objects.filter(pick__playerName__tournament=tournament).values('user').annotate(Sum('score')).annotate(cuts=Count('today_score', filter=Q(today_score="cut")))
            except Exception as e:
                print ('total score exception')
                total_scores = ScoreDetails.objects.filter(pick__playerName__tournament=tournament).values('user').annotate(Sum('score')).annotate(cuts=Count('today_score', filter=Q(today_score="cut")))

            print(total_scores)
            for s in total_scores:
                if s.get('cuts')==2:
                    print(s)

            if ranks.get('cut_status')[0] == "Actual" \
             and int(ranks.get('round')) >  1:
                 for s in total_scores:
                    if s.get('cuts')==0 and not \
                      PickMethod.objects.filter(user=s.get('user'), tournament=tournament, method='3').exists():
                        print ('creating bons detail cut')
                        bd, created = BonusDetails.objects.get_or_create(user__pk=s.get('user'), tournament=tournament)
                        #bd.cut_bonus = base_bonus
                        bd.cut_bonus = len(ranks) - getCutNum()
                        bd.save()
                    # if bad data leads to incorrect bonus detail, this should clean up automatically
                    if BonusDetails.objects.filter(user__pk=s.get('user'), tournament=tournament, cut_bonus__gt=0).exists() \
                     and s.get('cuts') > 0:
                        print ('corercting bonus details-cut')
                        bd = BonusDetails.objects.get(user__pk=s.get('user'), tournament=tournament, cut_bonus__gt=0)
                        bd.cut_bonus = 0
                        bd.save()
            # add elif to deal with bad data in round 2, before cut is set back to actual?


            for score in total_scores:
                print ('score', score, type(score.get('user')),tournament, ranks.get('finished'))
                user = User.objects.get(pk=score.get('user'))
                #cut_bonus = 0
                winner_bonus = 0

#                if PickMethod.objects.filter(user__id=score.get('user'), tournament=tournament, method='3').exists():
#                    print ('exists', score, PickMethod.objects.filter(user__id=score.get('user'), tournament=tournament, method='3'))

                # just try to get the top rank person for testing, belongs in the if below once it works
                #ranks = ss.rankdata(total_score_list, method='min')
                #print (type(total_scores), total_scores)
                #print ('ranks', total_scores(Min('score__sum')))

                if ranks.get('finished') and ScoreDetails.objects.filter(pick__playerName__tournament=tournament, user=user, score=1) \
                  and not PickMethod.objects.filter(user__id=score.get('user'), tournament=tournament, method='3').exists():
                        group = ScoreDetails.objects.get(pick__playerName__tournament=tournament, user=user, score=1)
                        group_number = (group.pick.playerName.group.number)
                        winner_bonus = base_bonus + (2 * group_number)

                bd, created = BonusDetails.objects.get_or_create(user=user, tournament=tournament)
                bd.winner_bonus = winner_bonus

                if ranks.get('finished') and tournament.major and tournament.winning_picks(User.objects.get(id=score.get('user'))):
                    print (user, 'major winner')
                    bd.major_bonus = 100
                if created:
                    bd.cut_bonus = 0
                    bd.major_bonus = 0

                bd.save()

                ts, created = TotalScore.objects.get_or_create(tournament=tournament, user=user)
                ts.score = score.get('score__sum') - (bd.winner_bonus + bd.cut_bonus + bd.major_bonus)
                ts.cut_count = score.get('cuts')
                ts.save()
        display_scores = TotalScore.objects.filter(tournament=tournament).order_by('score')


        sorted_scores = {}
        if request:
            if not request.user.is_authenticated:
                #print ('debug setup A', request)
                sorted_list = []
                for score in TotalScore.objects.filter(tournament=tournament).order_by('score'):
                    for sd in ScoreDetails.objects.filter(user=score.user, pick__playerName__tournament=tournament):
                        sorted_list.append(sd)
                    bd, created = BonusDetails.objects.get_or_create(user=score.user, tournament=tournament)
                    sorted_list.append(bd)
                    user= User.objects.get(pk=score.user.pk)

                    sorted_scores[user]= sorted_list
                    sorted_list = []
            else:
                #print ('debug setup', request)
                sorted_list = []
                for s in ScoreDetails.objects.filter(user=request.user, pick__playerName__tournament=tournament):
                    sorted_list.append(s)
                bd, created = BonusDetails.objects.get_or_create(user=request.user, tournament=tournament)
                sorted_list.append(bd)
                user = User.objects.get(pk=request.user.pk)
                sorted_scores[user]=sorted_list
                for score in TotalScore.objects.filter(tournament=tournament).exclude(user=request.user).order_by('score'):
                    sorted_list = []
                    for sd in ScoreDetails.objects.filter(user=score.user, pick__playerName__tournament=tournament):
                        sorted_list.append(sd)
                    bd, created = BonusDetails.objects.get_or_create(user=score.user, tournament=tournament)
                    sorted_list.append(bd)
                    sorted_scores[score.user]= sorted_list

        #print ('sortd scores', sorted_scores)
        #print ('display det', display_detail)
        if tournament.complete is False and ranks.get('finished') == True:
            tournament.complete = True
            tournament.save()
        #print ('return time', datetime.datetime.now() - before_display_time)
        #return display_scores, display_detail, leaders, cut_data, lookup_errors_dict
        return display_scores, sorted_scores, leaders, cut_data, lookup_errors_dict, ranks


def getPicks(tournament, ranks):
            '''retrieves pick objects and returns a dictionary'''
            picks_dict = {}
            pick_list = []
            cut_num = getCutNum(ranks)

            tournament = Tournament.objects.get(pk=tournament.get('pk'))

            if Picks.objects.filter(playerName__tournament=tournament) and tournament.current:
                for pick in Picks.objects.filter(playerName__tournament=tournament).order_by('playerName__group__number'):
                        golfer = pick.playerName.playerName
                        pick_list.append(str(pick.playerName))
                        sd = sd, created = ScoreDetails.objects.get_or_create(user=pick.user, pick=pick)
                        try:
                            if ranks[golfer][0] in ('cut', 'wd'):
                                #print ('cut/wd', ranks[golfer][0], pick.playerName.playerName)
                                sd.score = cut_num + 1
                            elif ranks[golfer][0] == 'mdf':
                                if ranks[golfer][1] == 'even':
                                    rank = '0'
                                else:
                                    rank = str(ranks[golfer][1])
                                    print ('rank type', type(rank))
                                sd.score = ((get_mdf_rank(int(formatRank(rank)), ranks)))
                            else:
                                sd.score=formatRank(str(ranks[golfer][0]))
                            sd.toPar = ranks[golfer][1]
                            sd.today_score = ranks[golfer][2]
                            sd.thru = ranks[golfer][3]
                            sd.sod_position = ranks[golfer][4]
                            sd.save()
                        except Exception as e:
                            print ('pick not in ranks dict', pick, e)
                            sd.score = cut_num + 1
                            sd.today_score = "WD"
                            sd.save()


                picks_dict[str(pick.user)] = pick_list
                pick_list = []

            return (picks_dict)


def getRanks(tournament):
            '''takes a dict with a touenamnet number. goes to the PGA web site and pulls back json file of tournament ranking/scores'''

            import urllib.request
            import json
            #print (tournament.get('pk'))
            json_url = Tournament.objects.get(pk=tournament.get('pk')).score_json_url
            print ('calc scores', json_url)

            try:
                with urllib.request.urlopen(json_url) as field_json_url:
                    data = json.loads(field_json_url.read().decode())
            except Exception as e:
                print ('score json lookup error', e)
                if Tournament.objects.get(pk=tournament.get('pk')).started():
                    print ('started add score here')
                else:
                    return "score lookup fail", e

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
                if (row["current_position"] == '' and round in (2,3,4)) and row['status'] != 'mdf' or row["status"] == "wd":
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
                        #print(score)
                        rank = 'mdf'  #calc score in the picks sect once ranks dict is complete
                        sod_position = row["start_position"]
                        today_score = "mdf"
                    else:
                        if ranks['round'] == 1:
                            score = formatRank(row['current_position'])
                            if int(score) > 70:
                                rank = '71'
                            else:
                                rank = row["current_position"]
                        else:
                            #print (row['player_bio']['last_name'], row['current_position'])
                            if int(formatRank(row['current_position'])) > int(ranks['cut number']):
                                rank = int(ranks['cut number']) + 1
                            else:
                                rank = row["current_position"]
                            #print (row['player_bio']['last_name'], int(formatRank(rank)))
                        score = format_score(row["total"])
                        today_score = format_score(row["today"])
                    if today_score == 'not started':
                        thru = ''
                    else:
                        thru = row['thru']
                    sod_position = row["start_position"]

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

            print ('calc_score.getRanks()', ranks, lookup_errors)
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

    if type(rank) is int:
        return rank
    elif rank in  ['', '--', None]:
       return 0
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

def get_mdf_rank(score, ranks):
    '''takes an int score and a dict of ranks and calulates to rank for an mdf'''
    mdf_rank = 0
    for k,v in ranks.items():
        if k not in ('cut number', 'round', 'cut_status', 'finished'):
            if v[1] == 'even':
                golfer_score = 0
            else:
                golfer_score = v[1]
            if v[0] != 'cut' and (int(golfer_score) < score or v[0] != "mdf"):
                mdf_rank += 1
    return mdf_rank + 1
