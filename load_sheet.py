import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from fb_app.models import Week, Player, Picks, Teams, MikeScore, WeekScore, League
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from fb_app import validate_picks


def readSheet(file,numPlayers):
        '''takes a pick file and updates week, owner list and picsk'''
        from bs4 import BeautifulSoup

        xml = open(file,encoding="utf8")
        soup = BeautifulSoup(xml,"xml")

        sheet = []
        picks = {}

        #test this for a single digit week....This gets the week from the start of the shhet
        week = []
        print (soup.findAll('t'))
        for data in soup.findAll('t')[0:1]:
        #for data in soup.findAll('t')[1]:
            week.append(data.text)
        week_str = ''.join(week)
        print ('week: ' + week_str)


        app_week = Week.objects.get(current=True)
        if app_week.week == 1:
            mike_score_week = app_week
        else:
            mike_score_week = Week.objects.get(season_model__current=True, week=app_week.week - 1)
        

        if str(app_week.week) != week_str:
            print ("sheet week doesn't match model", week_str, app_week.week)
            exit()
        elif Picks.objects.filter(player__league__league="Football Fools", week=app_week):
            print ('deleting picks')
            Picks.objects.filter(player__league__league="Football Fools", week=app_week).delete()
            MikeScore.objects.filter(player__league__league="Football Fools", week=app_week).delete()


        #create a sheet with just players, picks and totals (totals assumes that the total is 2 digits and more than 16).

        for tag in soup.findAll('t'):
            if tag.text not in (' ', '1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16', '17'):
                if len(tag.text) > 1:
                    if tag.text == "LiL":
                        sheet.append("LiL B")
                    elif tag.text == "B":
                        print (tag.text)
                    else:
                        sheet.append(tag.text)

        sheet_scores = True
        print (len(sheet))
        print (sheet)
        if len(sheet)/numPlayers == app_week.game_cnt + 2:
            print ('full sheet')
        elif len(sheet)/numPlayers == app_week.game_cnt +1:
            print ('scores missing')
            sheet_scores = False
        else:
            print ('bad sheet')
            exit()

        try:
            league = League.objects.get(league="Football Fools")
            Picks.objects.filter(week=app_week, player__league=league).delete()
            print ('deleting picks on rerun')
        except Exception as e:
            print ("no picks exists, proceeding", e)
            exit()

        player_i = 0
        pick_list = []
        while player_i < numPlayers:
            player = sheet[player_i]
            #print (player)
            #winner = 1
            print ('player', player)
            user = User.objects.get(username=player)
            player = Player.objects.get(name=user)
            if sheet_scores:
                scores = MikeScore()
                scores.week = mike_score_week
                scores.player = player
                scores.total = sheet[(player_i + (numPlayers * app_week.game_cnt) + numPlayers)]
                scores.save()

                my_total = 0
                for score in WeekScore.objects.filter(week__lte=mike_score_week, player=player, week__season_model__current=True):
                    my_total += score.score


                if int(my_total) != int(scores.total):
                    print ("score mismatch", player, my_total, scores.total)
                else:
                    print ("score good", player, my_total, scores.total)


            i = 1
            while i <= app_week.game_cnt:
                pick = sheet[(player_i + (numPlayers * i))]
                #game.append(sheet[(player_i + (numPlayers * i))])
                #picks[player] = game

                try:
                    pick_team = Teams.objects.get(mike_abbr=pick)
                except ObjectDoesNotExist:
                    #print ('mike abbr not found', player, pick)
                    try:
                        pick_team = Teams.objects.get(typo_name=pick)
                    except ObjectDoesNotExist:
                        print (str(pick) + str(player))
                        pick_team = Teams.objects.get(typo_name1=pick)
                except Exception as e:
                        print (e)
                        print ('pick exception' + str(player) + str(pick))



                sheet_picks = Picks()
                sheet_picks.player = player
                sheet_picks.week = app_week
                sheet_picks.pick_num = (17 - i)
                sheet_picks.team = pick_team
                sheet_picks.save()
                pick_list.append(str(pick_team))
                #print (player, pick_list)
                i += 1

            picks_check = validate_picks.validate(pick_list, app_week)
            if not picks_check[0]:
                print (str(player), picks_check[0], picks_check[1])
            else:
                print ('picks valid', str(player))

            pick_list = []
            player_i +=1



readSheet('21-22 FOOTBALL FOOLS.xml', 25)
