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
    
    def __init__(self, score_dict, tournament):
    
        self.tournament = tournament
        #self.tournament = Tournament.objects.get(pga_tournament_num=tournament_num, season__current=True)
        self.score_dict = score_dict

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




    def get_picked_golfers(self):
        pick_list = []
        for pick in Picks.objects.filter(playerName__tournament=self.tournament):
            #if any(isinstance(pick_list, type(list)) for pick in pick_list):
            if pick.pk in pick_list:
                print ('in')
            else:
                pick_list.append(pick.pk)
        print (len(pick_list))
        return pick_list


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
                        print (row)
                        if row[3] != '':
                            score_dict[row[3]] = {'total': row[0], 'status': row[5], 'score': row[4], 'r1': row[7], 'r2': row[8], 'r3': row[9], 'r4': row[10]}
                    
                        else:
                            print ('round.csv file read failed', row, e)
                    except Exception as e:
                        pass

        finally:
            driver.quit()


        #print ('end get_score_file', datetime.now())

        return score_dict
        

    def update_scores(self):
        print ('start update_scores', datetime.now())
        print (self.score_dict)
        for pick in Picks.objects.filter(playerName__tournament=self.tournament):
            print (pick.playerName.playerName, self.score_dict.get(pick.playerName.playerName))
            if self.score_dict.get(pick.playerName.playerName).get('total') in ["CUT", "WD"]:
                pick.score = self.get_cut_num()
            else:
                #print (self.get_round())
                #print (pick.playerName.playerName, self.get_cut_num(), calc_score.formatRank(self.score_dict.get(pick.playerName.playerName).get('total')))
                if int(calc_score.formatRank(self.score_dict.get(pick.playerName.playerName).get('total'))) > self.get_cut_num():
                    pick.score=self.get_cut_num()
                else:
                    pick.score = calc_score.formatRank(self.score_dict.get(pick.playerName.playerName).get('total'))
                
            pick.save()
                        
            sd, sd_created = ScoreDetails.objects.get_or_create(user=pick.user, pick=pick)
            sd.score=pick.score
            if self.score_dict.get(pick.playerName.playerName).get('total') in ["CUT", "WD"]:
                sd.today_score  = self.score_dict.get(pick.playerName.playerName).get('total')
            else:
                sd.today_score = self.score_dict.get(pick.playerName.playerName).get('r' + str(self.get_round()-1))
            sd.toPar = self.score_dict.get(pick.playerName.playerName).get('score')
            

            
            sd.save()

            if pick.is_winner() and not PickMethod.objects.filter(method=3).exists():
                print ('winner', pick.playerName)
                bd, created = BonusDetails.objects.get_or_create(user=pick.user, tournament=pick.playerName.tournament)
                bd.winner_bonus = 50 + (pick.playerName.group.number*2)
                bd.save()

        print ('end update_scores', datetime.now())

    def total_scores(self):
        print ('start total_scores', datetime.now())
        TotalScore.objects.filter(tournament=self.tournament).delete()
        for pick in Picks.objects.filter(playerName__tournament=self.tournament):
            ts, created = TotalScore.objects.get_or_create(user=pick.user, tournament=pick.playerName.tournament)
            if created:
                ts.score = pick.score
                ts.cut_count = 0
            else:
              #  print (pick, ts.score, pick.score)
                ts.score = calc_score.formatRank(ts.score) + calc_score.formatRank(pick.score)

            if self.score_dict.get(pick.playerName.playerName).get('total') in ["CUT", "WD"]:
                ts.cut_count +=1            
            
            
            # if pick.is_winner():
            #     print ('winner', pick)
            #     bd = BonusDetails.objects.get(tournament=self.tournament, user=pick.user)
            #     bd.winner_bonus = 50 + (2*pick.playerName.group.number)
            #     bd.save()
            #     ts.score -= bd.winner_bonus
            #     ts.save()

            ts.save()
        print ('end total_scores', datetime.now())

    def winner_bonus(self):
        for pick in Picks.objects.filter(playerName__tournament=self.tournament):
            if pick.is_winner():
                bd, created = BonusDetails.objects.get_or_create(user=pick.user, tournament=pick.playerName.tournament)
                bd.winner_bonus = 50 + (pick.playerName.group.number*2)
                bd.save()

            
    def get_round(self):
        round = 0
        for stats in self.score_dict.values():
            if stats.get('status')[0] != "F" and stats.get('total') not in ('CUT', 'WD'):
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
                        return 4
                    else:
                        round = 4
        return round
               

    def get_cut_num(self):
        if self.get_round() in [1, 2, 3]:
            return 66
        else:
            return len([x for x in self.score_dict.values() if x['total'] not in ['CUT', 'WD']]) + 1

    def get_leader(self):
        leader_dict = {}        
        for golfer, stats in self.score_dict.items():
           if stats['total'] in [1, 'T1']:
               leader_dict[golfer]=stats['score']
           else:
               pass
        return leader_dict

    