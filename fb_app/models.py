from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q, Sum
from django.core.exceptions import ObjectDoesNotExist

import datetime
import urllib3
import urllib
import json
import scipy.stats as ss
#from django.db.models import Q
from bs4 import BeautifulSoup
from fb_app import scrape_cbs

# Create your models here.

class Season(models.Model):
    season = models.CharField(max_length=30,unique=True)
    current = models.BooleanField(default=False)

    def __str__(self):
        return (str)(self.season)

class Week(models.Model):
    season = models.CharField(max_length=30, null=True)
    season_model = models.ForeignKey(Season, on_delete=models.CASCADE,null=True)
    week = models.PositiveIntegerField()
    game_cnt = models.PositiveIntegerField(null=True)
    current = models.BooleanField(default=False)
    late_picks = models.BooleanField(default=False)
    set_started = models.BooleanField(default=False)
    set_not_started = models.BooleanField(default=False)

    def __str__(self):
        return str(self.week)

    # def save(self, *args, **kwargs):
    #     if self.week != 1:
    #         print ('model self', self)
    #         print ('model kwargs', kwargs)
    #         last_week = Week.objects.get(current=True)
    #         if self.pk != None and last_week.started():
    #             for league in League.objects.all():
    #                 scores = WeekScore()
    #                 calc_scores(scores, league, last_week)

    #             if self.current==True:
    #                 last_week.current = False
    #                 last_week.save()
    #     super(Week, self).save()

    def started(self):
        print ('week started check')
        if self.set_started:
            print ('manually set started')
            return True
        if self.set_not_started:
            print ('manually set not started')
            return False
        #if Games.objects.filter(week=self, qtr__isnull=False).exists():
        if Games.objects.filter(week=self, qtr__isnull=False).exclude(qtr__in=['pregame', 'postponed']).exists():
            print ('true')
            return True
        else:
            web = scrape_cbs.ScrapeCBS(self).get_data()
            games = web['games']
            print (games)
            
            for k, v in games.items():
                if v.get('qtr') not in [None, 'pregame']:
                    print ('week started based on scrape: ', v)
                    return True
                else:
                    return False
            return False
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
                    print (game, game.fav, game.dog)
                    spread_dict[game.eid]=(game.home, game.away, 0)

        return spread_dict

    
    def score_ranks(self, league):
        u = []
        l = []
        for score in WeekScore.objects.filter(week=self, player__league=league):
            u.append(score.player.name.username)
            l.append(score.score)

        l_rank = ss.rankdata(l, method='min')
        d = {}

        for i, user in enumerate(u):
            d[user] = int(l_rank[i])

        return d

    def proj_ranks(self, league, proj_score=None):
        #print (proj_score, type(proj_score))
        u = []
        l = []
        if proj_score == None:
            for score in WeekScore.objects.filter(week=self, player__league=league):
                u.append(score.player.name.username)
                l.append(score.projected_score)
        else:
            for user, score in proj_score.items():
                #print ('new code: ', u, l)
                u.append(user)
                l.append(score.get('proj_score'))

        l_rank = ss.rankdata(l, method='min')
        d = {}

        for i, user in enumerate(u):
            d[user] = int(l_rank[i])

        return d

    def update_games(self):
        if Games.objects.filter(week=self).exclude(final=True).exists():
            try:
                print ('---------- updating football game scores')
                #data = get_data()
                web = scrape_cbs.ScrapeCBS(self).get_data()
                data  = web['games']


                for game in Games.objects.filter(week=self).exclude(final=True):
                    try:
                        print ('game', game, game.eid)

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
                            print ('qtr', qtr[0:5], game)
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

            return web

    def update_scores(self, league):
        start = datetime.datetime.now()

        loser_list = []
        proj_loser_list = []
        score_dict = {}
        for game in Games.objects.filter(week=self):
            #loser_list.append(game.loser)

            if not game.final:
                print ('not final', game, game.home_score, game.away_score)
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

        if self.current:
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
        scores = self.update_scores(league)
        
        score_dict = {}
        user_list = []
        picks_dict = {}

        print ('league: ', league, type(league))
        for player in Player.objects.filter(league=league, active=True):
            score_dict[player.name.username] = {}
        
        for pick in Picks.objects.filter(player__league=league, week=self, player__active=True).order_by('player__name__username').order_by('pick_num'):
            if pick.is_loser():
                status = 'loser' 
            else:
                status = 'reg'
            try:
                score_dict[pick.player.name.username]['picks'].update({pick.pick_num: {'team': pick.team.nfl_abbr, 'status': status}})
            except Exception as e:
                score_dict[pick.player.name.username]['picks'] = {pick.pick_num: {'team': pick.team.nfl_abbr, 'status': status}}

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
        print (datetime.datetime.now() - start)
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

    def get_mike_abbr(self):
        return self.mike_abbr

    def get_record(self, season=None):
        '''takes a season object and returns a tuple with record)'''
        if season == None:
            season = Season.objects.get(current=True)

        wins = Games.objects.filter(week__season=season, winner=self).count()
        losses = Games.objects.filter(week__season=season, loser=self).count()
        ties = Games.objects.filter(Q(week__season=season), (Q(home=self) | Q(away=self)), Q(tie=True)).count()

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

    def __str__(self):
        return str(self.home) + str(self.away)

    class Meta:
        index_together = ['week', 'home', 'away']



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

        l_rank = ss.rankdata(l, method='min')
        d = {}

        for i, user in enumerate(u):
            d[user] = int(l_rank[i])

        return d


class Player(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)


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
        if week.started():
            if not Picks.objects.filter(week=week, player=self).exists():
            #if len(pick_pending) > 0:
               sorted_spreads = sorted(week.get_spreads().items(), key=lambda x: x[1][2],reverse=True)
               for i, game in enumerate(sorted_spreads):
                    pick = Picks()
                    pick.week = week
                    pick.player = self
                    pick.pick_num = 16 - i
                    pick.team = game[1][1]
                    pick.save()



class Picks(models.Model):
    week = models.ForeignKey(Week,on_delete=models.CASCADE, db_index=True)
    player  = models.ForeignKey(Player,on_delete=models.CASCADE,related_name="picks", db_index=True)
    pick_num = models.PositiveIntegerField()
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, related_name="picksteam")


    def __str__(self):
        return str(self.player) + str(self.pick_num) + str(self.team)

    class Meta:
        index_together = ['week', 'player']

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

    def is_proj_loser(self):
        try:
            game = Games.objects.get(Q(final=False), Q(week=self.week), (Q(home=self.team) | Q(away=self.team)))
            if game.home_score == game.away_score:
                return False
            elif game.home == self.team:
                if home_score < away_score:
                    return True
                else:
                    return False
            elif game.away == self.team:
                if away_score < home_score:
                    return True
                else:
                    return False
            else:
                return False
                print ('projected issue', game)
        except ObjectDoesNotExist:
            return False



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


