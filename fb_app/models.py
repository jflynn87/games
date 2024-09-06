from lzma import FILTER_LZMA1
from django.db import models
from django.db.models import constraints
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q, Sum, F
from django.core.exceptions import ObjectDoesNotExist

import datetime
import urllib3
import urllib
import json
#import scipy.stats as ss
#from django.db.models import Q
from bs4 import BeautifulSoup
from fb_app import scrape_cbs, espn_data
from django.core import serializers
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.

class Season(models.Model):
    season = models.CharField(max_length=30,unique=True)
    current = models.BooleanField(default=False)

    def __str__(self):
        return (str)(self.season)

    def started(self):
        if Week.objects.filter(season=self, week=1).exists():
            if Week.objects.get(season=self, week=1).started():
                return True
        return False

    def home_wins(self):
        return Games.objects.filter(week__season_model=self, week__week__lte=18, home=F('winner')).count()

    def away_wins(self):
        return Games.objects.filter(week__season_model=self, week__week__lte=18, away=F('winner')).count()
            
            

class Week(models.Model):
    season = models.CharField(max_length=30, null=True)
    season_model = models.ForeignKey(Season, on_delete=models.CASCADE,null=True)
    week = models.PositiveIntegerField()
    game_cnt = models.PositiveIntegerField(null=True)
    current = models.BooleanField(default=False)
    late_picks = models.BooleanField(default=False)
    set_started = models.BooleanField(default=False)
    set_not_started = models.BooleanField(default=False)
    regular_week = models.BooleanField(default=False)

    def __str__(self):
        return str(self.week)

    #def save(self, *args, **kwargs):
    #    if self.week != 1:
    #       print ('model self', self)
    #       print ('model kwargs', kwargs)
    #       last_week = Week.objects.get(current=True)
           #if self.pk != None and last_week.started():

    #              scores = WeekScore()
    #              calc_scores(scores, league, last_week)

    #       if self.current==True:
    #           last_week.current = False
    #           last_week.save()
           
           

        
    #    super(Week, self).save()

    def started(self):
        #print ('week started check', self.current)
        if self.set_started:
            print ('manually set started')
            return True
        if self.set_not_started:
            print ('manually set not started')
            return False
        #if Games.objects.filter(week=self, qtr__isnull=False).exists():
        if Games.objects.filter(week=self, qtr__isnull=False).exclude(qtr__in=['pregame', 'postponed']).exclude(qtr__icontains='AM').exclude(qtr__icontains='PM').exists():
            print ('week started based on db scores')
            return True
        elif not self.current:
            print ('future week, not started')
            return False
        else:
            print ('checking if stated on espn api  ')
            #web = scrape_cbs.ScrapeCBS(self).get_data()
            games = espn_data.ESPNData().get_data()
            #games = web['games']
            
            #print (games)
            for k, v in games.items():
                print (k , v)
                if not Games.objects.filter(eid=k, week=self).exists():
                    print ('last week API data, skip')
                    continue
                time_inds = ['am', 'pm', 'AM', 'PM', 'pregame', 'postponed', 'Scheduled']

                if v.get('qtr') not in [None, 'pregame', 'postponed', 'Scheduled'] and not any(ele in v.get('qtr') for ele in time_inds):
                    print ('week started based on scrape: ', v)
                    return True
                #else:
                #     return False
            print ('week not started after scrape')
            return False
        print ('week not started after scrape2 - shouldnt be here?')
        return False
        

    def get_spreads(self):

        spread_dict = {}
        for game in Games.objects.filter(week=self):
            try:
                s = float(game.spread[1:])
                spread_dict[game.eid]=(game.fav, game.dog, float(game.spread[1:]))
            except Exception:
                try:
                    spread = 0
                    #if game.spread == 'pk':
                    #    spread = 0
                    #if game.spread != 'pk':    
                    for char in game.spread[1:]:
                        if char in ['-', '+']:
                           break
                        elif char == '½':
                           spread = float(spread) + .5
                           break
                        else:
                           spread = str(spread) + str(char)
                    spread_dict[game.eid]=(game.fav, game.dog, float(spread))
                except Exception:
                    #print (game, game.fav, game.dog)
                    spread_dict[game.eid]=(game.home, game.away, 0)

        return spread_dict

    
    def score_ranks(self, league):
        u = []
        l = []
        for score in WeekScore.objects.filter(week=self, player__league=league, player__active=True):
            u.append(score.player.name.username)
            l.append(score.score)

        #l_rank = ss.rankdata(l, method='min')
        l_rank = [sorted(l).index(x)+1 for x in l]
        d = {}

        for i, user in enumerate(u):
            d[user] = int(l_rank[i])

        return d

    def proj_ranks(self, league, proj_score=None):
        #print (proj_score, type(proj_score))
        u = []
        l = []
        if proj_score == None:
            for score in WeekScore.objects.filter(week=self, player__league=league, player__active=True):
                u.append(score.player.name.username)
                l.append(score.projected_score)
        else:
            for user, score in proj_score.items():
                #print ('new code: ', u, l)
                u.append(user)
                l.append(score.get('proj_score'))

        #l_rank = ss.rankdata(l, method='min')
        l_rank = [sorted(l).index(x)+1 for x in l]
        d = {}

        for i, user in enumerate(u):
            d[user] = int(l_rank[i])

        return d

    def update_games(self):
        if Games.objects.filter(week=self).exclude(final=True).exists():
            try:
                print ('---------- updating football game scores')
                #data = get_data()
                #web = scrape_cbs.ScrapeCBS(self).get_data()
                #data  = web['games']
                data = espn_data.ESPNData().get_data()
                print ('UPDATE GAMES: ', data)


                for game in Games.objects.filter(week=self).exclude(final=True):
                    try:
                        #print ('game', game, game.eid)

                        home_score = int(data[game.eid]['home_score'])
                        home_team = data[game.eid]['home']
                        away_team = data[game.eid]['away']
                        away_score =int(data[game.eid]['away_score'])
                        qtr = data[game.eid]['qtr']

                        if home_score == away_score:
                            tie = True
                            winner = None
                            loser = None
                        elif home_score > away_score:
                            winner = Teams.objects.get(nfl_abbr=home_team)
                            loser = Teams.objects.get(nfl_abbr=away_team)
                            tie = False
                        else:
                            winner = Teams.objects.get(nfl_abbr=away_team)
                            loser = Teams.objects.get(nfl_abbr=home_team)
                            tie = False

                        setattr(game, 'home_score',home_score)
                        setattr(game, 'away_score',away_score)
                        setattr(game, 'winner', winner)
                        setattr(game, 'loser', loser)
                        if qtr == None:
                            setattr(game, 'qtr', None)
                            
                        else:
                            setattr(game, 'qtr',qtr.lower())                        
                            #print ('qtr', qtr[0:5], game)
                            if qtr[0:5]  in ["final", "Final", "FINAL"]:
                                print (game, 'setting final')
                                setattr(game, 'final', True)
                                setattr(game, 'tie', tie)
                            else:
                                setattr(game, 'tie', False)
                    
                        game.save()

                    except Exception as e:
                        print ('failed to update game: ', game, e)

            except KeyError as e:
                print ('update scores NFL score file not ready for the week', e)
                pass
        else:
            data = espn_data.ESPNData().get_data()  # should make this model based if api seems slow

        return {'games': data}

    def update_scores(self, league, recalc=False):
        start = datetime.datetime.now()

        loser_list = []
        proj_loser_list = []
        score_dict = {}
        for game in Games.objects.filter(week=self):
            #loser_list.append(game.loser)

            if not game.final:
                #print ('not final', game, game.home_score, game.away_score)
                if game.home_score > game.away_score:
                    proj_loser_list.append(game.away)
                elif game.home_score < game.away_score:
                    proj_loser_list.append(game.home)
            else:
                if game.tie and league.ties_lose:
                    loser_list.append(game.home)
                    loser_list.append(game.away)
                else:
                    loser_list.append(game.loser)
        print ('proj_loser', proj_loser_list)
        for player in Player.objects.filter(league=league, active=True):
            score_dict[player.name.username] = {'score': 0, 'proj_score': 0}
            
        for pick in Picks.objects.filter(team__in=loser_list, week=self, player__league=league, player__active=True):
            score_dict[pick.player.name.username].update({'score': score_dict.get(pick.player.name.username).get('score') + pick.pick_num})
            score_dict[pick.player.name.username].update({'proj_score': score_dict.get(pick.player.name.username).get('proj_score') + pick.pick_num})
        
        for pick in Picks.objects.filter(team__in=proj_loser_list, player__league=league, week=self, player__active=True):
            score_dict[pick.player.name.username].update({'proj_score': score_dict.get(pick.player.name.username).get('proj_score') + pick.pick_num})

        if self.current or recalc:
            for player in Player.objects.filter(league=league, active=True):
                sd, created = WeekScore.objects.get_or_create(player=player, week=self)
                sd.score = score_dict[player.name.username].get('score')
                sd.projected_score = score_dict[player.name.username].get('proj_score')
                sd.save()
            
        print ('##### checking score dict in model update score', score_dict)
        print ('update_scores duration: ', datetime.datetime.now() - start)

        return score_dict


    def get_scores(self, league, loser_list=None, proj_loser_list=None):
        start = datetime.datetime.now()
        print ('starting calc_scores', start)
        print ('score week: ', self.week)

        print ('player and score object creation start')
        
        self.update_games()
        print ('finished updating scores: ', datetime.datetime.now() - start)
        scores = self.update_scores(league)
        
        score_dict = {}
        user_list = []
        picks_dict = {}

        for player in Player.objects.filter(league=league, active=True):
            score_dict[player.name.username] = {}
        
        print ('before building pick dict:', datetime.datetime.now() - start)
        
        # for pick in Picks.objects.filter(player__league=league, week=self, player__active=True).order_by('player__name__username').order_by('pick_num'):
        #     if pick.is_loser():
        #         status = 'loser' 
        #     else:
        #         status = 'reg'
        #     try:
        #         score_dict[pick.player.name.username]['picks'].update({pick.pick_num: {'team': pick.team.nfl_abbr, 'status': status}})
        #     except Exception as e:
        #         score_dict[pick.player.name.username]['picks'] = {pick.pick_num: {'team': pick.team.nfl_abbr, 'status': status}}

        print ('after building pick dict:', datetime.datetime.now() - start)

        for user, score in scores.items():
            score_dict[user].update(score)

        
        for user, rank in self.score_ranks(league).items():
            score_dict[user].update({'rank': rank})
        
        for user, rank in self.proj_ranks(league).items():
            score_dict[user].update({'proj_rank': rank})

        for player in Player.objects.filter(league=league, active=True):
            score_dict[player.name.username].update({'season_total': player.season_total()})
        
        for player, rank in league.season_ranks().items():
            score_dict[player].update({'season_rank': rank})


        #print (score_dict)
        print ('get scores durations: ', datetime.datetime.now() - start)
        return score_dict

    def picks_complete(self, league):
        players = Player.objects.filter(league=league, active=True).count()
        picks = Picks.objects.filter(week=self, player__league=league).count()
        # not adjusting game cnt for postponed as expecting not to happen before picks complete
        print (players, self.game_cnt)
        if picks == self.game_cnt * players:
            return True
        else:
            return False

    def games_complete(self):
        if Games.objects.filter(week=self, final=True).count() +  \
         Games.objects.filter(week=self, postponed=True).count()== self.game_cnt:
            return True
        else:
            return False

