from fb_app.models import Teams
import urllib3.request
from bs4 import BeautifulSoup

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Spreads(object):

    def get_spreads():

    try:

        html = urllib.request.urlopen("https://nypost.com/odds/")
        soup = BeautifulSoup(html, 'html.parser')

        nfl_sect = (soup.find("div", {'class':'odds__table-outer--1'}))
    
    #pull out the games and spreads from the NFL section
    
    
        for row in nfl_sect.find_all('tr')[1:]:
            
            try:
            col = row.find_all('td')
            teams = col[0].text.split()
            line = col[5].text.split()

            if line[0][0] == '-':
                fav = teams[0]
                dog = teams[1]
                spread = line[0]
                #print ('o/a', line[1])
            else:
                fav = teams[1]
                dog = teams[0]
                spread = line [1]
                #print ('o/a', line[0])

            fav_obj = Teams.objects.get(long_name__iexact=fav)
            dog_obj = Teams.objects.get(long_name__iexact=dog)
            
            week = Week.objects.get(current=True)
            
            if Games.objects.filter(Q(week=week) & Q(home=fav_obj) & Q(away=dog_obj)).exists():
                Games.objects.filter(Q(week=week) & Q(home=fav_obj) & Q(away=dog_obj)).update(fav=fav_obj, dog=dog_obj, spread=spread)
            elif Games.objects.filter(Q(week=week) & Q(home=dog_obj) & Q(away=fav_obj)).exists():
                Games.objects.filter(Q(week=week) & Q(home=dog_obj) & Q(away=fav_obj)).update(fav=fav_obj, dog=dog_obj, spread=spread)
            except Exception as e:
                print (fav, dog)
                print ('spread look up error', e)

        except Exception as e:
                print ('NY Post failed', e)

    return
