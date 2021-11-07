import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from golf_app.models import Tournament, TotalScore
from datetime import date, datetime, timedelta
import json
from golf_app import views
from urllib.request import Request
from urllib.request import urlopen
from requests import Session

t = Tournament.objects.get(current=True)

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

# espn = espn_api.ESPNData().all_data

# with open('espn_api_r1_complete.json', 'w') as convert_file:
#      convert_file.write(json.dumps(espn))


exit()