@receiver(post_save, sender=Week)
def update_analyitcs(sender, **kwargs):
    print ('updating stats; ', kwargs.get('instance'))
    week = kwargs.get('instance')
    print (week.week, type(week.week))
    if week.week > 19 or week.week == 1:
        return

    if week.current:
        print ('current week, updating stats')
        season = Season.objects.get(current=True)
        for league in League.objects.all():
            stats, created = PickPerformance.objects.get_or_create(season=season, league=league)
            stats.calculate()
    return


class Teams(models.Model):
    mike_abbr = models.CharField(max_length=4, null=True)
    nfl_abbr = models.CharField(max_length=4, null=True)
    long_name = models.CharField(max_length=30, null=True)
    typo_name = models.CharField(max_length=30,null=True, blank=True)
    typo_name1 = models.CharField(max_length=30,null=True, blank=True)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
    pic = models.URLField(null=True)

    class Meta:
        ordering = ('nfl_abbr',)

    def __str__(self):
        return str(self.nfl_abbr)

    def natural_key(self):
        return self.nfl_abbr


    def get_mike_abbr(self):
        return self.mike_abbr

    def get_record(self, season=None):
        '''takes a season object and returns a tuple with record)'''
        if season == None:
            season = Season.objects.get(current=True)

        wins = Games.objects.filter(week__season=season, winner=self).exclude(week__week__gte=19).count()
        losses = Games.objects.filter(week__season=season, loser=self).exclude(week__week__gte=19).count()
        ties = Games.objects.filter(Q(week__season=season), (Q(home=self) | Q(away=self)), Q(tie=True)).exclude(week__week__gte=19).count()

        return (wins, losses, ties)



