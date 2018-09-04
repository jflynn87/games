import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","fb_proj.settings")

import django
django.setup()
from fb_app.models import Week, Games, Teams

def dump_teams():

     team = Teams.objects.get(nfl_abbr__iexact="nYg")
     print (team.get_mike_abbr())

    #print (Teams.objects.get(nfl_abbr="NYG")
    # f = open("teams.txt", "w")
    # for team in Teams.objects.all():
    #     data = str(team.mike_abbr) + ',' + str(team.nfl_abbr) + ',' + str(team.long_name) + ',' + str(team.typo_name)
    #     f.write(data)
    #     f.write("\n")
    # print (f)
    # f.close()

dump_teams()
