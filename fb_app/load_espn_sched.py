from fb_app.models import Games, Week, Teams, Season
from django.db.models import Count
from fb_app import espn_data
#import requests

#from datetime import datetime, timezone




def load_sched(payload=None, nfl_season_type=None):
    '''takes an optional string for api payload'''

    #changing weeks to load preseason weeks (make week 0 and cnt 1)
    season = Season.objects.get(current=True)
    if Week.objects.filter(season_model__current=True, current=True).exists():
        current_week = Week.objects.get(current=True)
        week_cnt = current_week.week + 1
    elif Week.objects.filter(season_model=season).exists():  #figure out if this is best way , especially for playoffs
        w = Week.objects.filter(season_model=season).last()
        week_cnt = w.week + 1
    else:
        if Week.objects.filter(current=True).exists():
            w = Week.objects.get(current=True)
            w.current = False
            w.save()
            
        week_cnt = 1

    print (season, week_cnt)
    
    #week_cnt = current_week.week + 1
    
    if payload:
        max_week = payload
    else:
        max_week = week_cnt + 1

    if not nfl_season_type:
        nfl_season_type = "REG"
    
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
                #week.week = str(season.season)
                week.week = week_cnt
                week.game_cnt = 0
                week.save()

                if nfl_season_type == 'REG':
                    p = week_cnt
                else:
                    p = None

                espn =  espn_data.ESPNData(payload=p, nfl_season_type=nfl_season_type)
                print ('espn data len', len(espn.get_data()))
                for k, v in espn.get_data().items():
                        print (k, v, week)
                        game, created = Games.objects.get_or_create(eid=k, week=week)
                        game.away = Teams.objects.get(nfl_abbr=v.get('away'))
                        game.home = Teams.objects.get(nfl_abbr=v.get('home'))
                        game.game_time = v.get('game_date')
                        game.qtr = 'pregame'
                        game.save()

                if Games.objects.filter(week=week).exists():  #this doesnt work, fix at some point so not saving bad weeks.
                    week.game_cnt = Games.objects.filter(week=week).count()
                    week.regular_week = espn.regular_week()

                    week.save()
                
                d[week.week] = {'msg': 'week good'}
            except Exception as e:
                print ('exception with espn sched load', str(e))
                d[week.week] = {'msg': str(e)}
                
            finally:
                week_cnt +=1

    return d

