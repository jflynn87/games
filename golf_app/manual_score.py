import urllib.request
import json
from golf_app.models import Picks, Tournament, TotalScore, BonusDetails, ScoreDetails, PickMethod, \
    Group, Field
from django.contrib.auth.models import User
import csv
#from golf_app import calc_score
from golf_app import utils
from datetime import datetime
from django.db.models import Count, Max, Min, Sum
from django.db import transaction
import random
from unidecode import unidecode
from django.utils import timezone
from django.db.models import Q
from golf_app import golf_serializers
from django.http import JsonResponse

class Score(object):
    
    def __init__(self, score_dict, tournament, format=None):
    
        self.tournament = tournament
        #format to determine whether to return json or native django objects
        if format == None:
            self.format = 'object'
        else:
            self.format = format

        if score_dict != None:  
            self.score_dict = score_dict
        elif tournament.manual_score_file:
            score_dict = {}
            file = str(tournament.name) + ' score.csv'
            with open(file, encoding="utf8") as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    for row in csv_reader:
                        try:
                            name = row[3].split('(')[0].split(',')[0]
                            #print (name, len(name), name[len(name)-1])
                            if name != '':
                                if name[-1] == ' ':
                                   score_dict[name[:-1]] = {'total': row[0], 'status': row[5], 'score': row[4], 'r1': row[7], 'r2': row[8], 'r3': row[9], 'r4': row[10]}
                                else:
                                   score_dict[name] = {'total': row[0], 'status': row[5], 'score': row[4], 'r1': row[7], 'r2': row[8], 'r3': row[9], 'r4': row[10]}
                            else:
                                print ('round.csv file == psace', row)
                        except Exception as e:
                            print ('round.csv file read failed', row, e)

                    picks = manual_score.Score(score_dict, tournament)
                    picks.update_scores()
                    picks.total_scores()

        self.not_playing_list = ['CUT', 'WD', 'DQ']

        self.cut_indicators = ['--', '-', '_']


    def get_picks_by_user(self, user):
        '''takes a user object and returns that user's picks in a dict'''
        # replace with serialied sd object 5/7/2021

        det_picks = {}
        sd = ScoreDetails.objects.filter(pick__playerName__tournament=self.tournament, pick__user=user).order_by('pick__playerName__group')
        #print ('get pick by use sd', sd)

        #for user in sd.values('user').distinct():
        if self.format == "json":
                #user = User.objects.get(pk=user.get('user'))
                #det_picks[user.username]={}
                det_picks[user.username]={}
        else:
                det_picks[User.objects.get(pk=user.get('user'))]=[]

        for pick in sd:
            if self.format == 'json':
               if pick.pick.is_winner():
                   winner = 'red'
               else:
                   winner = 'black'
               if pick.pick.playerName.group.num_of_picks() == 1:
                   g = pick.pick.playerName.group.number
               else:
                   count = pick.pick.playerName.group.num_of_picks()
                   x = 1 
                   #print ('count', count, 'x', x)
                   while x <= count:
                       #if det_picks[pick.user.username].get(str(pick.pick.playerName.group.number) + '-' + str(x)) == None:
                       if det_picks[pick.user.username].get(str(pick.pick.playerName.group.number) + '-' + str(x)) == None:
                           g = str(pick.pick.playerName.group.number) + '-' + str(x)
                           break
                       else:
                           x += 1

              
               if pick.pick.playerName.partner:
                    player_name = pick.pick.playerName.playerName + ' ' + pick.pick.playerName.partner
               else:
                    player_name = pick.pick.playerName.playerName

               det_picks[pick.user.username][g]=\
                                {
                                'pick': player_name,
                                'pga_num': pick.pick.playerName.golfer.espn_number,
                                'score': pick.score,
                                'toPar': pick.toPar,
                                'today_score': pick.today_score,
                                'thru': pick.thru,
                                'sod_position': pick.sod_position,
                                'winner': winner,
                                'gross_score': pick.gross_score
                                }

            else:
                #det_picks[pick.pick.user.username].append(pick)
                det_picks[pick.user].append(pick)

        #print ('get picks result', det_picks)

        if self.format == 'json':
            #make json in the view so deleted the json.dumps
            return det_picks
        else:
            return det_picks




    #    return score_dict
        
    @transaction.atomic
    def update_scores(self, optimal_picks=None):
        start =  datetime.now()
        #print (self.score_dict)

        if self.tournament.complete:
            return

        cut_num = self.score_dict.get('info').get('cut_num')
        print ('after cut num', datetime.now() - start)
        if optimal_picks == None:
            optimal_picks = {}
            for g in Group.objects.filter(tournament=self.tournament):
                opt = self.optimal_picks(g.number)
                optimal_picks[str(g.number)] = {
                                                'golfer': opt[0],
                                                'rank': opt[1],
                                                'cuts': opt[2],
                                                'total_golfers': g.playerCnt
                } 
    
        print ('after optimal', datetime.now() - start)
        #print (optimal_picks)
        #curr_round = self.tournament.saved_round
        curr_round = self.score_dict.get('info').get('round')
        print ('after round', datetime.now() - start)

        BonusDetails.objects.filter(tournament=self.tournament).update(best_in_group_bonus=0)
        print ('starting pick loop time to here', datetime.now() - start)
        loop_start = datetime.now()

        for p in Picks.objects.filter(playerName__tournament=self.tournament).values('playerName').distinct():
            pick_loop_start = datetime.now()
            #print (p)
            pick = Picks.objects.filter(playerName__pk=p.get('playerName')).first()
            sd, sd_created = ScoreDetails.objects.get_or_create(user=pick.user, pick=pick)
            #if sd.filter(pick=pick, today_score__in=self.not_playing_list).exists() and self.score_dict.get('info').get('round') > 2: 
            try:
                temp = [x for x in self.score_dict.values() if x.get('pga_num') == pick.playerName.golfer.espn_number]
                #print ('temp', temp)
                data = temp[0] 
                #print ('data', data)
                
                if ScoreDetails.objects.filter(pick__playerName__tournament=self.tournament, pick__playerName__golfer__espn_number=pick.playerName.golfer.espn_number) \
                        .exclude(gross_score=utils.formatRank(data.get('rank')), thru=data.get('thru'), toPar=data.get('total_score')).count() == 0:
                            print ('skipping no change', pick.playerName, datetime.now() - pick_loop_start)
                            self.pick_bonuses(sd, pick, optimal_picks, data)
                            continue
               
                print ('thru skip checks')
                if data.get('rank') == "CUT":
                    score = cut_num
                elif data.get('rank') in ["WD", "DQ"] or (data.get('rank') in self.cut_indicators and data.get('total_score') in ['WD', 'DQ']):
                    print ('WD/DQ: ', pick, data)
                    score = self.get_wd_score(pick) 
                else:
                    if int(utils.formatRank(data.get('rank'))) > cut_num:
                         score=cut_num 
                    else:
                        score = utils.formatRank(data.get('rank')) 

                Picks.objects.filter(playerName__tournament=self.tournament, playerName=pick.playerName).update(score=score)

                #this doesn't work, only creates one SD record rater than all
                #sd, sd_created = ScoreDetails.objects.get_or_create(user=pick.user, pick=pick)
                
                sd.score = score - pick.playerName.handicap()
                
                sd.gross_score = pick.score
                if data.get('rank') == "CUT" or \
                    data.get('rank') == "WD" and curr_round < 3:
                    sd.today_score  = "CUT"
                    sd.thru  = "CUT"
                elif data.get('rank') == "WD":
                    sd.today_score = "WD"
                    sd.thru = "WD"
                else:
                    sd.today_score = data.get('round_score')
                    sd.thru  = data.get('thru')
                sd.toPar = data.get('total_score')
                sd.sod_position = data.get('change')

                ScoreDetails.objects.filter(pick__playerName__tournament=self.tournament, pick__playerName=pick.playerName).update(
                                            score=sd.score,
                                            gross_score=score,
                                            today_score=sd.today_score,
                                            thru=sd.thru,
                                            toPar=sd.toPar,
                                            sod_position=sd.sod_position
                                        )

            except Exception as e:
                #### fix this, doesn't work.
                print ('withdraw?', pick, e)
                pick.score  = cut_num
                #pick.save()
                Picks.objects.filter(playerName__tournament=self.tournament, playerName=pick.playerName).update(score=cut_num - pick.playerName.handicap())
                #sd, sd_created = ScoreDetails.objects.get_or_create(user=pick.user, pick=pick)
                sd.score=pick.score - pick.playerName.handicap() 
                #sd.gross_score = score
                sd.gross_score = self.get_wd_score(pick)
                sd.today_score = "WD"
                sd.thru = "WD"
                sd.toPar = "WD"
                sd.sod_position = '-'
                #sd.save()   comment for bulk update
                ScoreDetails.objects.filter(pick__playerName__tournament=self.tournament, pick__playerName=pick.playerName).update(
                                            score=cut_num - pick.playerName.handicap(),
                                            gross_score=sd.gross_score,
                                            today_score=sd.today_score,
                                            thru=sd.thru,
                                            sod_position=sd.sod_position,
                                            toPar=sd.toPar
                                            )
                data = {}

            self.pick_bonuses(sd, pick, optimal_picks, data)
            print ('pick loop: ', pick.playerName, ' ', Picks.objects.filter(playerName__pk=p.get('playerName')).count(), ' ', datetime.now() - pick_loop_start)
        ## end of bulk update section
        if self.score_dict.get('info').get('complete') == True:
            self.tournament.complete = True

        self.tournament.score_update_time = datetime.now(tz=timezone.utc) 
        self.tournament.save()
            
        print ('score loop duration', datetime.now() - loop_start)
        print ('update_scores duration', datetime.now() - start)
        return

    def pick_bonuses(self, sd, pick, optimal_picks, data):
        
        #d = [x for x in self.score_dict.values() if x.get('pga_num') == pick.playerName.golfer.espn_number][0]
        print (pick, data.get('rank'))
        winner = False 
        playoff_loser = False

        #if self.score_dict.get('info').get('complete') and sd.gross_score == 1:
        if self.score_dict.get('info').get('complete') and data.get('rank') == str(1):
            print ('winner: ', pick)
            for winner in Picks.objects.filter(playerName=pick.playerName):
                if not PickMethod.objects.filter(user=winner.user, method=3, tournament=winner.playerName.tournament).exists():
                    BonusDetails.objects.filter(user=winner.user, tournament=winner.playerName.tournament).update(winner_bonus=50 + (winner.playerName.group.number * 2))
                    winner = True

                        
        #if self.score_dict.get('info').get('complete') and self.score_dict.get('info').get('playoff') and utils.formatRank(sd.score) == 2:
        if self.score_dict.get('info').get('complete') and self.score_dict.get('info').get('playoff') and data.get('rank') in [2, '2', 'T2']:
            print ('playoff', pick, pick.user)
            for loser in Picks.objects.filter(playerName=pick.playerName):
                if not PickMethod.objects.filter(user=loser.user, method=3, tournament=loser.playerName.tournament).exists():
                    BonusDetails.objects.filter(user=loser.user, tournament=loser.playerName.tournament).update(playoff_bonus= 25)
                    playoff_loser = True
            
        if pick.playerName.golfer.espn_number in optimal_picks.get(str(pick.playerName.group.number)).get('golfer').keys():
            for best in Picks.objects.filter(playerName__golfer__espn_number=pick.playerName.golfer.espn_number):
                if not PickMethod.objects.filter(user=best.user, method=3, tournament=best.playerName.tournament).exists() \
                    and not winner \
                    and not playoff_loser \
                    and best.playerName.group.playerCnt > 4:
                        bd = BonusDetails.objects.get(user=best.user, tournament=best.playerName.tournament)
                        bd.best_in_group_bonus = bd.best_in_group_bonus + 10
                        bd.save()


        return
        


    @transaction.atomic
    def total_scores(self):
        start = datetime.now()
       
        ts_dict = {}

        if not self.tournament.current:
            for ts in TotalScore.objects.filter(tournament=self.tournament):
                if PickMethod.objects.filter(tournament=self.tournament, user=ts.user, method='3').exists():
                    message = "- missed pick deadline (no bonuses)"
                else:
                    message = ''
                try:
                    bd = BonusDetails.objects.get(user=ts.user, tournament=ts.tournament)    
                except Exception:
                    bd.winner_bonus = 0
                    bd.major_bonus = 0
                    bd.cut_bonus = 0
                ts_dict[ts.user.username] = {'total_score': ts.score, 'cuts': ts.cut_count, \
                    'msg': message, 'winner_bonus': bd.winner_bonus, 'major_bonus': bd.major_bonus, \
                    'cut_bonus': bd.cut_bonus, 'playoff_bonus': bd.playoff_bonus, \
                    'best_in_group': bd.best_in_group_bonus, 'handicap': ts.total_handicap()} 
            sorted_ts_dict = sorted(ts_dict.items(), key=lambda v: v[1].get('total_score'))
            return json.dumps(dict(sorted_ts_dict))
       
        
        TotalScore.objects.filter(tournament=self.tournament).delete()

        for player in self.tournament.season.get_users():
            ts_loop_start = datetime.now()
            user = User.objects.get(pk=player.get('user'))
            picks = Picks.objects.filter(playerName__tournament=self.tournament, user=user)
            gross_score = picks.aggregate(Sum('score'))
            handicap = picks.aggregate(Sum('playerName__handi'))
            print ('total score debug', gross_score, handicap)
            net_score = gross_score.get('score__sum') - handicap.get('playerName__handi__sum')
            cuts = ScoreDetails.objects.filter(pick__playerName__tournament=self.tournament, pick__user=user, today_score__in=self.not_playing_list).count()
            print ('player/score : ', player, gross_score, handicap, cuts) 
            ts, created = TotalScore.objects.get_or_create(user=user, tournament=self.tournament)
            ts.score = net_score
            ts.cut_count = cuts
            #ts.save()

            bd = BonusDetails.objects.get(tournament=self.tournament, user=user)
            ts.score -= bd.cut_bonus
            ts.score -= bd.best_in_group_bonus
            if self.tournament.complete: 
                ts.score -= bd.winner_bonus
                ts.score -= bd.cut_bonus
                #ts.score -= bd.best_in_group_bonus
                ts.score -= bd.playoff_bonus
                #ts.save()

            ts.save()

            if PickMethod.objects.filter(tournament=self.tournament, user=user, method='3').exists():
                message = "- missed pick deadline (no bonuses)"
            else:
                message = ''


            ts_dict[ts.user.username] = {'total_score': ts.score, 'cuts': ts.cut_count, 'msg': message}
            print ('ts loop duration', datetime.now() - ts_loop_start)
        if self.tournament.complete:
            if self.tournament.major: 
                winning_score = TotalScore.objects.filter(tournament=self.tournament).aggregate(Min('score'))
                print (winning_score)
                winner = TotalScore.objects.filter(tournament=self.tournament, score=winning_score.get('score__min'))
                print ('major', winner)
                for w in winner:
                    if not PickMethod.objects.filter(tournament=self.tournament, user=w.user, method=3).exists():
                        bd, created = BonusDetails.objects.get_or_create(user=w.user, tournament=self.tournament)
                        bd.major_bonus = 100/self.tournament.num_of_winners()
                        w.score -= bd.major_bonus
                        bd.save()
                        w.save()
        
        for ts in TotalScore.objects.filter(tournament=self.tournament):
            bd = BonusDetails.objects.get(tournament=ts.tournament, user=ts.user)
            ts_dict[ts.user.username].update({'total_score': ts.score, 'winner_bonus': bd.winner_bonus, 'major_bonus': bd.major_bonus, 'cut_bonus': bd.cut_bonus,
             'best_in_group': bd.best_in_group_bonus, 'playoff_bonus': bd.playoff_bonus, 'handicap': ts.total_handicap()})

        
        sorted_ts_dict = sorted(ts_dict.items(), key=lambda v: v[1].get('total_score'))
        print (ts_dict)
        print ('total_scores duration', datetime.now() - start)
        return json.dumps(dict(sorted_ts_dict))


    def winner_bonus(self):
        for pick in Picks.objects.filter(playerName__tournament=self.tournament):
            if pick.is_winner():
                bd, created = BonusDetails.objects.get_or_create(user=pick.user, tournament=pick.playerName.tournament)
                bd.winner_bonus = 50 + (pick.playerName.group.number*2)
                bd.save()
            

    def playoff_bonus(self):
        pass

    def no_cut_bonus(self):
        pass
   



    def get_leader(self):
        leader_dict = {}
        leader_list = []        
        for golfer, stats in self.score_dict.items():
           #print ('ld', golfer, stats)
           if stats.get('rank') in ['1', 'T1', 1]:
               leader_list.append(golfer)

               leader_dict= {'leaders': leader_list, 'score': stats['total_score']}
           else:
               pass

        if len(leader_dict.keys()) > 0:
            print ('leaders exist', leader_dict)
            self.tournament.leaders = json.dumps(leader_dict)
            #self.tournament.save()
            #leader_dict['leaders'] = (leader_dict)
            return json.dumps(leader_dict)
        else:
            print ('no leader, going to db', self.tournament.leaders)
            if self.tournament.leaders != None:
                return self.tournament.leaders
            else: return json.dumps('')


    def get_wd_score(self, pick):
        d = [v for v in self.score_dict.values() if v.get('pga_num') == pick.playerName.golfer.espn_number]
        print ('calc WD score: ', d)
        if len(d) > 0:
            score = d[0]
        elif len(d) == 0 and self.score_dict.get('info').get('cut_num') != None:
            return self.score_dict.get('info').get('cut_num')
        elif len(d) ==0:
            #return self.tournament.saved_cut_num
            return self.score_dict.get('info').get('cut_num')
        
        print ('wd lookup', score)

        if not self.tournament.has_cut:
            return len([x for x in self.score_dict.values() if x['rank'] not in self.not_playing_list]) + 1
        
        cut_indicators = ['--', '-', '_']

        if score.get('r1') in cut_indicators or score.get('r2') in cut_indicators or score.get('r3') in cut_indicators:
                print ('didnt get to r3')
                #return self.tournament.cut_num()
                #return self.tournament.saved_cut_num
                return self.score_dict.get('info').get('cut_num')
        elif score.get('r3') not in cut_indicators and self.tournament.get_cut_round() < 3:
                return len([x for (k,x) in self.score_dict.items() if k != 'info' and x['rank'] not in self.not_playing_list]) + 1
        # fix this if, retrun cut num?
        elif score.get('r4') in cut_indicators and self.tournament.get_cut_round() < 4:
            #return self.tournament.cut_num()
            #return self.tournament.saved_cut_num
            return self.score_dict.get('info').get('cut_num')
        else:
            return len([x for x in self.score_dict.values() if x['rank'] not in self.not_playing_list]) + 1

    def optimal_picks(self, group):
        '''takes an int group number, returns the best pick data as a tuple, including a dict of player name and numbers'''
        print ('optimal calc: ', group)
        best_score = min(utils.formatRank(x.get('rank')) - x.get('handicap') for k, x in self.score_dict.items() if k != 'info' and x.get('group') == group) 
        best_list = {v['pga_num']:k for (k,v) in self.score_dict.items() if v.get('group') == group and utils.formatRank(v.get('rank')) - v.get('handicap') == best_score}
        cuts = len([v for v in self.score_dict.values() if v.get('group') == group and v.get('rank') in self.not_playing_list])
        print ('best: ', best_list, best_score, cuts)
        return best_list, best_score, cuts


    def worst_picks(self, group):
        '''takes an int group number, returns the worsr pick data as a tuple, including a dict of player name and numbers'''
        print ('worst picks calc: ', group)
        worst_score = max(utils.formatRank(x.get('rank')) - x.get('handicap') for k, x in self.score_dict.items() if k != 'info' and x.get('group') == group) 
        worst_list = {v['pga_num']:k for (k,v) in self.score_dict.items() if v.get('group') == group and utils.formatRank(v.get('rank')) - v.get('handicap') == worst_score}
        #cuts = len([v for v in self.score_dict.values() if v.get('group') == group and v.get('rank') in self.not_playing_list])
        print ('worst: ', worst_list, worst_score)
        return worst_list, worst_score


    def worst_picks_score(self, group):
        '''takes an int group number, returns the worsr pick data as a tuple, including a dict of player name and numbers'''
        print ('worst picks calc: ', group)
        dnp = ['-', '--']
        pre_cut_wd = {v['pga_num']:k for k, v in self.score_dict.items() if k != 'info' and v.get('group') == group and v.get('total_score') in ['WD', 'DQ'] and v.get('r3') in dnp}
        print ('pre cut', pre_cut_wd)
        if pre_cut_wd:
            return pre_cut_wd, None
        worst_score = max(x.get('tot_strokes') for k, x in self.score_dict.items() if k != 'info' and x.get('group') == group and x.get('total_score') in self.tournament.not_playing_list())
            
        worst_list = {v['pga_num']:k for (k,v) in self.score_dict.items() if v.get('group') == group and v.get('tot_strokes') == worst_score}
        #cuts = len([v for v in self.score_dict.values() if v.get('group') == group and v.get('rank') in self.not_playing_list])
        print ('worst: ', worst_list, worst_score)
        return worst_list, worst_score


    def best_in_group(self, pick, optimal_picks):
        '''takes a pick object and optimal_picks dict, updates bd and returns nothing'''
        start = datetime.now()
        if pick.playerName.golfer.espn_number in optimal_picks.get(str(pick.playerName.group.number)).get('golfer').keys():
            for best in Picks.objects.filter(playerName__golfer__espn_number=pick.playerName.golfer.espn_number):
                if not PickMethod.objects.filter(user=best.user, method=3, tournament=best.playerName.tournament).exists() \
                    and not pick.is_winner() \
                    and not pick.playoff_loser() \
                    and best.playerName.group.playerCnt > 4:
                        bd = BonusDetails.objects.get(user=best.user, tournament=best.playerName.tournament)
                        bd.best_in_group_bonus = bd.best_in_group_bonus + 10
                        bd.save()
        #print ('best in group duration: ', datetime.now()-start)
        return 



