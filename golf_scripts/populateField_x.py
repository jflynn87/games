import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","golfProj.settings")

import django
django.setup()
from golf_app.models import Tournament, Field, Group
import urllib3

def get_pga_worldrank():
    '''Goes to PGA web site takes no input, goes to web to get world golf rankings and returns a dictionary with player name as a string and key, ranking as a string in values'''

    from bs4 import BeautifulSoup
    import urllib.request

    html = urllib.request.urlopen("https://www.pgatour.com/stats/stat.186.html")
    #html = request.get("https://www.pgatour.com/stats/stat.186.html")
    soup = BeautifulSoup(html, 'html.parser')


    rankslist = (soup.find("div", {'class': 'details section'}))

    ranks = {}

    for row in rankslist.find_all('tr')[1:]:
        try:
            player = (row.find('td', {'class': 'player-name'}).text).strip('\n')
            rank = row.find('td').text.strip('\n').strip(' ')
            ranks[player] = int(rank)
        except Exception as e:
            print(e)

    return ranks



def get_worldrank():
    '''Goes to OWGR web site takes no input, goes to web to get world golf rankings and returns a dictionary with player name as a string and key, ranking as a string in values'''

    from bs4 import BeautifulSoup
    import urllib.request

    html = urllib.request.urlopen("http://www.owgr.com/ranking?pageNo=1&pageSize=All&country=All")
    soup = BeautifulSoup(html, 'html.parser')


    rankslist = (soup.find("div", {'class': 'table_container'}))

    ranks = {}

    for row in rankslist.find_all('tr')[1:]:
        try:
            player = (row.find('td', {'class': 'name'}).text).replace('(am)','').replace(' Jr','')
            rank = row.find('td').text
            ranks[player] = int(rank)
        except Exception as e:
            print(e)

    return ranks



def get_field():
    '''takes no input, goes to web to get world golf rankings and returns a list with player names'''

    from bs4 import BeautifulSoup
    import json
    import urllib.request

    try:
        f = open("config.txt", "r")
        for line in f:
            if "Field URL" in line:
                json_url = line[12:]
                print (json_url)
                break


    except  Exception:
        print (e)

    with urllib.request.urlopen(json_url) as field_json_url:
        data = json.loads(field_json_url.read().decode())


    field_list = {}


    for player in data["Tournament"]["Players"][0:]:
        name = (' '.join(reversed(player["PlayerName"].split(', ')))).replace('Jr. ','')
        try:
            if player["isAlternate"] == "Yes":
                #exclude alternates from the field
                alternate = True
            else:
                alternate = False
                field_list[name] = alternate
        except IndexError:
            alternate = False
            print (player + 'alternate lookup failed')




    return field_list


def configure_groups(field_list):
    '''takes a list, calculates the number of groups and players per group'''


    group_size = 10
    group_cnt = 1
    groups = {}

    while group_cnt <6:
        groups[group_cnt] = group_size
        group_cnt += 1

    group_size = 15
    remainder = (len(field_list)-50) % group_size

    remaining_groups = (len(field_list)-(remainder+50))/group_size

    while group_cnt < remaining_groups + 5:
         groups[group_cnt] = group_size
         group_cnt += 1

    if remainder == 0:
        groups[group_cnt] = group_size
    else:
        groups[group_cnt] = group_size + remainder


    for k,v in groups.items():
         Group.objects.get_or_create(number=k,playerCnt=v)[0]

    print (groups)
    return groups

    # group_size = 10
    # group_cnt = 1
    # remainder = len(field_list) % group_size
    # groups = {}
    #
    #
    # while group_cnt < (len(field_list)-remainder)/group_size:
    #     groups[group_cnt] = group_size
    #     group_cnt += 1
    #
    # if remainder == 0:
    #     groups[group_cnt] = group_size
    # else:
    #     groups[group_cnt] = group_size + remainder
    #
    #
    # for k,v in groups.items():
    #     Group.objects.get_or_create(number=k,playerCnt=v)[0]
    #
    #
    # return groups



def create_groups():

    '''takes no input, combines the weekly field with the world ranks and creates 10 groups'''

    #import operator
    import re

    try:
        f = open("config.txt", "r")
        for line in f:
            if "Tournament Name" in line:
                tName = line[18:]
                print (tName)
            elif "Start Date" in line:
                tDate = line[13:]

    except  Exception:
        print (e)

    field = get_field()
    OWGR_rankings =  get_worldrank()
    PGA_rankings = get_pga_worldrank()
    configure_groups(field)

    print (len(field))

    tourny = Tournament.objects.get_or_create(name=tName, start_date=tDate)[0]
    group_dict = {}

    print (tourny)
    for player in field:

        rank = OWGR_rankings.get(player)

        if rank == None:
            rank = PGA_rankings.get(player)

            if rank == None:
                print (player)
                rank = 9999

        group_dict[player] = [rank, field.get(player)]

    player_cnt = 1
    group_num = 1

    groups = Group.objects.get(number=group_num)

    print (group_dict)
    for k, v in sorted(group_dict.items(), key=lambda x: x[1]):
        if player_cnt < groups.playerCnt:
          print (k,v[0], str(groups.number), str(groups.playerCnt))
          Field.objects.get_or_create(tournament=tourny, playerName=k, currentWGR=v[0], group=groups, alternate=v[1])[0]
          player_cnt +=1
        elif player_cnt == groups.playerCnt:
          print (k,v[0], str(groups.number), str(groups.playerCnt))
          Field.objects.get_or_create(tournament=tourny, playerName=k, currentWGR=v[0], group=groups, alternate=v[1])[0]
          group_num +=1
          player_cnt = 1
          if Field.objects.count() < len(field):
             groups = Group.objects.get(number=group_num)


if __name__ == '__main__':
    print ('populating script!')
    #clean_db()
    create_groups()
    print ("Populating Complete!")
