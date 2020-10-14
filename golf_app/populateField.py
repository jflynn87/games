#import os
#os.environ.setdefault("DJANGO_SETTINGS_MODULE","golfProj.settings")

from golf_app.models import (Picks, Field, Group, Tournament, TotalScore,
    ScoreDetails, Name, Season, User, BonusDetails, Golfer)
import urllib3
from django.core.exceptions import ObjectDoesNotExist
from golf_app import calc_score
from django.db import transaction
import urllib
from bs4 import BeautifulSoup
import json
import datetime
#import string
import unidecode 

def clean_db():
    print ('in clean db')
    from golf_app.management.commands.clear_models import Command

    Command()


def get_pga_worldrank():
    '''Goes to PGA web site takes no input, goes to web to get world golf rankings and returns a dictionary with player name as a string and key, ranking as a string in values'''

    #from bs4 import BeautifulSoup
    #import urllib.request
    print ('start pga.com worldrank lookup')
    html = urllib.request.urlopen("https://www.pgatour.com/stats/stat.186.html")
    #html = request.get("https://www.pgatour.com/stats/stat.186.html")
    soup = BeautifulSoup(html, 'html.parser')


    #rankslist = (soup.find("div", {'class': 'details section'}))
    rankslist = (soup.find("table", {'id': 'statsTable'}))

    ranks = {}
    for row in rankslist.find_all('tr')[1:]:
        #print (row)
        try:
            player = (row.find('td', {'class': 'player-name'}).text).strip('\n')
            rank = row.find('td').text.strip('\n').strip(' ')
            last_week=  row.find('td', {'class': 'hidden-print hidden-small hidden-medium'}).text.strip('\n')
            #ranks[player.capitalize()] = [int(rank), int(last_week), 0]
            try:
                rank = int(rank)
            except Exception as e:
                rank = 9999
            try:
                last_week = int(last_week)
            except Exception as e:
                last_week = 0

            ranks[player] = [int(rank), int(last_week), 0]
        except Exception as e:
            print('exception 2', e)

    print ('end pga.com worldrank lookup')
    #print ('pga ranks', ranks)
    print ('pga ranks', ranks.get('Adam scott'))
    return ranks



def get_worldrank():
    '''Goes to OWGR web site takes no input, goes to web to get world golf rankings and returns a dictionary with player name as a string and key, ranking as a string in values'''

    #from bs4 import BeautifulSoup
    #import urllib.request

    print ('start owgr.com lookp')

    html = urllib.request.urlopen("http://www.owgr.com/ranking?pageNo=1&pageSize=All&country=All")
    soup = BeautifulSoup(html, 'html.parser')

    rankslist = (soup.find("div", {'class': 'table_container'}))
    ranks = {}

    for row in rankslist.find_all('tr')[1:]:
        try:
            rank_data = row.find_all('td')
            
            rank_list = []
            i = 0
            for data in rank_data:
                if data.text != '':
                    rank_list.append(int(data.text))
                else:
                    rank_list.append(9999)
                i += 1
                if i == 3:
                    break
            #player = (row.find('td', {'class': 'name'}).text).replace('(Am)','').replace(' Jr','').replace('(am)','')
            player = (row.find('td', {'class': 'name'})).text.split('(')[0]
            
            #ranks[player.title()] = rank_list
            ranks[player] = rank_list
        except Exception as e:
            print('exeption 1',row,e)

    print ('end owgr.com lookup')
    
    #print (ranks.get('Mark anderson'))
    return ranks


