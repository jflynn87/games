from django import template
from fb_app.models import Season
#from django.db.models import Count
#from string import ascii_letters
#import re
#mport urllib
#from bs4 import BeautifulSoup


register = template.Library()

@register.filter
def check_final(qtr):
    if qtr != None and qtr[0:5] in ['final', 'Final']:
        return True
    else:
        return False


