from fb_app.models import Games, PlayoffStats
import scipy.stats as ss
from django.db.models import Sum

class Stats(object):
    '''takes a player object and optional game object and has methods to calc 
        scores for each category of the playoff game'''

    def __init__(self, game=None):
        
        print (game)
        if game == None:
            self.game = Games.objects.get(week__current=True, playoff_picks=True)
        else:
            self.game=game

        print (self.game)
        #self.score = Playoffscores.objects.get(game=game)
        self.stats = PlayoffStats.objects.get(game=self.game)
        
    def get_all_stats(self):
        all_stats = {}
        all_stats['total_rushing_yards'] = self.total_rushing_yards()
        all_stats['total_passing_yards'] = self.total_passing_yards()
        all_stats['total_points'] = self.total_points()
        all_stats['points_on_fg'] = self.points_on_fg()
        all_stats['takeaways'] = self.takeaways()
        all_stats['sacks'] = self.sacks()
        all_stats['def_special_teams_tds'] = self.def_special_teams_tds()
        all_stats['home_runner'] = self.home_runner()
        all_stats['home_receiver'] = self.home_receiver()

        return all_stats
    
    def total_rushing_yards(self):
        if self.stats.rushing_yards != None:
            print (self.stats.rushing_yards)
            return self.stats.rushing_yards
        else:
            print ('no override')
            return int(self.stats.data['home']['team_stats']['rushing']) + int(self.stats.data['away']['team_stats']['rushing'])

    def total_passing_yards(self):
        if self.stats.passing_yards != None:
            print (self.stats.passing_yards)
            return self.stats.passing_yards
        else:
            print ('no override')
            return int(self.stats.data['home']['team_stats']['passing']) + int(self.stats.data['away']['team_stats']['passing'])

    def total_points(self):
        if self.stats.total_points_scored != None:
            print (self.stats.total_points_scored)
            return self.stats.total_points_scored
        else:
            print ('no override')
            return int(self.stats.data['home']['team_stats']['score']) + int(self.stats.data['away']['team_stats']['score'])

    def points_on_fg(self):
        if self.stats.points_on_fg != None:
            print (self.stats.points_on_fg)
            return self.stats.points_on_fg
        else:
            print ('no override')
            home_fg = sum(int(f['fg/att'].split('/')[0]) for f in self.stats.data['home']['fg'].values())
            away_fg = sum(int(f['fg/att'].split('/')[0]) for f in self.stats.data['away']['fg'].values())
            
            return (home_fg + away_fg) *3

    def takeaways(self):
        if self.stats.takeaways != None:
            print (self.stats.takeaways)
            return self.stats.takeaways
        else:
            print ('no override')
            return int(self.stats.data['home']['team_stats']['turnovers']) + int(self.stats.data['away']['team_stats']['turnovers'])
    
    def sacks(self):
        if self.stats.sacks != None:
            print (self.stats.sacks)
            return self.stats.sacks
        else:
            print ('no override')
            home_sacks = sum(float(f['sacks']) for f in self.stats.data['home']['def'].values())
            away_sacks = sum(float(f['sacks']) for f in self.stats.data['away']['def'].values())

            return int(home_sacks) + int(away_sacks)

    def def_special_teams_tds(self):
        if self.stats.def_special_teams_tds != None:
            print (self.stats.def_special_teams_tds)
            return self.stats.def_special_teams_tds
        else:
            print ('no override')
            return int(self.stats.data['home']['team_stats']['other_tds']) + int(self.stats.data['away']['team_stats']['other_tds'])

    def home_runner(self):
        if self.stats.home_runner != None:
            print (self.stats.home_runner)
            return self.stats.home_runner
        else:
            print ('no override')
            return max(int(f['yards']) for f in self.stats.data['home']['rushing'].values())
        
    def home_receiver(self):
        if self.stats.home_receiver != None:
            print (self.stats.home_receiver)
            return self.stats.home_receiver
        else:
            print ('no override')
            return max(int(f['yards']) for f in self.stats.data['home']['receiving'].values())



    # team_one_passing = models.IntegerField(null=True)
    # team_two_runner = models.IntegerField(null=True)
    # team_two_receiver = models.IntegerField(null=True)
    # team_two_passing = models.IntegerField(null=True)