def get_field(tournament_number):
    '''takes a tournament number, goes to web to get field and returns a list with player names'''

    season = Season.objects.get(current=True)
    print ('getting field')
    json_url = 'https://statdata.pgatour.com/r/' + str(tournament_number) +'/field.json'
    print (json_url)
    with urllib.request.urlopen(json_url) as field_json_url:
        data = json.loads(field_json_url.read().decode())

    tourny = Tournament()
    tourny.name = data["Tournament"]["TournamentName"]
    tourny.season = season
    start_date = datetime.date.today()
    print (start_date)
    while start_date.weekday() != 3:
        start_date += datetime.timedelta(1)
    tourny.start_date = start_date
    #tourny.start_date = data["Tournament"]["yyyy"] + '-' +data["Tournament"]["mm"] + '-' + data["Tournament"]["dd"]
    tourny.field_json_url = json_url
    tourny.score_json_url = 'https://statdata.pgatour.com/r/' + str(tournament_number) +'/' + str(season) + '/leaderboard-v2mini.json'
    tourny.pga_tournament_num = tournament_number
    tourny.current=True
    tourny.complete=False
    tourny.score_update_time = datetime.datetime.now()
    tourny.cut_score = "no cut info"
    tourny.save()

    #Tournament.objects.get_or_create(season=season, name=tourny.name,start_date=tourny.start_date, field_json_url=tourny.field_json_url, score_json_url=tourny.score_json_url, current=True, complete=False)


    field_list = {}


    for player in data["Tournament"]["Players"][0:]:
        if 'Jr' in player["PlayerName"]:
            name = player["PlayerName"].split(' ')[2] + ' ' + player["PlayerName"].split(' ')[0] + ' ' +player["PlayerName"].split(' ')[1][:-1]
        else:    
            #name = (' '.join(reversed(player["PlayerName"].split(', ')))).replace('Jr.','')
            #name = (' '.join(reversed(player["PlayerName"].split(', '))).replace(' Jr.','').replace('(am)',''))
            name = (' '.join(reversed(player["PlayerName"].split(', '))).replace('(am)', '').replace('(a)', ''))
        playerID = player['TournamentPlayerId']
        try:
            if player["isAlternate"] == "Yes":
                #exclude alternates from the field
                alternate = True
            else:
                alternate = False
                field_list[name] = alternate, playerID
        except IndexError:
            alternate = False
            print (player + 'alternate lookup failed')



    print (field_list)
    return field_list


def configure_groups(field_list):
    '''takes a list, calculates the number of groups and players per group'''
    print ('config groups')
    group_cnt = 1
    groups = {}
    if len(field_list) > 64:
        group_size = 10

        while group_cnt <6:
            groups[group_cnt] = group_size
            group_cnt += 1

        #added to dict at end of funciton
        group_size = len(field_list) - 50
        remainder = 0

#        group_size = 15
#        remainder = (len(field_list)-50) % group_size

#        remaining_groups = (len(field_list)-(remainder+50))/group_size

#        while group_cnt < remaining_groups + 5:
#             groups[group_cnt] = group_size
#             group_cnt += 1
    elif len(field_list) > 29 and len(field_list) < 65 :
        print ('bet 30 - 64, 10 groups')
        total_groups = 10
        group_size = int(len(field_list) / total_groups)
        #total_groups = int(len(field_list)/group_size)
        remainder = len(field_list) % (total_groups*group_size)
        while group_cnt < total_groups:
            groups[group_cnt] = group_size
            group_cnt +=1
    else:
        #should only be here for fields less than 30 golfers
        print ('field less than 30')
        #group_size = int(len(field_list)/10)
        group_size = 3
        remainder = len(field_list) % (group_size)     
        total_groups = (len(field_list)-(remainder))/group_size

        while group_cnt < total_groups:
            groups[group_cnt] = group_size
            group_cnt +=1

    #for last group, same logig regardless of field size
    if remainder == 0:
        groups[group_cnt] = group_size
    else:
        groups[group_cnt] = group_size + remainder



    for k,v in groups.items():
        Group.objects.get_or_create(tournament=Tournament.objects.get(current=True, season__current=True), number=k,playerCnt=v)[0]

    print (groups)
    return groups