#### Adding below to try to calc one player at a time

    #@transaction.atomic
    def update_scores_player(self, user, optimal_picks=None):
        '''takes a user object and calcs score per pick for user.  returns nothing'''
        start =  datetime.now()
        #print (self.score_dict)
        
        ### commented for testing, ucomment 
        #if self.tournament.complete:
        #    return

        cut_num = self.score_dict.get('info').get('cut_num')
        
        if optimal_picks == None:
            optimal_picks = {}
            for g in Group.objects.filter(tournament=self.tournament):
                opt = self.optimal_picks(g.number)
                optimal_picks[str(g.number)] = {
                                                'golfer': opt[0],
                                                'rank': opt[1],
                                                'cuts': opt[2],
                                                'total_golfers': g.playerCnt
                } 
    
        print ('after optimal', datetime.now() - start)
        #print (optimal_picks)
        #curr_round = self.tournament.saved_round
        curr_round = self.score_dict.get('info').get('round')
        print ('after round', datetime.now() - start)

        BonusDetails.objects.filter(tournament=self.tournament).update(best_in_group_bonus=0)
        print ('starting pick loop time to here', datetime.now() - start)
        loop_start = datetime.now()

        for p in Picks.objects.filter(playerName__tournament=self.tournament).values('playerName').distinct():
            pick_loop_start = datetime.now()
            #print (p)
            pick = Picks.objects.filter(playerName__pk=p.get('playerName')).first()
            sd, sd_created = ScoreDetails.objects.get_or_create(user=pick.user, pick=pick)

            try:
                temp = [x for x in self.score_dict.values() if x.get('pga_num') == pick.playerName.golfer.espn_number]
                data = temp[0] 
                
                if ScoreDetails.objects.filter(pick__playerName__tournament=self.tournament, pick__playerName__golfer__espn_number=pick.playerName.golfer.espn_number) \
                        .exclude(gross_score=utils.formatRank(data.get('rank')), thru=data.get('thru'), toPar=data.get('total_score')).count() == 0 \
                        or (sd.today_score in self.not_playing_list and self.score_dict.get('info').get('round') > self.tournament.saved_cut_round): 
                            print ('skipping no change', pick.playerName, datetime.now() - pick_loop_start)
                            if self.score_dict.get('info').get('complete'):
                                self.pick_bonuses(sd, pick, optimal_picks, data)
                            continue
                
                print ('thru skip checks')
                if data.get('rank') == "CUT":
                    score = cut_num
                elif data.get('rank') == "WD":
                    score = self.get_wd_score(pick) 
                else:
                    if int(utils.formatRank(data.get('rank'))) > cut_num:
                         score=cut_num 
                    else:
                        score = utils.formatRank(data.get('rank')) 

                Picks.objects.filter(playerName__tournament=self.tournament, playerName=pick.playerName).update(score=score)

                sd.score=score - pick.playerName.handicap()
                
                sd.gross_score = pick.score
                if data.get('rank') == "CUT" or \
                    data.get('rank') == "WD" and curr_round < 3:
                    sd.today_score  = "CUT"
                    sd.thru  = "CUT"
                elif data.get('rank') == "WD":
                    sd.today_score = "WD"
                    sd.thru = "WD"
                else:
                    sd.today_score = data.get('round_score')
                    sd.thru  = data.get('thru')
                sd.toPar = data.get('total_score')
                sd.sod_position = data.get('change')

                ScoreDetails.objects.filter(pick__playerName__tournament=self.tournament, pick__playerName=pick.playerName).update(
                                            score=sd.score,
                                            gross_score=score,
                                            today_score=sd.today_score,
                                            thru=sd.thru,
                                            toPar=sd.toPar,
                                            sod_position=sd.sod_position
                                        )

            except Exception as e:
                print ('withdraw?', pick, e)
                pick.score  = cut_num
                Picks.objects.filter(playerName__tournament=self.tournament, playerName=pick.playerName).update(score=cut_num - pick.playerName.handicap())
                sd.score=pick.score - pick.playerName.handicap() 
                sd.gross_score = self.get_wd_score(pick)
                sd.today_score = "WD"
                sd.thru = "WD"
                sd.toPar = "WD"
                ScoreDetails.objects.filter(pick__playerName__tournament=self.tournament, pick__playerName=pick.playerName).update(
                                            score=cut_num - pick.playerName.handicap(),
                                            gross_score=sd.gross_score,
                                            today_score=sd.today_score,
                                            thru=sd.thru,
                                            toPar=sd.toPar
                                            )
            self.pick_bonuses(sd, pick, optimal_picks,data)
            print ('pick loop: ', pick.playerName, ' ', Picks.objects.filter(playerName__pk=p.get('playerName')).count(), ' ', datetime.now() - pick_loop_start)
        ## end of bulk update section
        if self.score_dict.get('info').get('complete') == True:
            self.tournament.complete = True

        self.tournament.score_update_time = datetime.now(tz=timezone.utc)  
        self.tournament.save()
            
        print ('score loop duration', datetime.now() - loop_start)
        print ('update_scores duration', datetime.now() - start)
        return


    @transaction.atomic
    def player_total_score(self, user):
        start = datetime.now()
       
        ts_dict = {}

        if not self.tournament.current:
            for ts in TotalScore.objects.filter(tournament=self.tournament, user=user):
                if PickMethod.objects.filter(tournament=self.tournament, user=ts.user, method='3').exists():
                    message = "- missed pick deadline (no bonuses)"
                else:
                    message = ''
                try:
                    bd = BonusDetails.objects.get(user=ts.user, tournament=ts.tournament)    
                except Exception:
                    bd.winner_bonus = 0
                    bd.major_bonus = 0
                    bd.cut_bonus = 0
                ts_dict[ts.user.username] = {'total_score': ts.score, 'cuts': ts.cut_count, \
                    'msg': message, 'winner_bonus': bd.winner_bonus, 'major_bonus': bd.major_bonus, \
                    'cut_bonus': bd.cut_bonus, 'playoff_bonus': bd.playoff_bonus, \
                    'best_in_group': bd.best_in_group_bonus, 'handicap': ts.total_handicap()} 
            #sorted_ts_dict = sorted(ts_dict.items(), key=lambda v: v[1].get('total_score'))
            return json.dumps(dict(sorted_ts_dict))
       
        
        TotalScore.objects.filter(tournament=self.tournament, user=user).delete()

        #for player in self.tournament.season.get_users():
        #    ts_loop_start = datetime.now()
        #    user = User.objects.get(pk=player.get('user'))
        picks = Picks.objects.filter(playerName__tournament=self.tournament, user=user)
        gross_score = picks.aggregate(Sum('score'))
        handicap = picks.aggregate(Sum('playerName__handi'))
        net_score = gross_score.get('score__sum') - handicap.get('playerName__handi__sum')
        cuts = ScoreDetails.objects.filter(pick__playerName__tournament=self.tournament, pick__user=user, today_score__in=self.not_playing_list).count()
        print ('player/score : ', user, gross_score, handicap, cuts) 
        ts, created = TotalScore.objects.get_or_create(user=user, tournament=self.tournament)
        ts.score = net_score
        ts.cut_count = cuts
        
        bd = BonusDetails.objects.get(tournament=self.tournament, user=user)
        ts.score -= bd.cut_bonus
        ts.score -= bd.best_in_group_bonus
        if self.tournament.complete: 
            ts.score -= bd.winner_bonus
            ts.score -= bd.cut_bonus
            #ts.score -= bd.best_in_group_bonus
            ts.score -= bd.playoff_bonus
            #ts.save()

        ts.save()

        if PickMethod.objects.filter(tournament=self.tournament, user=user, method='3').exists():
            message = "- missed pick deadline (no bonuses)"
        else:
            message = ''


        ts_dict[ts.user.username] = {'total_score': ts.score, 'cuts': ts.cut_count, 'msg': message}
        #print ('ts loop duration', datetime.now() - ts_loop_start)
        if self.tournament.complete:
            if self.tournament.major: 
                winning_score = TotalScore.objects.filter(tournament=self.tournament).aggregate(Min('score'))
                print (winning_score)
                winner = TotalScore.objects.filter(tournament=self.tournament, score=winning_score.get('score__min'))
                print ('major', winner)
                for w in winner:
                    if not PickMethod.objects.filter(tournament=self.tournament, user=w.user, method=3).exists():
                        bd, created = BonusDetails.objects.get_or_create(user=w.user, tournament=self.tournament)
                        bd.major_bonus = 100/self.tournament.num_of_winners()
                        w.score -= bd.major_bonus
                        bd.save()
                        w.save()
        
        for ts in TotalScore.objects.filter(tournament=self.tournament, user=ts.user):
            bd = BonusDetails.objects.get(tournament=ts.tournament, user=ts.user)
            ts_dict[ts.user.username].update({'total_score': ts.score, 'winner_bonus': bd.winner_bonus, 'major_bonus': bd.major_bonus, 'cut_bonus': bd.cut_bonus,
             'best_in_group': bd.best_in_group_bonus, 'playoff_bonus': bd.playoff_bonus, 'handicap': ts.total_handicap()})

        
        #sorted_ts_dict = sorted(ts_dict.items(), key=lambda v: v[1].get('total_score'))
        print (ts_dict)
        print ('total_scores duration', datetime.now() - start)
        return json.dumps(ts_dict)
