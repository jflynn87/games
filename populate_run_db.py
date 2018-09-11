from __future__ import print_function
import httplib2
import os
import urllib3

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from run_app.models import Run, Shoes

from googleapiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    """
    import time
    import datetime
    #import mysql.connector


    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    #spreadsheetId = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
    #rangeName = 'Class Data!A2:E'
    spreadsheetId = '1iWIbqFR1vW0cDTGRvo3ys1tTJdBt0LJkYhN7VTH1YTI'
    rangeName = 'actual!C76:H'

    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    rowcount = 0
    dist = 0.0
    runtime = 0
    cals = 0
    data = ' '
    runs18 = 0
    dist18 = 0

    if not values:
        print('No data found.')
    else:
        f = open('runs.txt', 'w' )
        for row in values:
            # get cols c - h for rows with runs.  Converts time to seconds for all rows, dealing wiht multiple formats.  writes to a file and prints totals for all runs.
            #print('%s, %s' % (row[0], (row[1])))
            try:
                if row[1] not in ("#N/A", '0', ' '):
                    #print (row)
                    data = ([row[0], row[1], convert2secs(row[2]), row[3], row[4], row[5]])
                    #f.write(str(data))
                    #cursor.execute
                    run = Run()
                    #run.date = row[0]
                    run.date = datetime.datetime.strptime(row[0], '%m/%d/%Y')
                    run.dist = row[1]
                    duration = convert2secs(row[2])
                    run.time = datetime.timedelta(seconds=duration)
                    run.cals = row[3]
                    run.location = row[4]
                    shoe = Shoes.objects.get(name__iexact=row[5])
                    run.shoes = shoe
                    print (row)
                    run.save()
                    rowcount += 1
                    dist += float(row[1])
                                        #timeParts = [int(s) for s in row[2].split(':')]
                    #if timeParts[0] < 5:
                    #    runtime +=(timeParts[0] * 60+ timeParts[1]) *60 + timeParts[2]
                    #    print ((timeParts[0] * 60+ timeParts[1]) *60 + timeParts[2])
                    #else:
                    #    runtime +=((timeParts[0] *60)+ timeParts[1])
                    #    print (((timeParts[0] *60)+ timeParts[1]))
                    runtime += convert2secs(row[2])
                    cals += int(row[3])
                    #if row[4] =='tm' and row[1] == '10':
                    #    print (([row[0], row[1], row[2], row[3], row[4], row[5]]))
                    if datetime.datetime.strptime(row[0],'%m/%d/%Y') > datetime.datetime.strptime('12/16/2017', '%m/%d/%Y'):
                        runs18 += 1
                        dist18 += float(row[1])

            except IndexError:
                #continue
                print (row, "no run")
                #print (row[0], "'no run'")
        print('number of runs: ' + str(rowcount))
        print ('total dist: ' + str(dist))
        print ('total time: ' + str(datetime.timedelta(seconds=runtime)))
        print ('total cals: ' + str(cals))
        print('2018 marathon training:')
        print ('2018 runs: ' + str(runs18))
        print ('2018 dist: ' + str(dist18))
        f.close()

def convert2secs(ssTime):
    ''' takes in a string with a time time from the spreadsheet, assumes if the first part is less than 5  that equates to hours.  If more than 5, mins.  Conversts all to seconds and returns a string of the seconds.'''
    runtime = 0

    timeParts = [int(s) for s in ssTime.split(':')]
    if timeParts[0] < 5:
        return((timeParts[0] * 60 + timeParts[1]) * 60 + timeParts[2])
    else:
        return(((timeParts[0] * 60) + timeParts[1]))


def getSchedule():
    import urllib.request
    from bs4 import BeautifulSoup

    html = urllib.request.urlopen("http://halhigdon.com/training/51138/Marathon-Novice-2-Training-Program")
    soup = BeautifulSoup(html, 'html.parser')

    schedule = (soup.find("table", {'class': 'table-training'}))

#    for schedule.find_all('tr'):
#        print




#if __name__ == '__main__':
#    main()
main()