class Games(models.Model):
    eid = models.CharField(max_length=30)
    week = models.ForeignKey(Week,on_delete=models.CASCADE, db_index=True)
    fav = models.ForeignKey(Teams, on_delete=models.CASCADE,null=True, related_name='fav')
    dog = models.ForeignKey(Teams, on_delete=models.CASCADE,null=True, related_name='dog')
    home = models.ForeignKey(Teams, on_delete=models.CASCADE,null=True, related_name='home', db_index=True)
    away = models.ForeignKey(Teams, on_delete=models.CASCADE,null=True, related_name='away', db_index=True)
    opening = models.CharField(max_length=10, null=True, blank=True)
    spread = models.CharField(max_length=10,null=True, blank=True)
    winner = models.ForeignKey(Teams, on_delete=models.CASCADE,null=True, related_name='winner', blank=True)
    loser = models.ForeignKey(Teams, on_delete=models.CASCADE,null=True, related_name='loser', blank=True)
    final = models.BooleanField(default=False)
    home_score = models.PositiveIntegerField(null=True, default=0)
    away_score = models.PositiveIntegerField(null=True, default=0)
    qtr = models.CharField(max_length=25, null=True)
    tie = models.BooleanField(default=False)
    date = models.DateField(null=True, blank=True)
    time = models.CharField(max_length=20, null=True, blank=True)
    day = models.CharField(max_length=10, null=True, blank=True)
    game_time = models.DateTimeField(null=True, blank=True)
    postponed = models.BooleanField(default=False)
    playoff_picks = models.BooleanField(default=False)

    def __str__(self):
        return str(self.home) + str(self.away)

    class Meta:
        #index_together = ['week', 'home', 'away']
        unique_together = ['week', 'home', 'away']


    def check_started(self):
        pass

    def pre_start_inds(self):
        return ['am', 'pm', 'AM', 'PM', 'pregame', 'postponed', 'Scheduled']


    #def get_game_id(self):
    #    return self.eid

