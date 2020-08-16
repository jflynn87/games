import urllib.request
import json
from golf_app.models import Picks, Tournament, TotalScore, BonusDetails, ScoreDetails, PickMethod, \
    Group, Field
from django.contrib.auth.models import User
import csv
#from golf_app import calc_score
from golf_app import utils
from datetime import datetime
from django.db.models import Count, Max, Min
from django.db import transaction
import random


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


    def get_picks_by_user(self):
        det_picks = {}
        sd = ScoreDetails.objects.filter(pick__playerName__tournament=self.tournament).order_by('pick__user', 'pick__playerName__group')

        for user in sd.values('user').distinct():
            if self.format == "json":
                user = User.objects.get(pk=user.get('user'))
                det_picks[user.username]={}
            else:
                det_picks[User.objects.get(pk=user.get('user'))]=[]

        for pick in sd:
            if self.format == 'json':
               if pick.pick.is_winner():
                   winner = 'red'
               else:
                   winner = 'black'

               det_picks[pick.user.username][pick.pick.playerName.group.number]=\
                   {
                   'pick': pick.pick.playerName.playerName,
                   'score': pick.score,
                   'toPar': pick.toPar,
                   'today_score': pick.today_score,
                   'thru': pick.thru,
                   'sod_position': pick.sod_position,
                   'winner': winner
                    }
            else:
                det_picks[pick.user].append(pick)



        if self.format == 'json':
            return json.dumps(det_picks)
        else:
            return det_picks


    # def get_score_file(self, file='round.csv'):
    #     #print ('start get_score_file', datetime.now())
    #     score_dict = {}
    #     try:
    #         driver = Chrome()
    #         url = "https://www.pgatour.com/leaderboard.html"
    #         driver.get(url)
    #         table = driver.find_elements_by_class_name("leaderboard-table")
    
    #         for t in table:
    #             for tr in t.find_elements_by_tag_name('tr'):
    #                 #for td in tr.find_elements_by_tag_name('td'):
    #                     print (len(tr), tr)
    #     except Exception as e:
    #         print ('scrape failed', e)
    #         with open(file, encoding="utf8") as csv_file:
    #             csv_reader = csv.reader(csv_file, delimiter=',')
    #             #for r in csv_reader:
    #             #    print (r)
    #             for row in csv_reader:
    #                 try:
    #                     #print (row)
    #                     if row[3] != '':
    #                         score_dict[row[3]] = {'rank': row[0], 'thru': row[5], 'total_score': row[4], 'r1': row[7], 'r2': row[8], 'r3': row[9], 'r4': row[10]}
                    
    #                     else:
    #                         print ('round.csv file read failed', row, e)
    #                 except Exception as e:
    #                     pass

    #     finally:
    #         driver.quit()


    #    return score_dict
        
    @transaction.atomic
    def update_scores(self):
        print ('start update_scores', datetime.now())
        print (self.score_dict)
        print ('round', self.get_round())
        print ('update scores dict end')
        for pick in Picks.objects.filter(playerName__tournament=self.tournament):
            try:
                if self.score_dict.get(pick.playerName.playerName).get('rank') == "CUT":
                    pick.score = self.get_cut_num()
                elif self.score_dict.get(pick.playerName.playerName).get('rank') == "WD":
                    pick.score = self.get_wd_score(pick)
                else:
                    if int(utils.formatRank(self.score_dict.get(pick.playerName.playerName).get('rank'))) > self.get_cut_num():
                        pick.score=self.get_cut_num()
                    else:
                        pick.score = utils.formatRank(self.score_dict.get(pick.playerName.playerName).get('rank'))
                
                pick.save()
                        
                sd, sd_created = ScoreDetails.objects.get_or_create(user=pick.user, pick=pick)
                sd.score=pick.score
                if self.score_dict.get(pick.playerName.playerName).get('rank') == "CUT" or \
                    self.score_dict.get(pick.playerName.playerName).get('rank') == "WD" and self.get_round() < 3:
                    sd.today_score  = "CUT"
                    sd.thru  = "CUT"
                elif self.score_dict.get(pick.playerName.playerName).get('rank') == "WD":
                    sd.today_score = "WD"
                    sd.thru = "WD"
                else:
                    sd.today_score = self.score_dict.get(pick.playerName.playerName).get('round_score')
                    sd.thru  = self.score_dict.get(pick.playerName.playerName).get('thru')
                sd.toPar = self.score_dict.get(pick.playerName.playerName).get('total_score')
                sd.sod_position = self.score_dict.get(pick.playerName.playerName).get('change')
                sd.save()
            except Exception as e:
                print ('withdraw?', pick, e)
                pick.score  = self.get_cut_num()
                pick.save()
                sd, sd_created = ScoreDetails.objects.get_or_create(user=pick.user, pick=pick)
                sd.score=pick.score
                sd.today_score = "WD"
                sd.thru = "WD"
                sd.save()

            self.tournament.score_update_time = datetime.now()
            if not self.tournament.complete:
                self.tournament.complete = self.tournament_complete()
            self.tournament.save()

            if pick.is_winner() and not PickMethod.objects.filter(user=pick.user, method=3, tournament=pick.playerName.tournament).exists():
                print ('winner', pick.playerName)
                bd, created = BonusDetails.objects.get_or_create(user=pick.user, tournament=pick.playerName.tournament)
                bd.winner_bonus = 50 + (pick.playerName.group.number*2)
                bd.save()

        print ('end update_scores', datetime.now())
        return


    @transaction.atomic
    def total_scores(self):
        print ('start total_scores', datetime.now())
       
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
                    'cut_bonus': bd.cut_bonus} 
            sorted_ts_dict = sorted(ts_dict.items(), key=lambda v: v[1].get('total_score'))
            return json.dumps(dict(sorted_ts_dict))
       
        
        TotalScore.objects.filter(tournament=self.tournament).delete()
        for pick in ScoreDetails.objects.filter(pick__playerName__tournament=self.tournament):
            ts, created = TotalScore.objects.get_or_create(user=pick.user, tournament=pick.pick.playerName.tournament)
            if created:
                ts.score = pick.score
                ts.cut_count = 0
            else:
                ts.score = utils.formatRank(ts.score) + utils.formatRank(pick.score)
            if pick.thru in self.not_playing_list:
                ts.cut_count +=1            

            ts.save()
            
            if PickMethod.objects.filter(tournament=self.tournament, user=ts.user, method='3').exists():
                message = "- missed pick deadline (no bonuses)"
            else:
                message = ''

            ts_dict[ts.user.username] = {'total_score': ts.score, 'cuts': ts.cut_count, 'msg': message}

        print (ts_dict)
        if self.tournament.complete:
            for total in TotalScore.objects.filter(tournament=self.tournament):
                try:
                    bd = BonusDetails.objects.get(tournament=total.tournament, user=total.user)
                    total.score -= bd.winner_bonus
                    total.score -= bd.cut_bonus
                    total.save()
                except Exception as e:
                    print (total.user, 'bonus detail issue ', e)

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
            ts_dict[ts.user.username].update({'total_score': ts.score, 'winner_bonus': bd.winner_bonus, 'major_bonus': bd.major_bonus, 'cut_bonus': bd.cut_bonus})

        
        sorted_ts_dict = sorted(ts_dict.items(), key=lambda v: v[1].get('total_score'))
        print ('end total_scores', datetime.now())
        return json.dumps(dict(sorted_ts_dict))


    def winner_bonus(self):
        for pick in Picks.objects.filter(playerName__tournament=self.tournament):
            if pick.is_winner():
                bd, created = BonusDetails.objects.get_or_create(user=pick.user, tournament=pick.playerName.tournament)
                bd.winner_bonus = 50 + (pick.playerName.group.number*2)
                bd.save()

            
    def get_round(self):
        round = 0
        if self.tournament.complete:
            return 4
        
        for stats in self.score_dict.values():
            print (stats)
            if len(stats.get('thru')) > 3:
                #print ('len', stats)
                continue
            if stats.get('thru')[0] != "F" and stats.get('rank') not in self.not_playing_list:
                if stats.get('r1')  == '--':
                    return 1
                if stats.get('r2') == '--':
                   return 2
                elif stats.get('r3') == '--':
                       return 3
                elif  stats.get('r4') == '--':
                       print ('get round - round 4')
                       return 4
            elif stats.get('thru')[0] == 'F' and stats.get('rank') not in self.not_playing_list:
                if stats.get('r2') == '--':
                    return 2
                elif stats.get('r3') == '--':
                    return 3
                elif stats.get('r4') == '--':
                    return 4
                else:
                    return 4
            else:
                return 0
        print ('exit get_round', round)
        return round


    def get_cut_num(self):
    
        if not self.tournament.has_cut:
            return len([x for x in self.score_dict.values() if x['rank'] not in ['WD']]) + 1
        round = self.get_cut_round()
        #round = self.get_round()
        #after cut WD's
        #commented for rerun, but do i need the if here?  should not get here normally for old tournament?
        #if self.tournament.current:  wd = len([x for x in self.score_dict.values() if x['rank'] == 'WD' and x['r'+str(round+1)] != '--']) 
        
        ##Not working if WD is before cut
        wd = len([x for x in self.score_dict.values() if x['rank'] == 'WD' and x['r'+str(round+1)] != '--']) 
        
        for v in self.score_dict.values():
            if v['rank'] == "CUT":
                return len([x for x in self.score_dict.values() if x['rank'] not in ['CUT', 'WD']]) + wd + 1
        if self.get_round() != 4 and len(self.score_dict.values()) >65:
            return 66
        else:
            return len([x for x in self.score_dict.values() if x['rank'] not in ['CUT','WD']]) + wd + 1


    def get_leader(self):
        leader_dict = {}
        leader_list = []        
        for golfer, stats in self.score_dict.items():
           #print ('ld', golfer, stats)
           if stats['rank'] in ['1', 'T1', 1]:
               leader_list.append(golfer)

               leader_dict= {'leaders': leader_list, 'score': stats['total_score']}
           else:
               pass

        if len(leader_dict.keys()) > 0:
            print ('leaders exist', leader_dict)
            self.tournament.leaders = json.dumps(leader_dict)
            self.tournament.save()
            #leader_dict['leaders'] = (leader_dict)
            return json.dumps(leader_dict)
        else:
            print ('no leader, going to db', self.tournament.leaders)
            if self.tournament.leaders != None:
                return self.tournament.leaders
            else: return json.dumps('')

    def tournament_complete(self):
        for v in self.score_dict.values():
            if (v['rank'] not in self.not_playing_list and \
                v['r4'] == "--") or v['rank']  == "T1":
                return False
        if self.get_round() == 4: 
            return True

    def get_wd_score(self, pick):
        score = self.score_dict.get(pick.playerName.playerName)
        print ('wd lookup', score)

        if not self.tournament.has_cut:
            return len([x for x in self.score_dict.values() if x['rank'] not in self.not_playing_list]) + 1
        
        if score.get('r1') =='--' or score.get('r2') == '--' or score.get('r3') == '--':
                print ('didnt get to r3')
                return self.get_cut_num()
        elif score.get('r3') != '--' and self.get_cut_round() < 3:
                return len([x for x in self.score_dict.values() if x['rank'] not in self.not_playing_list]) + 1
        elif score.get('r4') == '--' and self.get_cut_round() < 4:
            return self.get_cut_round()
        else:
            return len([x for x in self.score_dict.values() if x['rank'] not in self.not_playing_list]) + 1


    def get_cut_round(self):
        for data in self.score_dict.values():
            if data.get('rank') == "CUT":
                if data['r3'] == '--':
                    return 2
                elif data['r4'] == "--": 
                    return 3
        return 2

    
    def optimal_picks(self):

        optimal_dict = {}
       
        for group in Group.objects.filter(tournament=self.tournament):
           group_cuts = 0
           golfer_list = []
           group_min = group.min_score()
           print ('group: ', group, 'min', group_min)

           for player in Field.objects.filter(tournament=self.tournament, group=group):
               if player.playerName in self.score_dict.keys():  #needed to deal wiht WD's before start of tourn.
                    #print (player.playerName, self.score_dict[player.playerName]['rank'])
                    if self.score_dict[player.playerName]['rank'] not in  self.not_playing_list and  \
                       int(utils.formatRank(self.score_dict[player.playerName]['rank'])) == group_min:
                        golfer_list.append(player.playerName)
                        #score_list[str(player)] = int(calc_score.formatRank(str(self.score_dict[player.playerName]['rank'])))
                    else:
                        if self.score_dict[player.playerName]['rank'] in self.not_playing_list:
                            group_cuts += 1
               else:
                    print (player, 'mot in dict')

           optimal_dict[group.number] = {'golfer': golfer_list, 'rank': group_min, 'cuts': group_cuts, 'total_golfers': group.playerCnt}
           


           #cuts_dict[group] = group_cuts, group.playerCnt
           #scores[group]= score_list
           #score_list = {}
           #total_score = 0
 
        # if len(scores) != 0:
        #   for group, golfers in scores.items():
        #       print (type(group), golfers)
        #       try:
        #           leader = (min(golfers, key=golfers.get))
        #           total_score += golfers.get(leader)
        #           min_score[group.number] = \
        #               {'golfer': leader, 'rank': golfers.get(leader), 'cuts': cuts_dict.get(group)[0], 'total_golfers': cuts_dict.get(group)[1]}
        #       except Exception as e:
        #           print ('optimal scores exception', e)
        #           min_score[group.number] = "There was none!", None

        return json.dumps(optimal_dict)
        #return min_score, total_score, cuts_dict
        


