import urllib.request
import json
from golf_app.models import Picks, Tournament, TotalScore, BonusDetails, ScoreDetails, PickMethod, \
    Group, Field, CountryPicks, Golfer
from django.contrib.auth.models import User
import csv
#from golf_app import calc_score
from golf_app import utils
from datetime import datetime, timezone
from django.db.models import Count, Max, Min, Sum
from django.db import transaction
import random
from unidecode import unidecode
#from django.utils import timezone
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

        #BonusDetails.objects.filter(tournament=self.tournament).update(best_in_group_bonus=0)
        BonusDetails.objects.filter(tournament=self.tournament, bonus_type='5').update(bonus_points=0)
        print ('starting pick loop time to here', datetime.now() - start)
        loop_start = datetime.now()

        for p in Picks.objects.filter(playerName__tournament=self.tournament).values('playerName').distinct():
            pick_loop_start = datetime.now()
            #print ('PICK ', p)
            pick = Picks.objects.filter(playerName__pk=p.get('playerName')).first()
            sd, sd_created = ScoreDetails.objects.get_or_create(user=pick.user, pick=pick)

            #if sd.filter(pick=pick, today_score__in=self.not_playing_list).exists() and self.score_dict.get('info').get('round') > 2: 
            try:
                temp = [x for x in self.score_dict.values() if x.get('pga_num') == pick.playerName.golfer.espn_number]
                #print ('temp', temp)
                data = temp[0] 
                #print ('data', data)
                #print ('SD: ', sd, sd.user, sd.gross_score, int(utils.formatRank(data.get('rank'))))
                
                if ScoreDetails.objects.filter(pick__playerName__tournament=self.tournament, pick__playerName__golfer__espn_number=pick.playerName.golfer.espn_number) \
                        .exclude(gross_score=utils.formatRank(data.get('rank')), thru=data.get('thru'), toPar=data.get('total_score')).count() == 0:
                            print ('skipping no change', pick.playerName, datetime.now() - pick_loop_start)
                            self.pick_bonuses(sd, pick, optimal_picks, data)
                            continue
               
                print ('thru skip checks')
                if data.get('rank') == "CUT":
                    score = cut_num + self.cut_penalty(pick)
                elif data.get('rank') in ["WD", "DQ"] or (data.get('rank') in self.cut_indicators and data.get('total_score') in ['WD', 'DQ']):
                    print ('WD/DQ: ', pick, data)
                    score = self.get_wd_score(pick) + self.cut_penalty(pick)
                else:
                    if self.tournament.has_cut and int(utils.formatRank(data.get('rank'))) > cut_num:
                         score=cut_num + self.cut_penalty(pick)
                    else:
                        score = utils.formatRank(data.get('rank')) 

                Picks.objects.filter(playerName__tournament=self.tournament, playerName=pick.playerName).update(score=score)

                #this doesn't work, only creates one SD record rater than all
                #sd, sd_created = ScoreDetails.objects.get_or_create(user=pick.user, pick=pick)
                
                sd.score = score - pick.playerName.handicap()
                
                sd.gross_score = pick.score
                if data.get('rank') == "CUT" or \
                    data.get('rank') in ["WD", 'DQ'] and curr_round < 3:
                    sd.today_score  = "CUT"
                    sd.thru  = "CUT"
                elif data.get('rank') in ["WD", 'DQ']:
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
                #sd.score=pick.score - pick.playerName.handicap() 
                sd.score=pick.score
                #sd.gross_score = score
                sd.gross_score = self.get_wd_score(pick)
                sd.today_score = "WD"
                sd.thru = "WD"
                sd.toPar = "WD"
                sd.sod_position = '-'
                #sd.save()   comment for bulk update
                ScoreDetails.objects.filter(pick__playerName__tournament=self.tournament, pick__playerName=pick.playerName).update(
                                            #score=cut_num - pick.playerName.handicap(),
                                            score=cut_num,
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

        self.tournament.score_update_time = datetime.timezone(timezone.utc) 
        self.tournament.save()
            
        print ('score loop duration', datetime.now() - loop_start)
        print ('update_scores duration', datetime.now() - start)
        return

    def pick_bonuses(self, sd, pick, optimal_picks, data):
        
        print ('bonuses: ', pick, data.get('rank'), 'complete: ', self.score_dict.get('info').get('complete'), type(data.get('rank')))
        winner_picked = False 
        playoff_loser_picked = False

        if self.score_dict.get('info').get('complete') and data.get('rank') in [str(1), 1]:
            print ('winner: ', pick)
            for winner in Picks.objects.filter(playerName=pick.playerName):
                if not PickMethod.objects.filter(user=winner.user, method=3, tournament=winner.playerName.tournament).exists():
                    #bd = BonusDetails.objects.get(user=winner.user, tournament=winner.playerName.tournament)
                    if self.tournament.pga_tournament_num == '999':
                        if winner.playerName.group.number > 5:
                            group = winner.playerName.group.number - 5
                        else:
                            group = winner.playerName.group.number
                        winner_bonus =  bd.winner_bonus + 50 + (group * 2)
                        if int(self.tournament.season.season) < 2022:
                            bd.winner_bonus = winner_bonus 
                        else:
                            bd, created = BonusDetails.objects.get_or_create(user=winner.user, tournament=winner.playerName.tournament, bonus_type='1')
                            bd.winner_bonus = 0  #just to be safe
                            #bd.bonus_type = '1'
                            bd.bonus_points = winner_bonus

                        bd.save()

                    else:
                        if int(self.tournament.season.season) < 2022:
                            BonusDetails.objects.filter(user=winner.user, tournament=winner.playerName.tournament).update(winner_bonus=50 + (winner.playerName.group.number * 2))
                        else:
                            bd, created = BonusDetails.objects.get_or_create(user=winner.user, tournament=winner.playerName.tournament, bonus_type='1')
                            bd.bonus_points = 50 + (winner.playerName.group.number * 2)
                            bd.save()
                            

                    winner_picked = True

                        
        if self.score_dict.get('info').get('complete') and self.score_dict.get('info').get('playoff') and data.get('rank') in [2, '2', 'T2']:
            print ('playoff', pick, pick.user)
            for loser in Picks.objects.filter(playerName=pick.playerName):
                if not PickMethod.objects.filter(user=loser.user, method=3, tournament=loser.playerName.tournament).exists():
                    if int(self.tournament.season.season) < 2022:
                        BonusDetails.objects.filter(user=loser.user, tournament=loser.playerName.tournament).update(playoff_bonus= 25)
                    else:
                        bd, created = BonusDetails.objects.get_or_create(user=loser.user, tournament=loser.playerName.tournament, bonus_type='4')
                        bd.bonus_points = 25
                        bd.save()
                    playoff_loser_picked = True
            
        if pick.playerName.golfer.espn_number in optimal_picks.get(str(pick.playerName.group.number)).get('golfer').keys():
            for best in Picks.objects.filter(playerName__golfer__espn_number=pick.playerName.golfer.espn_number, playerName__tournament=self.tournament):
                if not PickMethod.objects.filter(user=best.user, method=3, tournament=best.playerName.tournament).exists() \
                    and not winner_picked \
                    and not playoff_loser_picked \
                    and best.playerName.group.playerCnt > 4:
                        
                        #fix the >, reversed for testing
                        if int(self.tournament.season.season) < 2022:
                            bd = BonusDetails.objects.get(user=best.user, tournament=best.playerName.tournament)
                            bd.best_in_group_bonus = bd.best_in_group_bonus + 10
                            bd.save()
                        else:
                            big_bd, created = BonusDetails.objects.get_or_create(user=best.user, tournament=self.tournament, bonus_type='5')
                            #bd.best_in_group_bonus = 0  #just to be safe
                            big_bd.bonus_points += 10
                            big_bd.save()

        return


    def olympic_medals(self, user):
        print ('OLYMPIC MEDAL calcs', self.score_dict.get('info').get('mens_complete'), self.score_dict.get('info').get('womens_complete'))
        if self.score_dict.get('info').get('mens_complete'):
            gold_winner = [v.get('pga_num') for k,v in self.score_dict.items() if k != 'info' and v.get('rank') == 1 and v.get('gender') == 'men']
            print (gold_winner)
            gold_golfer = Golfer.objects.get(espn_number=gold_winner[0])
            if CountryPicks.objects.filter(country=gold_golfer.country(), user=user, gender='men').exists():
                c = CountryPicks.objects.get(user=user, country=gold_golfer.country(), gender='men')
                num_of_golfers = self.tournament.individual_country_count(gold_golfer.country(), 'men')
                c.score = 50 - (5* (num_of_golfers -1))
                
                c.save()
            silver_winner = [v.get('pga_num') for k,v in self.score_dict.items() if k != 'info' and v.get('rank') == 2 and v.get('gender') == 'men']
            silver_golfer = Golfer.objects.get(espn_number=silver_winner[0])
            if CountryPicks.objects.filter(country=silver_golfer.country(), user=user, gender='men').exists():
                c = CountryPicks.objects.get(user=user, country=silver_golfer.country(), gender='men')
                num_of_golfers = self.tournament.individual_country_count(silver_golfer.country(), 'men')
                c.score = 35 - (5* (num_of_golfers -1))

                c.save()
            bronze_winner = [v.get('pga_num') for k,v in self.score_dict.items() if k != 'info' and v.get('rank') == 2 and v.get('gender') == 'men']
            bronze_golfer = Golfer.objects.get(espn_number=bronze_winner[0])
            if CountryPicks.objects.filter(country=bronze_golfer.country(), user=user, gender='men').exists():
                c = CountryPicks.objects.get(user=user, country=bronze_golfer.country(), gender='men')
                num_of_golfers = self.tournament.individual_country_count(bronze_golfer.country(), 'men')
                c.score = 20 - (5* (num_of_golfers -1))

                c.save()
        print ('checkng women')
        if self.score_dict.get('info').get('womens_complete'):
            gold_winner = [v.get('pga_num') for k,v in self.score_dict.items() if k != 'info' and v.get('rank') == 1 and v.get('gender') == 'women']
            print ('women golf winner: ', gold_winner)
            gold_golfer = Golfer.objects.get(espn_number=gold_winner[0])
            print ('w gold winner: ', gold_golfer, gold_golfer.country())
            if CountryPicks.objects.filter(country=gold_golfer.country(), user=user, gender='woman').exists():
                c = CountryPicks.objects.get(user=user, country=gold_golfer.country(), gender='woman')
                num_of_golfers = self.tournament.individual_country_count(gold_golfer.country(), 'woman')
                c.score = 50 - (5* (num_of_golfers -1))
                c.save()
            silver_winner = [v.get('pga_num') for k,v in self.score_dict.items() if k != 'info' and v.get('rank') == 2 and v.get('gender') == 'women']
            silver_golfer = Golfer.objects.get(espn_number=silver_winner[0])
            print ('w silver winner: ', silver_golfer, silver_golfer.country())
            if CountryPicks.objects.filter(country=silver_golfer.country(), user=user, gender='woman').exists():
                c = CountryPicks.objects.get(user=user, country=silver_golfer.country(), gender='woman')
                num_of_golfers = self.tournament.individual_country_count(silver_golfer.country(), 'woman')
                c.score = 35 - (5* (num_of_golfers -1))

                c.save()
            bronze_winner = [v.get('pga_num') for k,v in self.score_dict.items() if k != 'info' and v.get('rank') == 3 and v.get('gender') == 'women']
            bronze_golfer = Golfer.objects.get(espn_number=bronze_winner[0])
            print ('w bronze winner: ', bronze_golfer, bronze_golfer.country())
            if CountryPicks.objects.filter(country=bronze_golfer.country(), user=user, gender='woman').exists():
                c = CountryPicks.objects.get(user=user, country=bronze_golfer.country(), gender='woman')
                num_of_golfers = self.tournament.individual_country_count(bronze_golfer.country(), 'woman')
                c.score = 20 - (5* (num_of_golfers -1))

                c.save()

        return


    @transaction.atomic
    def total_scores(self):
        start = datetime.now()
        print ('calc total scores')
        ts_dict = {}

        TotalScore.objects.filter(tournament=self.tournament).delete()

        for player in self.tournament.season.get_users():
            ts_loop_start = datetime.now()
            user = User.objects.get(pk=player.get('user'))
            ts_dict[user.username] = {}
            picks = Picks.objects.filter(playerName__tournament=self.tournament, user=user)
            gross_score = picks.aggregate(Sum('score'))
            handicap = picks.aggregate(Sum('playerName__handi'))
            #print ('total score debug', gross_score, handicap)
            net_score = gross_score.get('score__sum') - handicap.get('playerName__handi__sum')
            
            cuts = ScoreDetails.objects.filter(pick__playerName__tournament=self.tournament, pick__user=user, today_score__in=self.not_playing_list).count()
            #print ('player/score : ', player, gross_score, handicap, cuts) 
            ts, created = TotalScore.objects.get_or_create(user=user, tournament=self.tournament)
            ts.score = net_score
            ts.cut_count = cuts
            ts.save()

            if PickMethod.objects.filter(tournament=self.tournament, user=user, method=3).exists():
                ts_dict[user.username].update({'msg': "- missed pick deadline (no bonuses)",
                                                'cuts': cuts})
            else:
                ts_dict[user.username].update({'msg': "",
                                            'cuts': cuts})

                ## Individual Bonus calcs - overall bonuses below ##
                if cuts == 0 and len([v for (k,v) in self.score_dict.items() if k != 'info' and v.get('total_score') == "CUT"]) != 0:
                    print (player, 'no cut bonus')
                    post_cut_wd = len([v for k,v in self.score_dict.items() if k!= 'info' and v.get('total_score') in self.tournament.not_playing_list() and \
                        v.get('r3') != '--'])

                    cut_bonus = (len(self.score_dict) -1) - (len([k for k,v in self.score_dict.items() if k != 'info' and v.get('rank') not in self.tournament.not_playing_list()]) + post_cut_wd)
                    print (cut_bonus)
                    bd, created = BonusDetails.objects.get_or_create(tournament=self.tournament, user=user, bonus_type='2')
                    bd.bonus_points = cut_bonus
                    bd.save()

                    #do I need to relocate this 999 logic?
                    if self.tournament.pga_tournament_num == '999':
                        medals = self.olympic_medals(user)

                        medal_total = CountryPicks.objects.filter(user=ts.user).aggregate(Sum('score'))
                        if medal_total.get('score__sum'): #need to check for none since no picks for some
                           ts.score -= int(medal_total.get('score__sum'))
                           ts.save()

            #ts_dict[ts.user.username] = {'total_score': ts.score, 'cuts': ts.cut_count, 'msg': message}
            #print ('ts loop duration', datetime.now() - ts_loop_start)
            #print ('ts dict', ts_dict)

                if self.tournament.complete: 
                    if Field.objects.filter(tournament=self.tournament).count() > 70 and \
                                ScoreDetails.objects.filter(pick__playerName__tournament=self.tournament, gross_score=1, pick__user=user).exists() and \
                                ScoreDetails.objects.filter(pick__playerName__tournament=self.tournament, gross_score=2, pick__user=user).exists() and \
                                ScoreDetails.objects.filter(pick__playerName__tournament=self.tournament, gross_score__in=[1,2,3], pick__user=user).count() >= 3:
                                bd, created = BonusDetails.objects.get_or_create(user=user, tournament=self.tournament, bonus_type='6')
                                bd.bonus_points = 50
                                bd.save()

                    #tot_score, created = TotalScore.objects.get_or_create(tournament=self.tournament, user=user)
                    #print (tot_score, User.objects.get(pk=u.get('user')))
                for bd in BonusDetails.objects.filter(tournament=ts.tournament, user=user).exclude(bonus_type='3'):
                    ts.score -= bd.bonus_points
                    ts.save()
                        #ts_dict[tot_score.user.username].update({bd.get_bonus_type_display(): bd.bonus_points})
        #end player loop
        # start all scores calculated logic
        if self.tournament.complete:
            for u in self.tournament.season.get_users('obj'):
                if not PickMethod.objects.filter(tournament=self.tournament, user=u, method=3).exists() and \
                self.tournament.winning_picks(u):
                    print ('weekly winner ', u)
                    bd, created = BonusDetails.objects.get_or_create(user=u, tournament=self.tournament, bonus_type='3')
                    field_type = self.tournament.field_quality()
                    if field_type == 'weak':
                        bd.bonus_points = 50 / self.tournament.num_of_winners()
                    elif field_type == 'strong':
                        bd.bonus_points = 100 / self.tournament.num_of_winners()
                    elif field_type == 'major':
                        bd.bonus_points = 150 / self.tournament.num_of_winners()
                    else:
                        print ('no winner ', self.tournament.field_quality())
                    bd.save()
                    ts = TotalScore.objects.get(tournament=self.tournament, user=u)
                    ts.score -= bd.bonus_points
                    ts.save()
        
        for ts in TotalScore.objects.filter(tournament=self.tournament):
            for bonus in BonusDetails.objects.filter(user=ts.user, tournament=ts.tournament):
                ts_dict[ts.user.username].update({bonus.get_bonus_type_display(): bonus.bonus_points})
            ts_dict[ts.user.username].update({'handicap': ts.total_handicap(), 'total_score': ts.score})
            #ts_dict[ts.user.username].update({'total_score': ts.score, 'winner_bonus': bd.winner_bonus, 'major_bonus': bd.major_bonus, 'cut_bonus': bd.cut_bonus,
            # 'best_in_group': bd.best_in_group_bonus, 'playoff_bonus': bd.playoff_bonus, 'handicap': ts.total_handicap()})

        
        sorted_ts_dict = sorted(ts_dict.items(), key=lambda v: v[1].get('total_score'))
        print (ts_dict)
        print ('total_scores duration', datetime.now() - start)
        return json.dumps(dict(sorted_ts_dict))


    def cut_penalty(self, p):
        '''takes a pick obj and a score obj, returns an int'''
        if len([v for k,v in self.score_dict.items() if k != 'info' and v.get('rank') == 'CUT']) > 0:
            if p.playerName.group.number in [1, 2, 3]:
                cut_penalty = p.playerName.group.playerCnt - p.playerName.group.cut_count(self.score_dict) 
            else:
                cut_penalty = 0
        else:
            cut_penalty = 0

        return cut_penalty

    # def winner_bonus(self):
    #     for pick in Picks.objects.filter(playerName__tournament=self.tournament):
    #         if pick.is_winner():
    #             bd, created = BonusDetails.objects.get_or_create(user=pick.user, tournament=pick.playerName.tournament)
    #             if self.tournamanet.pga_tournament_num == '999' and pick.playerName.group.number > 5:
    #                 group = pick.playerName.group.number - 5
    #             else:
    #                 group = pick.playerName.group.number
    #             #bd.winner_bonus = 50 + (pick.playerName.group.number*2)
    #             bd.winner_bonus = 50 + (group*2)
    #             bd.save()
            

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
            return self.score_dict.get('info').get('cut_num') + self.cut_penalty(pick)
        elif len(d) ==0:
            #return self.tournament.saved_cut_num
            return self.score_dict.get('info').get('cut_num')
        
        print ('wd lookup', score)

        if not self.tournament.has_cut:
            return len([x for x in self.score_dict.values() if x.get('rank') not in self.not_playing_list]) 
        
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