class League(models.Model):
    league = models.CharField(max_length=30)
    ties_lose = models.BooleanField(default=True)

    def __str__(self):
        return self.league

    def season_ranks(self):
        u = []
        l = []
        for player in Player.objects.filter(league=self, active=True):
            u.append(player.name.username)
            l.append(player.season_total())

        #l_rank = ss.rankdata(l, method='min')
        l_rank = [sorted(l).index(x)+1 for x in l]
        d = {}

        for i, user in enumerate(u):
            d[user] = int(l_rank[i])

        return d

    def leading_score(self):
        l = []
        for player in Player.objects.filter(league=self, active=True):
            l.append(player.season_total())

        return min(l)


    def correct_picks(self):
        d = {}
        for p in Player.objects.filter(league=self):
            d.update({p.name.username: p.correct_picks()})

        return d


class Player(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    email_picks = models.BooleanField(default=False)


    def __str__(self):
        return str(self.name)

    def picks_submitted(self, week):
        if Picks.objects.filter(week=week, player=self).exists():
            return True
        else:
            return False

    def season_total(self):
        score = WeekScore.objects.filter(player=self, week__season_model__current=True).aggregate(Sum('score'))
        return int(score.get('score__sum'))

    def submit_default_picks(self, week):
        print ('Submit auto FB picks', self, week, datetime.datetime.now())
        if week.started():
            espn = espn_data.ESPNData()
            starting_pick = 16
            #if len(espn.first_game_of_week()) == 1 and \
            #    espn.game_dow(espn.first_game_of_week()[0]) == 'Thursday':
            if week.regular_week:
                pick_16 = Picks()
                pick_16.week = week
                pick_16.player = self
                pick_16.pick_num = 16
                g = Games.objects.get(eid=espn.first_game_of_week()[0])
                if g.loser:
                    pick_16.team = g.loser
                elif g.dog:
                    pick_16.team = g.dog
                else:
                    pick_16.team = g.away
                pick_16.save()
                starting_pick = 15
                
            #if not Picks.objects.filter(week=week, player=self).exists():
            #if len(pick_pending) > 0:
            sorted_spreads = sorted(week.get_spreads().items(), key=lambda x: x[1][2],reverse=True)
            if starting_pick == 15:
                games_list= [x for x in sorted_spreads if x[0] != espn.first_game_of_week()[0]]
            else:
                games_list = sorted_spreads
            for i, game in enumerate(games_list):
                pick = Picks()
                pick.week = week
                pick.player = self
                pick.pick_num = starting_pick - i
                pick.team = game[1][1]
                pick.save()
        pm = PickMethod()
        pm.player = self
        pm.week = week
        pm.method = '3'
        pm.save()



    def season_points_behind(self):
        return self.league.leading_score() - self.season_total()  
         

    def season_picks_summary(self, season=None):
        if not season:
            season = Season.objects.get(current=True)

        d = {}

        for t in Teams.objects.all():
            wins = SeasonPicks.objects.filter(pick=t, season=season, player=self).count()
            loss = 17 - wins
            d[t.pk] = {'nfl_abbr': t.nfl_abbr,
                        'wins': wins,
                        'loss': loss }
        
        return d

    def season_picks_week_wins(self, week):
        d = {}
        if week.started():
            wins = SeasonPicks.objects.filter(game__week=week, player=self, pick=F('game__winner')).count()
            loss = SeasonPicks.objects.filter(game__week=week, player=self, pick=F('game__loser')).count()

            d[week.week] = {'wins': wins, 'loss': loss}

        return d

            
    def home_season_picks(self, season=None):
        if not season:
            season = Season.objects.get(current=True)
        return SeasonPicks.objects.filter(season=season, player=self, pick=F('game__home')).count()

    def away_season_picks(self, season=None):
        if not season:
            season = Season.objects.get(current=True)
        return SeasonPicks.objects.filter(season=season, player=self, pick=F('game__away')).count()


    def season_picks_record(self, season=None):
        #start = datetime.datetime.now()
        if not season:
            season = Season.objects.get(current=True)
        
        if not SeasonPicks.objects.filter(season=season, player=self).exists():
            return None
        d = {}
        d[self.name.username] = {'wins': 0,
             'loss': 0}
        #d = {}
        current_week = Week.objects.get(current=True)
        for week in Week.objects.filter(season_model__current=True, week__lte=current_week.week):
            wins = SeasonPicks.objects.filter(game__week=week, player=self, pick=F('game__winner')).count()
            loss = SeasonPicks.objects.filter(game__week=week, player=self, pick=F('game__loser')).count()
            d.get(self.name.username).update({'wins': d.get(self.name.username).get('wins') + wins,
                                            'loss': d.get(self.name.username).get('loss') + loss})
        
        #print (datetime.datetime.now() - start)

        return d 
        #if SeasonPicks.objects.filter(season=season, player=self).exists():
        #    wins = SeasonPicks.objects.filter(season=season, player=self, pick=F('game__winner')).count()
        #    loss = SeasonPicks.objects.filter(season=season, player=self, pick=F('game__loser')).count()
        #    d.update({self.name.username : {'wins': wins, 'loss': loss}})
        #    return d    
        #else:
        #    return None

    def season_picks_weekly_details(self, week):
        d = {}
        d[self.name.username] = {}
        
        for sp in SeasonPicks.objects.filter(game__week=week, player=self):
            d.get(self.name.username).update({sp.game.eid: {'home': sp.game.home.nfl_abbr,
                                                                'home_score': sp.game.home_score,
                                                                'away': sp.game.away.nfl_abbr,
                                                                'away_score': sp.game.away_score,
                                                                #'winner': sp.game.winner.nfl_abbr,
                                                                'tie': sp.game.tie,
                                                                'pick': sp.pick.nfl_abbr}})

            if not sp.game.tie:
                d.get(self.name.username).get(sp.game.eid).update({'winner': sp.game.winner.nfl_abbr})
            else:
                d.get(self.name.username).get(sp.game.eid).update({'winner': None})

        return d

    
    def correct_picks(self):
        wins = 0
        for w in Week.objects.filter(season_model__current=True):
            winners = Games.objects.filter(week=w).values('winner')
            wins += Picks.objects.filter(week=w, player=self, team__in=winners).count()
        return wins
        


class Picks(models.Model):
    week = models.ForeignKey(Week,on_delete=models.CASCADE, db_index=True)
    player  = models.ForeignKey(Player,on_delete=models.CASCADE,related_name="picks", db_index=True)
    pick_num = models.PositiveIntegerField()
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name="picksteam")


    def __str__(self):
        return str(self.player) + str(self.pick_num) + str(self.team)

    class Meta:
        #index_together = ['week', 'player']
        unique_together = ['week', 'player']


    def is_loser(self):
        try:
            game = Games.objects.get(Q(final=True), Q(week=self.week), (Q(home=self.team) | (Q(away= self.team))))
            if self.team == game.loser:
                return True
            elif self.team == game.winner:
                return False
            elif game.tie and self.player.league.ties_lose:
                return True
            else:  #ties win
                return False
        except ObjectDoesNotExist:
            return False

    # def is_proj_loser(self):
    #     try:
    #         game = Games.objects.get(Q(final=False), Q(week=self.week), (Q(home=self.team) | Q(away=self.team)))
    #         if game.home_score == game.away_score:
    #             return False
    #         elif game.home == self.team:
    #             if home_score < away_score:
    #                 return True
    #             else:
    #                 return False
    #         elif game.away == self.team:
    #             if away_score < home_score:
    #                 return True
    #             else:
    #                 return False
    #         else:
    #             return False
    #             print ('projected issue', game)
    #     except ObjectDoesNotExist:
    #         return False



