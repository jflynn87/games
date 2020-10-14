import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
#from golf_app.models import Tournament, TotalScore, ScoreDetails, Field, Picks, PickMethod
from fb_app.models import Season, Week, Games, Teams, Picks, League, Player,  MikeScore, WeekScore
from django.contrib.auth.models import User
from datetime import datetime, timedelta, timezone
from django.db.models import Min, Q, Count, Sum, Max
from django.db.models.functions import ExtractWeek, ExtractYear
import time
import urllib
from urllib import request
import json
#from fb_app.scores import Scores
#from urllib.request import Request, urlopen
from selenium.webdriver import Chrome, ChromeOptions
#

#
import requests
#from linebot import LineBotApi
#from linebot.models import TextSendMessage
#from linebot.exceptions import LineBotApiError
from bs4 import BeautifulSoup
from fb_app import scrape_cbs
import pytz




#week = Week.objects.get(current=True)
start = datetime.now()
l = League.objects.get(league="Football Fools")
week = Week.objects.get(current=True)
player = Player.objects.get(name__username='TOKYO')
winners = ['DAL', 'HOU', 'NE']

for pick in Picks.objects.filter(player=player, week=week):
    if pick.team.nfl_abbr not in winners \
     and Games.objects.filter(Q(home=pick.team) | Q(away=pick.team), postponed=False).exists():
        print ('exists works: ', pick)
    else:
        print ('in else: ', pick)




print (datetime.now() - start)
exit()

f = open("picksweek4prefix.txt", "w")
for pick in Picks.objects.filter(week=week, player__league=l):
    
    f.write(pick.player.name.username + ',' + str(pick.pick_num) + ',' + str(pick.team.nfl_abbr) + '\n')
    #f.write('\n')
f.close()
    
    


for player in Player.objects.filter(league=l).order_by('name'):
    prior_pick = Picks.objects.filter(week=week, player=player).order_by('-pick_num')[0]
    for p in Picks.objects.filter(week=week, player=player).order_by('-pick_num').exclude(pick_num = prior_pick.pick_num):
        if p.pick_num + 1 == prior_pick.pick_num:
            prior_pick = p
        #print ('good', p)
        else:
            print (player.name, p.pick_num, p.team, prior_pick.pick_num, prior_pick.team)    
            prior_pick = p
        
print (Picks.objects.filter(week=week, player__league=l).count())

exit()

#d = week.update_games()
#print (len(d))
scrape_cbs.ScrapeCBS(week).get_data()
exit()

start = datetime.now()
player = Player.objects.get(name__username="john")
print (player.season_total(), type(player.season_total()))

l = League.objects.get(league='Golfers')
#print (l.season_ranks())
#exit()
week = Week.objects.get(current=True)

print (l)
#week.update_games()
#r = week.update_scores(l)
s = week.get_scores(l)

print (s)
print ('dur: ', datetime.now() - start)
exit()


week = Week.objects.get(current=True)
eastern = pytz.timezone('America/New_York')

for game in Games.objects.filter(week=week):
    print (game.eid, game.game_time)
    est = game.game_time.astimezone(eastern)
    print (est)
    
exit()




game_dict = {}
week = Week.objects.get(current=True)
game = Games.objects.get(week=week, eid='20201MINGB')
game.final = False
game.tie = False
game.save()

#web = scrape_cbs.ScrapeCBS().get_data()

exit()

html = urllib.request.urlopen("https://www.cbssports.com/nfl/scoreboard/")
soup = BeautifulSoup(html, 'html.parser')

games = soup.find_all('div', {'class': 'single-score-card'})

for game in games:
    teams = game.find_all('a', {'class': 'helper-team-name'})
    scores = game.find_all('td', {'class': 'total-score'})
   
    if teams != None and len(teams) == 2:
      #print(teams)
      away_team = Teams.objects.get(long_name=teams[0].text)
      home_team = Teams.objects.get(long_name=teams[1].text)
      if len(scores) == 2:
        away_score = scores[0].text
        home_score = scores[1].text
      else:
        away_score = 0
        home_score = 0
      
    status = game.find('div', {'class': 'game-status'})
    if status != None:
        qtr = status.text.lstrip().rstrip()

    game_dict[str(week.season_model.season) + str(week.week) + str(home_team.nfl_abbr) + str(away_team.nfl_abbr)]  = {
        'home': home_team.nfl_abbr,
        'home_score': home_score,
        'away': away_team.nfl_abbr,
        'away_score': away_score,
        'qtr': qtr
    }
        
