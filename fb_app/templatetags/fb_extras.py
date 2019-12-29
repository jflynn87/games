from django import template
#from golf_app.models import Picks, mpScores, Field, Tournament, Group
#from django.db.models import Count
#from string import ascii_letters
#import re
#mport urllib
#from bs4 import BeautifulSoup


register = template.Library()

@register.filter
def check_final(qtr):
    if qtr[0:5] in ['final', 'Final']:
        return True
    else:
        return False

