import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","fb_proj.settings")

import django
django.setup()
from fb_app.models import Games, Picks, Week, Player, WeekScore
import datetime
import urllib3
import urllib
import json
import scipy.stats as ss
from django.db.models import Q

def build_scores_context(user, league, winner_list=None):
    '''takes a user and league object and an optional list of winners.  If no
     list provided, goes to the web/db to get the winners.  updates WeekScore
      objects and returns an actual scores and projected scores list'''


        week = Week.objects.get(current=True)

        player_list = []
        pick_dict = {}
        pick_list = []
        pick_num = 16
        pick_pending = []

        #if league.league == "Football Fools":
        #    for player in Player.objects.filter(league=league):
        #        player_list.append(player)
        #else:
        #player list for header or footnote if no picks
        for player in Player.objects.filter(league=league).order_by('name'):
            if Picks.objects.filter(week=week, player=player):
                player_list.append(player)
            else:
                pick_pending.append(player)

        #gets picks for any player with picks

        while pick_num > 0:
            if Picks.objects.filter(week=week, pick_num=pick_num, player__league=league):
               for picks in Picks.objects.filter(week=week, pick_num=pick_num, player__league=league).order_by('player__name'):
                   pick_list.append(picks.team)
               pick_dict[pick_num]=pick_list
               pick_list = []
            pick_num -= 1

        print (pick_dict)
        #get scores

        #get game id's to look up score in json files
        #add a query to skip if all games are done and updated in db
        print ('starting nfl json lookup')
        print (datetime.datetime.now())
        json_url = 'http://www.nfl.com/liveupdate/scores/scores.json'

        with urllib.request.urlopen(json_url) as field_json_url:
            data = json.loads(field_json_url.read().decode())

        #use for testing
        #with open ('c:/users/john/pythonProjects/games/gamesProj/fb_app/nfl_scores.json') as f:
        #    data = json.load(f)




        try:
          #for game in Games.objects.filter(week=0):
          for game in Games.objects.filter(week=week).exclude(final=True):
            home_score = data[game.eid]['home']['score']['T']
            home_team = data[game.eid]['home']["abbr"]
            away_team = data[game.eid]['away']["abbr"]
            away_score = data[game.eid]['away']['score']['T']
            qtr = data[game.eid]["qtr"]

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
            setattr(game, 'qtr',qtr)
            if qtr == "Final":
                setattr(game, 'final', True)
                setattr(game, 'tie', tie)
            else:
                setattr(game, 'tie', False)

            game.save()


        except KeyError:
            print ('NFL score file not ready for the week')
            pass

        print ('player and score object creation start')
        print (datetime.datetime.now())
        scores_list = []
        projected_scores_list = []
        total_score_list = []
        for player in Player.objects.filter(league=league):
            print ('player ne 2018')
            score_obj, created = WeekScore.objects.get_or_create(player=player, week=week)
            #score_obj = WeekScore.objects.get_or_create(player=player, week=week)
            score = 0
            projected_score = 0

            for pick in Picks.objects.filter(player=player, week=week):

                game = Games.objects.get((Q(home=pick.team) | Q(away=pick.team)) & Q(week=week))
                if game.qtr == "Final":
                    if game.tie:
                        score += pick.pick_num
                    elif pick.team == game.loser:
                        score += pick.pick_num
                else:
                    if pick.team == game.loser:
                        projected_score += pick.pick_num

                setattr (score_obj, "score", score)
                setattr (score_obj, "projected_score", projected_score)
                score_obj.save()

            scores_list.append(score)
            projected_scores_list.append(score + projected_score)

            #calculate season totals


            total_score = 0

            for weeks in WeekScore.objects.filter(player=player, week__week__lte=week.week):
                total_score += weeks.score
            total_score_list.append(total_score)


        ranks = ss.rankdata(scores_list, method='min')
        projected_ranks = ss.rankdata(projected_scores_list, method='min')
        season_ranks = ss.rankdata(total_score_list, method='min')
        print ('sending context')
        print (datetime.datetime.now())
        print ('scores', scores_list)

        context.update({
        'players': player_list,
        'picks': pick_dict,
        'week': week,
        'pending': pick_pending,
        'games': Games.objects.filter(week=week),
        'scores': scores_list,
        'projected_ranks': projected_ranks,
        'projected_scores': projected_scores_list,
        'ranks': ranks,
        'totals': total_score_list,
        'season_ranks': season_ranks,
        })
        #print (context)
        return context  