@transaction.atomic
def create_groups(tournament_number):

    '''takes in a tournament number for pgatour.com to get json files for the field and score.  initializes all tables for the tournament'''
    print ('increate groups')
    season = Season.objects.get(current=True)

    if Tournament.objects.filter(season=season).count() > 0:
        try:
            last_tournament = Tournament.objects.get(current=True, complete=True, season=season)
            last_tournament.current = False
            last_tournament.save()
            key = {}
            key['pk']=last_tournament.pk
            try:
                calc_score.calc_score(key)
            except:
                print ('error calc scores for last tournament', last_tournament)

        except ObjectDoesNotExist:
            print ('no current tournament')
    else:
        print ('setting up first tournament of season')

    print ('going to get_field')
    field = get_field(tournament_number)
    OWGR_rankings =  get_worldrank()
    #OWGR_rankings = {}
    print ('a')
    try:
        PGA_rankings = get_pga_worldrank()
    except Exception as e:
        print ('pga wgr failed: ', e)
    print ('b')
    configure_groups(field)
    print ('c')
    tournament = Tournament.objects.get(current=True, season=season)
    print ('d')

    print (len(field))

    group_dict = {}
    name_switch = False

    for player in field:
        if Name.objects.filter(PGA_name=player).exists():
            name_switch = True
            name = Name.objects.get(PGA_name=player)
            player = name.OWGR_name
            print ('owgr player', player)
            print ('pga player', name)

        # fix this to get 0 index of ranking list
        try:
            #rank = OWGR_rankings[player.capitalize()][0]
            #rank = OWGR_rankings[player.capitalize()]
            rank = OWGR_rankings[player]
        except Exception:
            try:
                rank = fix_name(player, OWGR_rankings)
                print ('not in owgr', player)
                #rank = PGA_rankings[player]
            except Exception:
                print ('no rank found',player)
                rank = [9999, 9999, 9999]

        if name_switch:
            print ('name switch', player, name)
            player = name.PGA_name
            name_switch = False

        group_dict[player] = [rank, field.get(player)]


    player_cnt = 1
    group_num = 1

    groups = Group.objects.get(tournament=tournament, number=group_num)

    print ('group_dict before field save', group_dict)

    #create dict of player links for picture lookup
    #import urllib

    json_url = 'https://www.pgatour.com/players.html'
    html = urllib.request.urlopen("https://www.pgatour.com/players.html")
    soup = BeautifulSoup(html, 'html.parser')


    #players =  (soup.find("div", {'class': 'directory-item'}).find_all('option'))
    players =  soup.find("div", {'class': 'overview'})
    golfer_dict = {}
    #print (players)
    #print (players.find_all('a', {'class': 'directory-item'}))
    for p in players.find_all('span', {'class': 'player-flag'}):
        #print ('players', p)
        link = ''
        p_text = str(p)[47:]
        for char in p_text:
            if char == '"':
                break
            else:
                link = link + char
            golfer_dict[link[:5]]=link

    for k, v in sorted(group_dict.items(), key=lambda x: x[1][0]):
        #print (k, v)
        map_link = get_flag(k, v)
        if player_cnt < groups.playerCnt:
          #print (k,v[0], str(groups.number), str(groups.playerCnt))
          #player_link = 'https://www.pgatour.com/players/player.' + str(v[1][1]) + '.' + k.split(' ')[0].lowercase() + '-' + k.split(' ')[1].lowercase() + '.html')
          Field.objects.get_or_create(tournament=tournament, playerName=k, \
             #currentWGR=v[0][0], sow_WGR=v[0][1], soy_WGR=v[0][2], group=groups, alternate=v[1][0], \
             currentWGR=v[0][0], sow_WGR=v[0][1], soy_WGR=v[0][2], \
             group=groups, alternate=v[1][0], \
             playerID=v[1][1], pic_link= get_pick_link(v[1][1]), \
             map_link= map_link, golfer=Golfer.objects.get(golfer_pga_num=v[1][1]), handi=calc_handi(v[0][0], len(field)))
          player_cnt +=1
        elif player_cnt == groups.playerCnt:
          #print (k,v[0], str(groups.number), str(groups.playerCnt))
          Field.objects.get_or_create(tournament=tournament, playerName=k, \
             #currentWGR=v[0][0], sow_WGR=v[0][1], soy_WGR=v[0][2], group=groups, alternate=v[1][0], \
             currentWGR=v[0][0], sow_WGR=v[0][1], soy_WGR=v[0][2], \
             group=groups, alternate=v[1][0], \
             playerID=v[1][1], pic_link= get_pick_link(v[1][1]), \
             map_link= map_link, golfer=Golfer.objects.get(golfer_pga_num=v[1][1]), handi=calc_handi(v[0][0], len(field)))
          group_num +=1
          player_cnt = 1
          if Field.objects.filter(tournament=tournament).count() < len(field):
             groups = Group.objects.get(tournament=tournament,number=group_num)

    print ('saved field objects')
    # fix the hard coded tournament, change to identify users who are in the golf game
    # users = TotalScore.objects.filter(tournament__pga_tournament_num="014")
    # for user in users:
    #     bd = BonusDetails()
    #     bd.user = user.user
    #     bd.tournament = tournament
    #     bd.cut_bonus = 0
    #     bd.winner_bonus = 0
    #     bd.save()