print (game_dict)
        

exit()
print (games)

exit()

try:

    html = urllib.request.urlopen("https://nypost.com/sports/")
    soup = BeautifulSoup(html, 'html.parser')

    score_board = (soup.find("div", {'class':'widget_nypost_scoreboard_widget'}))

    nfl_sect = (soup.find("div", {'id':'NFL'}))

    games = (nfl_sect.find_all("div", {'class': 'sport-score'}))

    for row in games:
        #print ('-------------------------------------------')
        print (row)
        teams = row.find_all("div", {"class": "sport-score-team"})
        scores = row.find_all('div', {'class': 'sport-score-total'})
        for t in teams:
            print ('row', t)
            if 'home' in t.get('class'):
                home = t.text
                #print (row.get("div", {"class": "sport-score-total home"}))
                #home_score = row.find("div", {"class": "sport-score-total home"}).text
                #print (home, home_score)
            elif 'visiting' in t.get('class'):
                away = t.text
                #print (row.find("div", {"class": "sport-score-total visiting"}))
                #away_score = row.find("div", {"class": "sport-score-total visiting"})
            else:
                print ('score data issue?', t) 
        for s in scores:
            print ('score', s)
            if 'home' in s.get('class'):
                home_score = s.text
            elif 'visiting' in s.get('class'):
                away_score = s.text
            else:
                print ('score data issue?', s) 
        qtr = row.find("div", {"class": "sport-score-status"}).text

        games_dict[home+away] = {'home': home, 'away': away, 'qtr': qtr, 'home_score': home_score, 'away_score': away_score}

except Exception as e:
        print ('NY Post failed going to NFL.com')

        #try:

        html = urllib.request.urlopen("https://nytimes.stats.com/fb/scoreboard.asp")
        soup = BeautifulSoup(html, 'html.parser')

        score_board = (soup.find("div", {'id':'shsScoreboard'}))

        #cols =score_board.find_all('div', {'class': 'shsScoreboardCol'})
        #print (cols, len(cols))

        games_sect = score_board.find_all('div', {'class': 'shsScoreboardCol'}) 
        
        for game in games_sect:
            game_data = {}
            i = 1
            while i < 4:
                for line in game.find_all('td', {'class': 'shsNamD'}):
                    try:
                        if i == 1:
                            game_data = {'qtr': line.text}
                        elif i == 2:
                            game_data.update({'away': line.text})
                            print (line.text)
                            away_short = Teams.objects.get(long_name=line.text)
                            game_data.update({'away_score': game.find_all('td', {'class': 'shsTotD'})[9].text})
                        elif i == 3:
                            game_data.update({'home': line.text})
                            home_short = Teams.objects.get(long_name=line.text)
                            game_data.update({'home_score': game.find_all('td', {'class': 'shsTotD'})[14].text})
                        i += 1 
                        print(game_data)
                    except Exception as e:
                        i += 1
                        print (e)

            game_dict[str(week.season_model.season) + str(week.week) + home_short + away_short] = game_data
            
            print (game_dict)

        #print (len(games_sect))
        #for col in cols:
        #    print ('===================================')
       #    print (col.find_all('td', {'class': 'shsNamD'})) 
            

        #print(cols)


            

            
            #options = ChromeOptions()
            #options.add_argument("--headless")
            #options.add_argument("--disable-gpu")
            #driver = Chrome(options=options)
                
            #driver.get(url)
            #time.sleep(10)
            #g = driver.find_elements_by_class_name("nfl-c-matchup-strip__left-area")
            #main = driver.find_element_by_class_name("css-37urdo")
         #   soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            
         #   games_sect = soup.find('div', {'class': 'score-strip-list-container'})

            #games = games_sect.find_all('div', {'class': 'score=strip-game'})

          #  print (games_sect)
            

       # except Exception as e:
        #    print ('exception with NFL com scrape', e)




#finally:
#        driver.quit()




