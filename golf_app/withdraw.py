from golf_app.models import Picks, Tournament, TotalScore, BonusDetails, ScoreDetails, PickMethod, \
    Group, Field
from django.contrib.auth.models import User
from golf_app import scrape_scores


class WDCheck(object):

    def __init__(self, tournament=None):
        if tournament == None:
            self.tournament = Tournament.objects.get(current=True)
        else:
            self.tournament = tournament

    def check_wd(self):
        wd_list = []
        good_list = []
        field = scrape_scores.ScrapeScores(self.tournament).scrape()
        print (field)
        for golfer in Field.objects.filter(tournament = self.tournament):
            #if golfer.playerName in {key.split(', Jr.') for key in field.keys()}:
            if golfer.playerName in field.keys():
                good_list.append(golfer.playerName)
            else:
                print ('missed look up', golfer.playerName, field.get(golfer.playerName))
                wd_list.append(golfer.playerName)
        return wd_list, good_list
        
    
