import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
#from . import port_app.models

#from datetime import datetime, timedelta
import datetime
#import sqlite3
from django.db.models import Min, Q, Count
from golf_app import calc_score
from string import ascii_lowercase
import json
import urllib.request
import time

def load_symbols():

    for c in ascii_lowercase:
        json_url = 'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=' + c + '&apikey=LMFMS9U0HUA4DV7O'
        with urllib.request.urlopen(json_url) as mktData_json_url:
            data = json.loads(mktData_json_url.read().decode())

        if data.get('Note') == None:
            for product in data['bestMatches']:
                print (product['1. symbol'] + product['2. name'])
        else:
            time.sleep(60)
            with urllib.request.urlopen(json_url) as mktData_json_url:
                data = json.loads(mktData_json_url.read().decode())
            if data.get('Note') == None:
                for product in data['bestMatches']:
                    print (product['1. symbol'] + product['2. name'])




load_symbols()
