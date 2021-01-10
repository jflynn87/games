from fb_app.models import Games, PlayoffStats
import scipy.stats as ss
from django.db.models import Sum

class Stats(object):
    '''takes a player object and optional game object and has methods to calc 
        scores for each category of the playoff game'''

    def __init__(self, game=None):
        
        if game == None:
            self.game = Games.objects.get(week__current=True, playoff_picks=True)
        else:
            self.game=game

        print ('playoff stats game', self.game)
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
        all_stats['home_passing'] = self.home_passing()
        all_stats['home_passer_rating'] = self.home_passer_rating()
        all_stats['away_runner'] = self.away_runner()
        all_stats['away_receiver'] = self.away_receiver()
        all_stats['away_passing'] = self.away_passing()
        all_stats['away_passer_rating'] = self.away_passer_rating()
        all_stats['winning_team'] = self.winning_team()
        all_stats['teams'] = self.teams()

       # print ('XXXXXall stats', all_stats['teams'])
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


    def home_passing(self):
        if self.stats.home_passing != None:
            print (self.stats.home_passing)
            return self.stats.home_passing
        else:
            print ('no override')
            return max(int(f['yards']) for f in self.stats.data['home']['passing'].values())

    
    def home_passer_rating(self):
        ### update model for this
        if self.stats.home_passing != None:
            print (self.stats.home_passing)
            return self.stats.home_passing
        else:
            print ('no override')
            return max(float(f['rating']) for f in self.stats.data['home']['passing'].values())


    def away_runner(self):
        if self.stats.away_runner != None:
            print (self.stats.away_runner)
            return self.stats.away_runner
        else:
            print ('no override')
            return max(int(f['yards']) for f in self.stats.data['away']['rushing'].values())
        
    
    def away_receiver(self):
        if self.stats.away_receiver != None:
            print (self.stats.away_receiver)
            return self.stats.away_receiver
        else:
            print ('no override')
            return max(int(f['yards']) for f in self.stats.data['away']['receiving'].values())


    def away_passing(self):
        if self.stats.away_passing != None:
            print (self.stats.away_passing)
            return self.stats.away_passing
        else:
            print ('no override')
            return max(int(f['yards']) for f in self.stats.data['away']['passing'].values())


    def away_passer_rating(self):
        ### update model for this
        if self.stats.away_passing != None:
            print (self.stats.away_passing)
            return self.stats.away_passing
        else:
            print ('no override')
            return max(float(f['rating']) for f in self.stats.data['away']['passing'].values())
 
    def winning_team(self):
        if self.stats.winning_team != None:
            print (self.stats.winning_team)
            return self.stats.winning_team
        else:
            print ('no override')
            home_score = self.stats.data['home']['team_stats']['score']
            away_score = self.stats.data['away']['team_stats']['score']
            if home_score > away_score:
                print ('home team wins')
                return self.stats.data['home']['team']
            elif away_score > home_score:
                print ('away team wins')
                return self.stats.data['away']['team']
            else:
                print ('no winner')
                return 'No winner'


    def teams(self):
        print ('teams sect', self.stats.data['home']['team'])
        return {'home': self.stats.data['home']['team'],
                'away': self.stats.data['away']['team']
                        }
