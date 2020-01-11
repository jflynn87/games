import urllib.request
import json
from golf_app.models import Picks, Tournament, TotalScore, BonusDetails, ScoreDetails
import csv
from golf_app import calc_score
import unicodedata

class Score(object):
    
    def __init__(self, tournament_num, season='current'):
    
        self.tournament_num = tournament_num
        self.tournament = Tournament.objects.get(pga_tournament_num=tournament_num, season__current=True)
        #self.json_url = 'https://statdata.pgatour.com/r/' + self.tournament_num + '/2020/leaderboard-v2mini.json'
        
        #with urllib.request.urlopen(self.json_url) as field_json_url:
        #        self.json = json.loads(field_json_url.read().decode())

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
        score_dict = {}
        with open(file, encoding="utf8") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
    
            for row in csv_reader:
                try:
                    if row[3] != '':
                        score_dict[row[3]] = {'total': row[0], 'status': row[5], 'score': row[4], 'r1': row[7], 'r2': row[8], 'r3': row[9], 'r4': row[10]}
                except Exception:
                    pass
        
        return score_dict
        

    def update_scores(self):
        for pick in Picks.objects.filter(playerName__tournament=self.tournament):
            print (pick.playerName, self.get_score_file().get(pick.playerName.playerName))
            
            if self.get_score_file().get(pick.playerName.playerName).get('total') in ["CUT", "WD"]:
                pick.score = self.get_cut_num()
            else:
                pick.score = calc_score.formatRank(self.get_score_file().get(pick.playerName.playerName).get('total'))
                
            pick.save()
                        
            sd, sd_created = ScoreDetails.objects.get_or_create(user=pick.user, pick=pick)
            sd.score=pick.score
            sd.save()

            if pick.is_winner():
                print ('winner', pick.playerName)
                bd, created = BonusDetails.objects.get_or_create(user=pick.user, tournament=pick.playerName.tournament)
                bd.winner_bonus = 50 + (pick.playerName.group.number*2)
                bd.save()

        print ('scores done')

    def total_scores(self):
        TotalScore.objects.filter(tournament=self.tournament).delete()
        for pick in Picks.objects.filter(playerName__tournament=self.tournament):
            ts, created = TotalScore.objects.get_or_create(user=pick.user, tournament=pick.playerName.tournament)
            print (ts, created)
            if created:
                ts.score = pick.score
            else:
                ts.score = ts.score + pick.score
            if pick.is_winner():
                print ('winner', pick)
                bd = BonusDetails.objects.get(tournament=self.tournament, user=pick.user)
                bd.winner_bonus = 50 + (2*pick.playerName.group.number)
                bd.save()
                ts.score -= bd.winner_bonus
                ts.save()

            

            ts.save()

    def winner_bonus(self):
        for pick in Picks.objects.filter(playerName__tournament=self.tournament):
            if pick.is_winner():
                bd, created = BonusDetails.objects.get_or_create(user=pick.user, tournament=pick.playerName.tournament)
                bd.winner_bonus = 50 + (pick.playerName.group.number*2)
                bd.save()

            
    def get_round(self):
        round = 0
        for stats in self.get_score_file().values():
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
        if self.get_round() in [1, 2]:
            return 66
        else:
            return len([x for x in self.get_score_file().values() if x['total'] not in ['CUT', 'WD']]) + 1