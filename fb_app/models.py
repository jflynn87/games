from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

import datetime
import urllib3
import urllib
import json
import scipy.stats as ss
from django.db.models import Q

# Create your models here.

class Week(models.Model):
    season = models.CharField(max_length=30)
    week = models.PositiveIntegerField()
    game_cnt = models.PositiveIntegerField()
    current = models.BooleanField(default=False)
    #start_date = models.DateField()
    #end_date = models.DateField()

    def __str__(self):
        return str(self.week)

    def save(self, *args, **kwargs):
        for league in League.objects.all():
            scores = WeekScore()
            calc_scores = calc_scores(scores, league, self)

        if self.current==True:
            last_week = Week.objects.get(current=True)
            last_week.current = False
            last_week.save()
        super(Week, self).save()


#class TeamManager(models.Manager):
#    def as_choices(self):
#        for team in self.all():
#            yield (team.pk, force_text(nfl_abbr))


class Teams(models.Model):
    mike_abbr = models.CharField(max_length=4, null=True)
    nfl_abbr = models.CharField(max_length=4, null=True)
    long_name = models.CharField(max_length=30, null=True)
    typo_name = models.CharField(max_length=30,null=True, blank=True)
    typo_name1 = models.CharField(max_length=30,null=True, blank=True)
    wins = models.PositiveIntegerField(default=0)
    losses = models.PositiveIntegerField(default=0)
#    objects = TeamManager()

    class Meta:
        ordering = ('nfl_abbr',)

    def __str__(self):
        return str(self.nfl_abbr)


    def get_mike_abbr(self):
        return self.mike_abbr



class Games(models.Model):
    eid = models.CharField(max_length=30)
    week = models.ForeignKey(Week,on_delete=models.CASCADE, db_index=True)
    fav = models.ForeignKey(Teams, on_delete=models.CASCADE,null=True, related_name='fav')
    dog = models.ForeignKey(Teams, on_delete=models.CASCADE,null=True, related_name='dog')
    home = models.ForeignKey(Teams, on_delete=models.CASCADE,null=True, related_name='home', db_index=True)
    away = models.ForeignKey(Teams, on_delete=models.CASCADE,null=True, related_name='away', db_index=True)
    opening = models.CharField(max_length=10, null=True)
    spread = models.CharField(max_length=10,null=True)
    winner = models.ForeignKey(Teams, on_delete=models.CASCADE,null=True, related_name='winner')
    loser = models.ForeignKey(Teams, on_delete=models.CASCADE,null=True, related_name='loser')
    final = models.BooleanField(default=False)
    home_score = models.PositiveIntegerField(null=True)
    away_score = models.PositiveIntegerField(null=True)
    qtr = models.CharField(max_length=5, null=True)
    tie = models.BooleanField(default=False)
    date = models.DateField(null=True)
    time = models.CharField(max_length=20, null=True)
    day = models.CharField(max_length=10, null=True)

    def __str__(self):
        return str(self.home) + str(self.away)

    class Meta:
        index_together = ['week', 'home', 'away']



    #def get_game_id(self):
    #    return self.eid

class League(models.Model):
    league = models.CharField(max_length=30)

    def __str__(self):
        return self.league

class Player(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    name = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


    def __str__(self):
        return str(self.name)

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
            elif game.tie:
                return True
            else:
                print ('something wrong in is_loser')
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



def calc_scores(self, league, week, loser_list=None, proj_loser_list=None):

    print ('starting nfl json lookup')
    print (datetime.datetime.now())
    print (week)

    if Games.objects.filter(week=week).exclude(final=True).exists():
        json_url = 'http://www.nfl.com/liveupdate/scores/scores.json'

        with urllib.request.urlopen(json_url) as field_json_url:
            data = json.loads(field_json_url.read().decode())

        #use for testing
        #with open ('c:/users/john/pythonProjects/games/gamesProj/fb_app/nfl_scores.json') as f:
        #    data = json.load(f)

        try:
                for score in Games.objects.filter(week=week).exclude(final=True):
                    home_score = data[score.eid]['home']['score']['T']
                    home_team = data[score.eid]['home']["abbr"]
                    away_team = data[score.eid]['away']["abbr"]
                    away_score = data[score.eid]['away']['score']['T']
                    qtr = data[score.eid]["qtr"]

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

                    setattr(score, 'home_score',home_score)
                    setattr(score, 'away_score',away_score)
                    setattr(score, 'winner', winner)
                    setattr(score, 'loser', loser)
                    setattr(score, 'qtr',qtr)
                    if qtr == "Final":
                        setattr(score, 'final', True)
                        setattr(score, 'tie', tie)
                    elif qtr == "final overtime":
                        setattr(score, 'final', True)
                        setattr(score, 'tie', tie)
                    else:
                        setattr(score, 'tie', False)

                    score.save()


        except KeyError:
                print ('NFL score file not ready for the week')
                pass

    print ('player and score object creation start')
    print (datetime.datetime.now())
    scores_list = []
    projected_scores_list = []
    total_score_list = []
    scores = {}
    score = 0
    proj_scores = {}
    proj_score = 0

    #for player in player_list:
    for player in Player.objects.filter(league=league):
        scores[player]=score
        proj_scores[player] = proj_score
    for game in Games.objects.filter(week=week, final=True):
        if game.tie:
            picks = Picks.objects.filter(Q(team=game.home) | Q(team=game.away), week=week, player__league=league)
        else:
            picks = Picks.objects.filter(team=game.loser, player__league=league, week=week)
        for loser in picks:
            score = scores.get(loser.player)
            scores[loser.player]= score + loser.pick_num
    print (scores)

    if proj_loser_list != None:
        for team in proj_loser_list:
            team_obj = Teams.objects.get(nfl_abbr=team)
            picks = Picks.objects.filter(team=team_obj, player__league=league, week=week)
            for loser in picks:
                print (loser.pick_num, loser.team, loser.player)
                proj_score = proj_scores.get(loser.player)
                proj_scores[loser.player]= proj_score + loser.pick_num
        print ('there', proj_scores)
    else:
        for game in Games.objects.filter(week=week, final=False):
            picks = Picks.objects.filter(team=game.loser, player__league=league, week=week)
            for loser in picks:
                proj_score = proj_scores.get(loser.player)
                proj_scores[loser.player]= proj_score + loser.pick_num
        print ('here', proj_scores)

    for player in Player.objects.filter(league=league):
        score_obj, created = WeekScore.objects.get_or_create(player=player, week=week)
        score = scores.get(player)
        projected_score = proj_scores.get(player)

        setattr (score_obj, "score", score)
        setattr (score_obj, "projected_score", projected_score)
        score_obj.save()

        scores_list.append(score)
        projected_scores_list.append(score + projected_score)

        #calculate season totals
        total_score = 0

        for weeks in WeekScore.objects.filter(player=player, week__week__lte=week.week):
            if weeks.score == None:
                weeks.score = 0
            total_score += weeks.score
        total_score_list.append(total_score)


    ranks = ss.rankdata(scores_list, method='min')
    projected_ranks = ss.rankdata(projected_scores_list, method='min')
    season_ranks = ss.rankdata(total_score_list, method='min')
    print ('sending context')
    print (datetime.datetime.now())

    return (scores_list, ranks, projected_scores_list, projected_ranks, total_score_list, season_ranks)
