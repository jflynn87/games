from golf_app.models import Picks, Tournament, TotalScore, BonusDetails, ScoreDetails, PickMethod, \
    Group, Field
from django.contrib.auth.models import User
from golf_app import scrape_scores_picks


class WDCheck(object):

    def __init__(self, tournament=None, field=None):
        if tournament == None:
            self.tournament = Tournament.objects.get(current=True)
        else:
            self.tournament = tournament
        if field == None:
            self.field = scrape_scores_picks.ScrapeScores(self.tournament).scrape()
        else:
            self.field = field

    def check_wd(self):
        results = {}
        wd_list = []
        good_list = []

        clean_dict = {key.replace('(a)', '').strip() for key in self.field.keys()}

        print (clean_dict)
        for golfer in Field.objects.filter(tournament = self.tournament):
            #if golfer.playerName in {key.split(', Jr.') for key in field.keys()}:
            #if golfer.playerName in self.field.keys():
            if golfer.playerName in clean_dict:
                good_list.append(golfer.playerName)
            #elif: for k in self.fields.keys():
            #    if golfer_playerName in k.strip('(a)').lstrip().rstrip():
            #        good_list.append(golfer.playerName)
            else:
                print ('missed look up', golfer.playerName, self.field.get(golfer.playerName))
                wd_list.append(golfer.playerName)
                #golfer.withdrawn = True
                #golfer.save()
        results['wd_list'] = wd_list
        results['good_list'] = good_list

        if len(wd_list) < 4:
            for wd in wd_list:
                f = Field.objects.get(tournament=self.tournament, playerName=wd)
                f.withdrawn = True
                f.save()
        else:
            print ('long WD list, check....')

        return results
    
    def check_wd_picks(self):
        wd_picks = {}
        
        if Picks.objects.filter(playerName__playerName__in=self.check_wd()['wd_list'], playerName__tournament=self.tournament).exists():
            for pick in Picks.objects.filter(playerName__playerName__in=self.check_wd()['wd_list'], playerName__tournament=self.tournament):
                print(wd_picks, pick, pick.user.username)
                try:
                    wd_picks.get(pick.playerName.playerName).append(pick.user.username)
                except Exception as e:
                    print (e)
                    wd_picks[pick.playerName.playerName] = [pick.user.username]
                    

        return wd_picks


            
        
    
