import urllib.request
import json
from golf_app.models import Picks, Tournament, TotalScore, BonusDetails, ScoreDetails, PickMethod, \
    Group, Field
from django.contrib.auth.models import User
import csv
from golf_app import calc_score
from datetime import datetime
from django.db.models import Count, Max
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
#        else:
#            self.score_dict = self.get_picks_by_user()



    ## don't use this, use the models.py function
    def confirm_all_pics(self):
        print ('checking picks')

        if self.tournament.started():
            t = Tournament.objects.filter(season__current=True).earliest('pk')
            c=  len(Picks.objects.filter(playerName__tournament=t).values('user').annotate(unum=Count('user')))
            expected_picks = Group.objects.filter(tournament=self.tournament).aggregate(Max('number'))
            print ('expected', expected_picks, expected_picks['number__max'] * c)
            print ('actual', Picks.objects.filter(playerName__tournament=self.tournament).count() - expected_picks['number__max'] * c)
            if Picks.objects.filter(playerName__tournament=self.tournament).count() \
            == (expected_picks.get('number__max') * c):
                print ('equal')
            elif (expected_picks.get('number__max') - Picks.objects.filter(playerName__tournament=self.tournament).count()) \
            % expected_picks.get('number__max') == 0:
                print ('missing full picks')
                #using first tournament, should update to use league
                for user in TotalScore.objects.filter(tournament=t).values('user__username'):
                    if not Picks.objects.filter(playerName__tournament=self.tournament, \
                    user=User.objects.get(username=user.get('user__username'))).exists():
                        print (user.get('user__username'), 'no picks so submit random')
                        self.create_picks(self.tournament, User.objects.get(username=user.get('user__username')))
            else:
                print ('missing individual picks')
            
            return

    ## don't use this, use the models.py function
    @transaction.atomic
    def create_picks(self, tournament, user):
        '''takes tournament and user objects and generates random picks.  check for duplication with general pick submit class'''

        for group in Group.objects.filter(tournament=tournament):
            pick = Picks()
            random_picks = random.choice(Field.objects.filter(tournament=tournament, group=group, withdrawn=False))
            pick.playerName = Field.objects.get(playerName=random_picks.playerName, tournament=tournament)
            pick.user = user
            pick.save()

        pm = PickMethod()
        pm.user = user
        pm.tournament = tournament
        pm.method = '3'
        pm.save()

        return


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
            #print (pick)
            #pick.refresh_from_db()
            #print (pick)
            if self.format == 'json':
               #det_picks[pick.user.username]= {'group': pick.pick.playerName.group.number} 
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


    def get_score_file(self, file='round.csv'):
        #print ('start get_score_file', datetime.now())
        score_dict = {}
        try:
            driver = Chrome()
            url = "https://www.pgatour.com/leaderboard.html"
            driver.get(url)
            table = driver.find_elements_by_class_name("leaderboard-table")
    
            for t in table:
                for tr in t.find_elements_by_tag_name('tr'):
                    #for td in tr.find_elements_by_tag_name('td'):
                        print (len(tr), tr)
        except Exception as e:
            print ('scrape failed', e)
            with open(file, encoding="utf8") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                #for r in csv_reader:
                #    print (r)
                for row in csv_reader:
                    try:
                        #print (row)
                        if row[3] != '':
                            score_dict[row[3]] = {'rank': row[0], 'thru': row[5], 'total_score': row[4], 'r1': row[7], 'r2': row[8], 'r3': row[9], 'r4': row[10]}
                    
                        else:
                            print ('round.csv file read failed', row, e)
                    except Exception as e:
                        pass

        finally:
            driver.quit()


        return score_dict
        
    @transaction.atomic
    def update_scores(self):
        print ('start update_scores', datetime.now())
        #print (self.score_dict)
        print ('update scores dict end')
        for pick in Picks.objects.filter(playerName__tournament=self.tournament):
            print (pick.playerName.playerName, self.score_dict.get(pick.playerName.playerName))
            try:
                if self.score_dict.get(pick.playerName.playerName).get('rank') == "CUT" or \
                    (self.score_dict.get(pick.playerName.playerName).get('rank') == "WD" and \
                    self.get_round() < 3):
                    pick.score = self.get_cut_num()
                elif self.score_dict.get(pick.playerName.playerName).get('rank') == "WD" and \
                    self.get_round() > 2:
                    pick.score = self.get_cut_num() -1
                else:
                    if int(calc_score.formatRank(self.score_dict.get(pick.playerName.playerName).get('rank'))) > self.get_cut_num():
                        pick.score=self.get_cut_num()
                    else:
                        pick.score = calc_score.formatRank(self.score_dict.get(pick.playerName.playerName).get('rank'))
                
                pick.save()
                        
                sd, sd_created = ScoreDetails.objects.get_or_create(user=pick.user, pick=pick)
                sd.score=pick.score
                #print (self.score_dict.get(pick.playerName.playerName).get('rank'))
                if self.score_dict.get(pick.playerName.playerName).get('rank') == "CUT" or \
                    self.score_dict.get(pick.playerName.playerName).get('rank') == "WD" and self.get_round() < 3:
                    #sd.today_score  = self.score_dict.get(pick.playerName.playerName).get('today_score')
                    sd.today_score  = "CUT"
                    sd.thru  = "CUT"
                elif self.score_dict.get(pick.playerName.playerName).get('rank') == "WD":
                    sd.today_score = "WD"
                    sd.thru = "WD"
                else:
                    #sd.today_score = self.score_dict.get(pick.playerName.playerName).get('r' + str(self.get_round()-1))
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


            if pick.is_winner() and not PickMethod.objects.filter(method=3).exists():
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
        #ts_dict['totals'] = {}
        TotalScore.objects.filter(tournament=self.tournament).delete()
        #for pick in Picks.objects.filter(playerName__tournament=self.tournament):
        for pick in ScoreDetails.objects.filter(pick__playerName__tournament=self.tournament):
            ts, created = TotalScore.objects.get_or_create(user=pick.user, tournament=pick.pick.playerName.tournament)
            if created:
                ts.score = pick.score
                ts.cut_count = 0
            else:
              #  print (pick, ts.score, pick.score)
                ts.score = calc_score.formatRank(ts.score) + calc_score.formatRank(pick.score)

            #if self.score_dict.get(pick.pick.playerName.playerName).get('rank') in ["CUT", "WD"] or \
            if pick.thru in ["CUT", "WD"]:
                ts.cut_count +=1            
            
            #print (pick, pick.is_winner())
            if pick.pick.is_winner():
                print ('winner', pick)
                bd = BonusDetails.objects.get(tournament=self.tournament, user=pick.user)
                bd.winner_bonus = 50 + (2*pick.pick.playerName.group.number)
                bd.save()
                ts.score -= bd.winner_bonus
                ts.save()

            ts.save()
            
            if PickMethod.objects.filter(tournament=self.tournament, user=ts.user, method='3').exists():
                message = "- missed pick deadline (no bonuses)"
            else:
                message = ''


            ts_dict[ts.user.username + message] = {'total_score': ts.score, 'cuts': ts.cut_count}

        print ('end total_scores', datetime.now())
        sorted_ts_dict = sorted(ts_dict.items(), key=lambda v: v[1].get('total_score'))
        
        return json.dumps(dict(sorted_ts_dict))


    def winner_bonus(self):
        for pick in Picks.objects.filter(playerName__tournament=self.tournament):
            if pick.is_winner():
                bd, created = BonusDetails.objects.get_or_create(user=pick.user, tournament=pick.playerName.tournament)
                bd.winner_bonus = 50 + (pick.playerName.group.number*2)
                bd.save()

            
    def get_round(self):
        round = 0
        for stats in self.score_dict.values():
            if stats.get('thru')[0] != "F" and stats.get('rank') not in ('CUT', 'WD'):
               if stats.get('r2') == '--':
                  return 2
               elif stats.get('r3') != '--':
                      return 3
               elif  stats.get('r4') == '--':
                      return 4
            else:
                if round == 0:
                    if stats.get('r1') == '--':
                        round = 1
                    elif stats.get('r2') == '--':
                        round = 2
                    elif stats.get('r3') == '--':
                        round = 3
                    elif stats.get('r4') == '--':
                        round = 4
                    else:
                        round = 4
        return round
               

    def get_cut_num(self):
    
        for v in self.score_dict.values():
            if v['rank'] == "CUT":
                return len([x for x in self.score_dict.values() if x['rank'] not in ['CUT',]]) + 1
        if self.get_round() != 4 and len(self.score_dict.values()) >65:
            return 66
        #else:
        #    return len([x for x in self.score_dict.values() if x['rank'] not in ['CUT',]]) + 1


    def get_leader(self):
        leader_dict = {}        
        for golfer, stats in self.score_dict.items():
           #print ('ld', golfer, stats)
           if stats['rank'] in ['1', 'T1']:
               leader_dict[golfer]=stats['total_score']
           else:
               pass
     
        return leader_dict

    def tournament_complete(self):
        for v in self.score_dict.values():
            if v['rank'] not in ["CUT", "WD"] and \
                v['r4'] == "--":
                return False
        if self.get_round() == 4:
            return True

    