def get_pick_link(playerID):
    return "https://pga-tour-res.cloudinary.com/image/upload/c_fill,d_headshots_default.png,f_auto,g_face:center,h_85,q_auto,r_max,w_85/headshots_" + playerID + ".png"

def get_flag(golfer, golfer_data):
    #print ('get flag', golfer, golfer_data)
    golfer_obj, created = Golfer_obj = Golfer.objects.get_or_create(
    golfer_pga_num = golfer_data[1][1])
    if created:
        golfer_obj.golfer_name = golfer
        golfer_obj.save()
    #golfer_obj.save()
    ## add some code to deal with name changes

    try:
        print ('created', created, 'map_link ', golfer_obj.flag_link)
        if golfer_obj.flag_link not in [None, ' ']:  #Golfer.objects.filter(golfer_pga_num=golfer_data[1][1]).exists():
            #golfer = Golfer.objects.get(golfer_pga_num=golfer_data[1][1])
           # print ('flag from db')
            return golfer_obj.flag_link

        elif golfer[1]=='.' and golfer[3] =='.':
            name = str(golfer_data[1][1]) + '.' + golfer[0].lower() + '-' + golfer[2].lower() + '--' + golfer.split(' ')[1].strip(', Jr.').lower()
        else:
            name = str(golfer_data[1][1]) + '.' + golfer.split(' ')[0].lower() + '-' + golfer.split(' ')[1].strip(', Jr.').lower()
        link = 'https://www.pgatour.com/players/player.' + unidecode.unidecode(name) + '.html'
            
        
        player_html = urllib.request.urlopen(link)
        player_soup = BeautifulSoup(player_html, 'html.parser')
        country = (player_soup.find('div', {'class': 'country'}))

        flag = country.find('img').get('src')
        #golfer_obj = Golfer()
        #golfer_obj.golfer_pga_num = golfer_data[1][1]
        #golfer_obj.golfer_name = golfer
        golfer_obj.flag_link = "https://www.pgatour.com" + flag
        golfer_obj.save()
        #print (golfer, flag)
        return  "https://www.pgatour.com" + flag
    except Exception as e:
        #print ("flag lookup issue", golfer, name, e)
        print ("flag lookup issue", golfer, e)
        return None
        #else:
    #    return None


def calc_handi(owgr, field_cnt):
    if round(owgr*.01) < (field_cnt * .13):
        return int(round(owgr*.01))
    return round(field_cnt * .13)



if __name__ == '__main__':
    print ('populating script!')
    #clean_db()
    #create_groups()

    print ("Populating Complete!")


def fix_name(player, owgr_rankings):
    print ('trying to fix name: ', player)
    
    if owgr_rankings.get(player) != None:
        return (owgr_rankings.get(player))

    for k, v in owgr_rankings.items():
        owgr_name = k.split(' ')
        pga_name = player.split(' ')
        #print (owgr_name, pga_name)
        
        if unidecode.unidecode(owgr_name[len(owgr_name)-1]) == unidecode.unidecode(pga_name[len(pga_name)-1]) \
           and k[0:1] == player[0:1]:
            print ('last name, first initial match', player)
            return v
        elif unidecode.unidecode(owgr_name[len(owgr_name)-2]) == unidecode.unidecode(pga_name[len(pga_name)-1]) \
            and k[0:1] == player[0:1]:
            print ('last name, first initial match, cut owgr suffix', player)
            return v

    return None

    
    

