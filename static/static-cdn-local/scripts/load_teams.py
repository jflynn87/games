import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","fb_proj.settings")

import django
django.setup()
from fb_app.models import Week, Games, Teams
import urllib3
from bs4 import BeautifulSoup
import urllib.request



def load_teams():
    # import urllib3.request
    # from bs4 import BeautifulSoup
    #
    # html = urllib.request.urlopen("https://nypost.com/sports/")
    # soup = BeautifulSoup(html, 'html.parser')
    #
    # #find nfl section within the html
    #
    # nfl_sect = (soup.find("div", {'id': 'line-nfl'}))
    # #nfl_sect = (soup.find("div", {'id': 'line-mlb'}))
    #
    #
    # #pull out the games and spreads from the NFL section
    #
    # spreads = {}
    # sep = ' '
    #
    # for row in nfl_sect.find_all('tr')[1:]:
    #      col = row.find_all('td')
    #      fav = col[0].string
    #      opening = col[1].string
    #      spread = col[2].string.split(sep, 1)[0]
    #      dog =  col[3].string
    #      team1 = Teams()
    #      team2 = Teams()
    #      team1.long_name = (fav.lower())
    #      team2.long_name = (dog.lower())
    #      team1.save()
    #      team2.save()

    f=open('teams.txt',"r")
    sep = ','

    for line in f:
        team = Teams()
        team_list= []
        team_list = line.split(sep)
        team.mike_abbr = team_list[0]
        team.nfl_abbr = team_list[1]
        team.long_name = team_list[2]
        team.typo_name = team_list[3].strip("\n")
        team.typo_name1 = None
        team.wins = 0
        team.loses = 0
        print (team, team.typo_name)

        team.save()



if __name__ == '__main__':
    print ('populating script!')
    #clean_db()
    load_teams()
    print ("Populating Complete!")
