from fb_app.models import Games, WeekScore, Player
#import scipy.stats as ss
from django.db.models import Sum

class Scores(object):
    '''takes a week and league object and calculates the scores and updates the NFL scores'''

    def __init__(self, week, league, calc=True):
        self.week = week
        self.league = league
        self.week_score = WeekScore
        if calc:
            self.scores = calc_scores(self.week_score, self.league, self.week)

    def get_nfl_scores(self):
        nfl_dict = {}
        for game in Games.objects.filter(week=self.week):
            nfl_dict[game.eid]={'home': str(game.home), 'home_score': game.home_score, \
                 'away': str(game.away), 'away_score': game.away_score, 'qtr': game.qtr, \
                 'winner': str(game.winner), 'loser': str(game.loser), 'tie': game.tie, \
                     'final': game.final}
        return nfl_dict

    def get_week_scores(self):
        scores_dict = {}
        for score in WeekScore.objects.filter(week=self.week, player__league=self.league):
            scores_dict[score.player.name.username]=score.score
        return scores_dict

    def get_week_rank(self):
        rank_dict = {}
        #ranks = ss.rankdata(list(self.get_week_scores().values()), method='min')
        l = list(self.get_week_scores().values())
        ranks = [sorted(l).index(x)+1 for x in l]
        for i, (player, rank) in enumerate(self.get_week_scores().items()):
            rank_dict[player]=ranks[i]
        return rank_dict

    
    def get_week_proj(self):
        #projected is only games in progree, need to add complete games to it
        proj_dict = {}
        for score in WeekScore.objects.filter(week=self.week, player__league=self.league):
            proj_dict[score.player.name.username]=score.projected_score + score.score
        return proj_dict

    def get_week_proj_rank(self):
        proj_rank_dict = {}
        #proj_ranks = ss.rankdata(list(self.get_week_proj().values()), method='min')
        l = list(self.get_week_proj().values())
        proj_ranks = [sorted(l).index(x)+1 for x in l]

        for i, (player, rank) in enumerate(self.get_week_proj().items()):
            proj_rank_dict[player]=proj_ranks[i]
        return proj_rank_dict


    def get_season_total(self):
        season_total_dict = {}
        totals = WeekScore.objects.filter(week__week__lte=self.week.week, \
          player__league=self.league, week__season_model__current=True, \
          player__active=True).values('player__name__username').annotate(Sum('score'))
        for total in totals:
            season_total_dict[total.get('player__name__username')]=total.get('score__sum')
        return season_total_dict

    def get_season_rank(self):
        season_rank_dict = {}
        #season_ranks = ss.rankdata(list(self.get_season_total().values()), method='min')
        l = list(self.get_season_total().values())
        season_ranks = [sorted(l).index(x)+1 for x in l]
        for i, (player, rank) in enumerate(self.get_season_total().items()):
            season_rank_dict[player]=season_ranks[i]
        return season_rank_dict

    def get_losers(self):
        loser_list = []
        for game in Games.objects.filter(week=self.week, final=True):
            loser_list.append(game.loser.nfl_abbr)
        return loser_list



