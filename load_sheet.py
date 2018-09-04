import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from fb_app.models import Week, Player, Picks, Teams, MikeScore
from django.contrib.auth.models import User


def readSheet(file,numPlayers):
        '''takes a pick file and updates week, owner list and picsk'''
        from bs4 import BeautifulSoup

        xml = open(file,encoding="utf8")
        soup = BeautifulSoup(xml,"xml")

        sheet = []
        picks = {}


        #test this for a single digit week....This gets the week from the start of the shhet
        week = []
        for data in soup.findAll('t')[0:1]:
            week.append(data.text)
        week_str = ''.join(week)
        print ('week: ' + week_str)

        app_week = Week.objects.get(current=True)

        if str(app_week.week) != week_str:
            print ("sheet week doesn't match model")
        elif Picks.objects.filter(player__league__league="Football Fools", week=app_week):
            Picks.objects.filter(player__league__league="Football Fools", week=app_week).delete()
            MikeScore.objects.filter(player__league__league="Football Fools", week=app_week).delete()


        #create a sheet with just players, picks and totals (totals assumes that the total is 2 digits and more than 16).

        for tag in soup.findAll('t'):
            if tag.text not in (' ', '1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16'):
                if len(tag.text) > 1:
                    sheet.append(tag.text)
        #print (sheet)

        player_i = 0
        while player_i < numPlayers:
            player = sheet[player_i]
            #winner = 1
            user = User.objects.get(username=player)
            player = Player.objects.get(name=user)
            scores = MikeScore()
            scores.week = app_week
            scores.player = player
            scores.total = sheet[(player_i + (numPlayers * 16) + numPlayers)]
            scores.save()

            i = 1
            while i <= app_week.game_cnt: #change this to the len of games from games.py
                pick = sheet[(player_i + (numPlayers * i))]
                #game.append(sheet[(player_i + (numPlayers * i))])
                #picks[player] = game

                pick_team = Teams.objects.get(mike_abbr=pick)
                sheet_picks = Picks()
                sheet_picks.player = player
                sheet_picks.week = app_week
                sheet_picks.pick_num = (17 - i)
                sheet_picks.team = pick_team
                sheet_picks.save()

                i += 1
            player_i +=1



readSheet('C:/Users/John/Documents/pooltest3.xml', 24)
