#import os
#os.environ.setdefault("DJANGO_SETTINGS_MODULE","fb_proj.settings")

#import django
#django.setup()
from fb_app.models import Games, Picks, Week, Player, WeekScore

import datetime
import urllib3
import urllib
import json
import scipy.stats as ss
from django.db.models import Q

def calc_scores(league, week, loser_list=None, proj_loser_list=None):
#def calc_scores(self, league, player, week, player_list=None, pick_dict=None, loser_list=None, proj_loser_list=None):

    print ('CALC_Scores starting nfl json lookup')
    print ('before json', week)
    if Games.objects.filter(week=week).exclude(final=True).exists():
        print ('look up nfl json link')
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


        except KeyError as e:
                print ('XXXNFL file not ready for the week', e)
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
        print (proj_scores)
    else:
        for game in Games.objects.filter(week=week, final=False):
            picks = Picks.objects.filter(team=game.loser, player__league=league, week=week)
            for loser in picks:
                proj_score = proj_scores.get(loser.player)
                proj_scores[loser.player]= proj_score + loser.pick_num
        print (proj_scores)

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
