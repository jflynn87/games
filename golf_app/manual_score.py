import urllib.request
import json
from golf_app.models import Picks, Tournament, TotalScore
import csv
from golf_app import calc_score

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


    def update_scores(self, file):
        with open(file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count > 0 and Picks.objects.filter(playerName__tournament=self.tournament, playerName__playerName=row[3]).exists():
                    for pick in Picks.objects.filter(playerName__tournament=self.tournament, playerName__playerName=row[3]):
                        pick.score = calc_score.formatRank(row[0])
                        pick.save()
                    #print (row[3], row[0])
                line_count += 1

    def total_scores(self):
        TotalScore.objects.filter(tournament=self.tournament).delete()
        for pick in Picks.objects.filter(playerName__tournament=self.tournament):
            ts, created = TotalScore.objects.get_or_create(user=pick.user, tournament=pick.playerName.tournament)
            if created:
                ts.score = pick.score
            else:
                ts.score = ts.score + pick.score
            ts.save()
