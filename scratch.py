import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from run_app.models import Run, Shoes
from django.db.models import Sum


def dump_teams():

    dist = Run.objects.values('shoes__name').annotate(total_dist=Sum('dist'))
    print (dist)
    #print (Teams.objects.get(nfl_abbr="NYG")
    # f = open("teams.txt", "w")
    # for team in Teams.objects.all():
    #     data = str(team.mike_abbr) + ',' + str(team.nfl_abbr) + ',' + str(team.long_name) + ',' + str(team.typo_name)
    #     f.write(data)
    #     f.write("\n")
    # print (f)
    # f.close()

dump_teams()
