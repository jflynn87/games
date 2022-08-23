from fb_app.models import Games, Week, Teams, Season
from django.db.models import Count
import requests
#from datetime import datetime, timezone




def load_sched(payload=None, nfl_season=None):
    '''takes an optional string for api payload'''

    #changing weeks to load preseason weeks (make week 0 and cnt 1)
    season = Season.objects.get(current=True)
    if Week.objects.filter(current=True).exists():
        current_week = Week.objects.get(current=True)
        week_cnt = current_week.week + 1
    elif Week.objects.filter(season_model=season).exists():  #figure out if this is best way , especially for playoffs
        w = Week.objects.filter(season_model=season).last()
        week_cnt = w.week + 1
    else:
        week_cnt = 1

    print (season, week_cnt)
    
    #week_cnt = current_week.week + 1
    
    if payload:
        max_week = payload
    else:
        max_week = week_cnt + 1

    if not nfl_season:
        nfl_season = "REG"

    d = {}

    while week_cnt < int(max_week):
            try:
                week, created = Week.objects.get_or_create(season_model=season, week=week_cnt)
                print ('model week: ', week.week, week.current)
                #week.season = season.season
                if not week.current and week.week != 1:
                    week.current = False
                else:
                    week.current = True
                week.season = season.season
                #week.week = week_cnt
                week.game_cnt = 0
                week.save()

                #if week_cnt > 17:
                #    url_week = 'post' + str(week_cnt - 17)
                #else:
                #    url_week = 'reg' + str(week_cnt)

                headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
                url = "http://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
                
                if week.week < 19 and nfl_season == 'REG': 
                
                    payload = {'week': str(week_cnt)}
                    #payload = {}  #works for pre season/current week?
                    print ('payload ', payload)
                    
                else:
                    payload = {}  #works for preseason and post season
                json_data = requests.get(url, headers=headers, params=payload).json()
                #print (json_data)
                #print (json_data.keys())
                print ('espn week: ', json_data.get('week'))
                print ('espn season type: ', json_data.get('season'))
                for l in json_data.get('events'):
                    print (l.get('name'))
                    for competition in l.get('competitions'):
                        for c in competition.get('competitors'):
                            print (c.get('homeAway'), c.get('team').get('name'))
                            if c.get('team').get('name'):
                                t_name = c.get('team').get('name')
                            elif c.get('team').get('displayName') == "Washington":
                                t_name = "Football Team"
                            else:
                                raise Exception('uknown team: ', c.get('team'))                        
                                
                            if c.get('homeAway') == 'home':
                                home = Teams.objects.get(long_name=t_name)
                            elif c.get('homeAway') == "away":
                                away = Teams.objects.get(long_name=t_name)
                            else:
                                raise Exception('uknown value in home/away: ', c.get('homeAway'))                        

                        #game_time = competition.get('date')

                        game, created = Games.objects.get_or_create(week=week, home=home, away=away)
                        game.week = week
                        game.eid = competition.get('id')
                        game.away = away
                        game.home = home
                        #game_time = competition.get('date')
                        #print ('game tiem', game_time)

                        game.game_time = competition.get('date')
                        #game.day = game_dow
                        game.qtr = 'pregame'

                        game.save()

                week.game_cnt = Games.objects.filter(week=week).count()
                week.save()
                
                d[week.week] = {'msg': 'week good'}
            except Exception as e:
                print ('exception with scrape', str(e))
                d[week.week] = {'msg': str(e)}
                
            finally:
                week_cnt +=1

    return d

