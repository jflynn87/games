import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")
#import django
#django.setup()
from golf_app.models import Tournament, TotalScore, ScoreDetails, Picks, PickMethod, BonusDetails, \
        Season, Golfer, Group, Field, ScoreDict, AuctionPick, AccessLog, StatLinks, CountryPicks, \
         FedExSeason, FedExField, FedExPicks
from django.contrib.auth.models import User
from datetime import date, datetime, timedelta
from golf_app import populateField, utils


def update_score_dicts():
    for t in Tournament.objects.all():
        if not t.special_field():
            if ScoreDict.objects.filter(tournament=t).exists():
                sd = ScoreDict.objects.get(tournament=t)
                if sd.data.get('info'):
                    continue
                    #print ('OK: ', t.season, t.name)
                else:
                    try:
                        print ('SD but no info: ', t.season, t.name, t.espn_t_num, Tournament.objects.filter(season__season='2021', pga_tournament_num=t.pga_tournament_num).values('espn_t_num'))
                        populateField.prior_year_sd(t, True)
                        sd = ScoreDict.objects.get(tournament=t)
                    except Exception as e:
                        print (t, e)
                    #populateField.prior_year_sd(t)
            else:
                try:
                    print ('No SD: ', t.season, t.name, t.espn_t_num, Tournament.objects.filter(season__season='2021', pga_tournament_num=t.pga_tournament_num).values('espn_t_num'))
                    populateField.prior_year_sd(t, True)
                    sd = ScoreDict.objects.get(tournament=t)
                except Exception as e:
                    print (t, e)
            #print('CUTS: ', len({k:v for k,v in sd.data.items() if v.get('rank') == 'CUT'}))
            #print ('INFO and winner: ', sd.data.get('info'), {k:v for k,v in sd.data.items() if v.get('rank') == '1'})

def check_sd():
    print ("XXXXXXXX  Starting checks")

    for t in Tournament.objects.all():
        if not t.special_field():
            sd = ScoreDict.objects.get(tournament=t)
            if abs(Field.objects.filter(tournament=t).count() - (len(sd.data.keys()) -1)) > 5:
                field = Field.objects.filter(tournament=t).values_list('playerName', flat=True)
                sd_names = [k for k,v in sd.data.items() if k != 'info']
                print (t.season, t)
                print ('Field len: ', Field.objects.filter(tournament=t).count())
                print ('SD length: ', len(sd.data.keys()))
                print ('In SD, not in field: ', {k for k,v in sd.data.items() if k != 'info' and k not in field})
                print ("In Field, not in SD: ", Field.objects.filter(tournament=t).exclude(playerName__in=sd_names))

    print (("XXXXXXXX  end of  checks"))


update_score_dicts()
check_sd()