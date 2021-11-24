import os

#from gamesProj.golf_app.models import ScoreDetails
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
#from golf_app import espn_api
from golf_app.models import Tournament, TotalScore, ScoreDict
from datetime import datetime, timedelta
import json
from golf_app import views, espn_api
from urllib.request import Request
import pytz
#from urllib.request import urlopen
#from requests import Session


start = datetime.now()
t = Tournament.objects.get(current=True)

if t.complete:
    print (t, 'tournament complete')
    exit()

sd = ScoreDict.objects.get(tournament=t)

if sd.espn_api_data:
    saved_espn = espn_api.ESPNData(data=sd.espn_api_data)
    
    print ((sd.updated + timedelta(minutes = 10)), datetime.utcnow().replace(tzinfo=pytz.utc))
    if saved_espn.first_tee_time() > datetime.utcnow():  
        print ('before first tee time, exiting')
        exit()
    elif saved_espn.get_round_status() in ['pre', 'post'] and \
        (sd.updated + timedelta(minutes = 10)) > datetime.utcnow().replace(tzinfo=pytz.utc):  #changed from 10 to 0 for testing
        print ('wait 10 mins to update before/after round') 
        exit()



if not t.started():
    print ('not started, exiting')
    exit()
elif not t.picks_complete():
    t.missing_picks()


if os.environ.get('DEBUG'):
    domain = '127.0.0.1:8000'
else:
    domain = 'jflynn87.pythonanywhere.com'

scrape_url = 'http://' + domain + '/golf_app/get_scores/' 
scrape_req = Request(scrape_url)
scrape_data = views.GetScores().get(scrape_req, t.pk)

api_req = Request('http://' + domain + '/golf_app/espn_api_scores/' + t.pga_tournament_num)
data = views.EspnApiScores().get(api_req, t.pga_tournament_num)
d = json.loads(data.content)
print (d)

for ts in TotalScore.objects.filter(tournament=t):
    if ts.score == d.get(ts.user.username).get('score'):
        print (ts.user, ' : match')
    else:
        print (ts.user, ': mismatch : ', ts.score, d.get(ts.user.username).get('score'))

print ('durtion: ', datetime.now() - start)

exit()