class WeekScore(models.Model):
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(null=True)
    projected_score = models.PositiveIntegerField(null=True)

    def __str__(self):
        return str(self.player)
       

class MikeScore(models.Model):
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    total = models.PositiveIntegerField()

    def __str__(self):
        return str(self.player) + str(self.total)


class PickPerformance(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    data = models.JSONField(null=True)

    def __str__(self):
        return str(self.season)

    def calculate(self):

        start = datetime.datetime.now()
        c_week = Week.objects.get(current=True)
        team_dict = {}
        league_dict = {}

        for p in Player.objects.filter(league=self.league):
            league_dict[p.name.username] = {}

        for player in Player.objects.filter(league=self.league):
            for team in Teams.objects.all():
                team_dict[team.nfl_abbr] = {'picked_and_won': 0,
                                'picked_and_lost': 0,
                                'picked_against_won': 0,
                                'picked_against_lost': 0,
                                'tie': 0,
                                'right': 0,
                                'wrong': 0,
                                'points_lost': 0,
                                'points_won': 0}

            user = player.name
            for week in Week.objects.filter(week__lt=c_week.week, season_model=self.season):
                for pick in Picks.objects.filter(week=week, player__name=user).order_by('-pick_num'):
                    #print ('pick: ', pick)
                    game =  Games.objects.get(Q(week=week) & (Q(home=pick.team) | Q(away=pick.team)))
                    if game.tie:
                        team_dict[game.home.nfl_abbr].update({'tie': team_dict[game.home.nfl_abbr]['tie'] +1})
                        team_dict[game.away.nfl_abbr].update({'tie': team_dict[game.away.nfl_abbr]['tie'] +1})
                        if pick.player.league.ties_lose:
                            team_dict[game.home.nfl_abbr].update({'wrong': team_dict[game.home.nfl_abbr]['wrong'] +1})
                            team_dict[game.away.nfl_abbr].update({'wrong': team_dict[game.away.nfl_abbr]['wrong'] +1})
                            team_dict[game.home.nfl_abbr].update({'points_lost': team_dict[game.home.nfl_abbr]['points_lost'] + pick.pick_num})
                            team_dict[game.away.nfl_abbr].update({'points_lost': team_dict[game.away.nfl_abbr]['points_lost'] + pick.pick_num})
                        else:
                            team_dict[game.home.nfl_abbr].update({'right': team_dict[game.home.nfl_abbr]['right'] +1})
                            team_dict[game.away.nfl_abbr].update({'right': team_dict[game.away.nfl_abbr]['right'] +1})
                            team_dict[game.away.nfl_abbr].update({'points_won': team_dict[game.away.nfl_abbr]['points_won'] + pick.pick_num})
                    else:
                        if pick.team == game.winner:
                            team_dict[pick.team.nfl_abbr].update({'picked_and_won': team_dict[pick.team.nfl_abbr]['picked_and_won'] +1})
                            team_dict[pick.team.nfl_abbr].update({'right': team_dict[pick.team.nfl_abbr]['right'] +1})
                            team_dict[pick.team.nfl_abbr].update({'points_won': team_dict[pick.team.nfl_abbr]['points_won'] + pick.pick_num})

                            team_dict[game.loser.nfl_abbr].update({'picked_against_lost': team_dict[game.loser.nfl_abbr]['picked_against_lost'] +1})
                            team_dict[game.loser.nfl_abbr].update({'right': team_dict[game.loser.nfl_abbr]['right'] +1})
                            team_dict[game.loser.nfl_abbr].update({'points_won': team_dict[game.loser.nfl_abbr]['points_won'] + pick.pick_num})
                        elif pick.team == game.loser:
                            team_dict[pick.team.nfl_abbr].update({'picked_and_lost': team_dict[pick.team.nfl_abbr]['picked_and_lost'] +1})
                            team_dict[pick.team.nfl_abbr].update({'wrong': team_dict[pick.team.nfl_abbr]['wrong'] +1})
                            team_dict[pick.team.nfl_abbr].update({'points_lost': team_dict[pick.team.nfl_abbr]['points_lost'] + pick.pick_num})

                            team_dict[game.winner.nfl_abbr].update({'picked_against_won': team_dict[game.winner.nfl_abbr]['picked_against_won'] +1})
                            team_dict[game.winner.nfl_abbr].update({'wrong': team_dict[game.winner.nfl_abbr]['wrong'] +1})
                            team_dict[game.winner.nfl_abbr].update({'points_lost': team_dict[game.winner.nfl_abbr]['points_lost'] + pick.pick_num})
            league_dict[user.username].update(team_dict)

        self.data = json.dumps(league_dict)
        self.save() 
        print ('stats dict duration: ', datetime.datetime.now() - start)

        return json.dumps(league_dict)
        
    def team_results(self, team, player=None):
        '''takes a nfl_abbr (string) for a team, option player obj and returns a dict object'''
        if player:
            data = {}
            d = json.loads(self.data)[player.name.username]
            data[player] = d
        else:
            data = json.loads(self.data)
        results_dict = {}
        
        #print (data)
        wrong = sum(t[team]['wrong'] for t in data.values())
        right = sum(t[team]['right'] for t in data.values())
        picked_and_won = sum(t[team]['picked_and_won'] for t in data.values())
        picked_and_lost = sum(t[team]['picked_and_lost'] for t in data.values())
        picked_against_lost = sum(t[team]['picked_against_lost'] for t in data.values())
        picked_against_won = sum(t[team]['picked_against_won'] for t in data.values())
        points_won = sum(t[team]['points_won'] for t in data.values())
        points_lost = sum(t[team]['points_lost'] for t in data.values())

        results_dict = {'team': team, 'right': right, 'wrong': wrong, 
                        'picked_and_lost': picked_and_lost, 
                        'picked_and_won': picked_and_won,
                        'picked_against_lost': picked_against_lost,
                        'picked_against_won': picked_against_won,
                        'points_won': points_won,
                        'points_lost': points_lost,
        }

        return results_dict

    def all_team_results(self):
        '''takes PickPerformane object and returns a dict'''
        data = json.loads(self.data)
        results_dict = {}

        for team in Teams.objects.all():
            wrong = sum(t[team.nfl_abbr]['wrong'] for t in data.values())
            right = sum(t[team.nfl_abbr]['right'] for t in data.values())
            results_dict[team.nfl_abbr] = {'wrong': wrong, 'right': right, 
            'win_percent': "{:.0%}".format(round(int(right)/(int(right)+int(wrong)),2))}

        return results_dict


class PlayoffPicks(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Games, on_delete=models.CASCADE)
    rushing_yards = models.PositiveIntegerField(null=True)
    passing_yards = models.PositiveIntegerField(null=True)
    total_points_scored = models.PositiveIntegerField()
    points_on_fg = models.PositiveIntegerField()
    takeaways = models.PositiveIntegerField()
    sacks = models.PositiveIntegerField()
    def_special_teams_tds = models.PositiveIntegerField()
    home_runner = models.PositiveIntegerField()
    home_receiver = models.PositiveIntegerField()
    home_passing = models.PositiveIntegerField(null=True)
    home_passer_rating = models.FloatField(default=100.0)
    away_runner = models.PositiveIntegerField()
    away_receiver = models.PositiveIntegerField()
    away_passing = models.PositiveIntegerField(null=True)
    away_passer_rating = models.FloatField(default=100.0)
    winning_team = models.ForeignKey(Teams, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.player) + str(self.game)

    class Meta:
        constraints = [
        models.UniqueConstraint(fields=['player', 'game'], name='duplicate_picks')]


class PlayoffScores(models.Model):
    picks = models.ForeignKey(PlayoffPicks, on_delete=models.CASCADE)
    rushing_yards = models.IntegerField()
    passing_yards = models.IntegerField()
    total_points_scored = models.IntegerField()
    points_on_fg = models.IntegerField()
    takeaways = models.IntegerField()
    sacks = models.IntegerField()
    def_special_teams_tds = models.IntegerField()
    home_runner = models.IntegerField()
    home_receiver = models.IntegerField()
    home_passing = models.IntegerField()
    away_runner = models.IntegerField()
    away_receiver = models.IntegerField()
    away_passing = models.IntegerField()
    winning_team = models.IntegerField()
    total_score = models.IntegerField()
    

    def __str__(self):
        return str(self.picks.player, self.picks.game)


class PlayoffStats(models.Model):
    game = models.ForeignKey(Games, on_delete=models.CASCADE, null=True)
    rushing_yards = models.IntegerField(null=True)
    passing_yards = models.IntegerField(null=True)
    total_points_scored = models.IntegerField(null=True)
    points_on_fg = models.IntegerField(null=True)
    takeaways = models.IntegerField(null=True)
    sacks = models.IntegerField(null=True)
    def_special_teams_tds = models.IntegerField(null=True)
    home_runner = models.IntegerField(null=True)
    home_receiver = models.IntegerField(null=True)
    home_passing = models.IntegerField(null=True)
    home_passer_rating = models.FloatField(null=True)
    away_runner = models.IntegerField(null=True)
    away_receiver = models.IntegerField(null=True)
    away_passing = models.IntegerField(null=True)
    away_passer_rating = models.FloatField(null=True)
    winning_team = models.ForeignKey(Teams, on_delete=models.CASCADE, null=True)
    data = models.JSONField(null=True)


    def __str__(self):
        return str(self.game)


class PickMethod(models.Model):
    CHOICES = (('1', 'player'), ('2', 'favs'), ('3', 'auto'), ('4', 'fixed_auto'))

    method = models.CharField(max_length=20, choices=CHOICES)
    week = models.ForeignKey(Week, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.player) + self.method


class AccessLog(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='fb_user')
    page = models.CharField(max_length=100, null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    week = models.ForeignKey(Week, blank=True, null=True, on_delete=models.CASCADE)
    device_type = models.CharField(max_length=100, blank=True, null=True)
    views = models.PositiveBigIntegerField(default=0, null=True)

    def __str__(self):
        return str(self.user.username) + '  ' + str(self.page)


class SeasonPicks(models.Model):
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    game = models.ForeignKey(Games, on_delete=models.CASCADE)
    pick = models.ForeignKey(Teams, on_delete=models.CASCADE)


    def __str__(self):
        return str(self.season) + str(self.player) + str(self.game)

  
        


