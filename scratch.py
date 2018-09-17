import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from fb_app.models import Games, Player, Week, Picks,Teams, League
from django.db.models import Sum, Q


def dump_teams():

    league = League.objects.get(league="Football Fools")
    week = Week.objects.get(current=True)
    #player = Player.objects.get(name='john')

    scores = {}
    score = 0

    for player in Player.objects.filter(league=league):
        scores[player]=score
    for game in Games.objects.filter(week=week, final=True):
        if game.tie:
            picks = Picks.objects.filter(Q(team=game.home) | Q(team=game.away), week=week, player__league=league)
        else:
            picks = Picks.objects.filter(team=game.loser, player__league=league, week=week)
        for loser in picks:
            score = scores.get(loser.player)
            scores[loser.player]= score + loser.pick_num
            #print(loser.player, loser.pick_num, loser.team)
    #print (scores)

    proj_scores = {}
    proj_score = 0
    for game in Games.objects.filter(week=week, final=False):
        picks = Picks.objects.filter(team=game.loser, player__league=league, week=week)
        for loser in picks:
            proj_score = scores.get(loser.player)
            proj_scores[loser.player]= score + loser.pick_num
            #print(loser.player, loser.pick_num, loser.team)
    #print (proj_scores)

    for pick in Picks.objects.filter(week=week, player__league=league).order_by('-pick_num', 'player'):
        print (pick)

    #print (Teams.objects.get(nfl_abbr="NYG")
    # f = open("teams.txt", "w")
    # for team in Teams.objects.all():
    #     data = str(team.mike_abbr) + ',' + str(team.nfl_abbr) + ',' + str(team.long_name) + ',' + str(team.typo_name)
    #     f.write(data)
    #     f.write("\n")
    # print (f)
    # f.close()

dump_teams()
