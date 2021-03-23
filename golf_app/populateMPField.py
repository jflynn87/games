from golf_app.models import (Picks, Field, Group, Tournament, TotalScore,
    ScoreDetails, Name, Season, User, BonusDetails, Golfer, ScoreDict)
from golf_app import scrape_scores_picks
import urllib3
from django.core.exceptions import ObjectDoesNotExist
from golf_app import scrape_espn, utils, populateField
from django.db import transaction
import urllib
from bs4 import BeautifulSoup
import json
import datetime
import unidecode 
import collections



def configure_groups(field_list):
    '''creates 12 groups of 4,  assumes 64 player tournament'''
    print ('config groups')

    print ('len field list in configure_groups: ', len(field_list))

    group = 1
    while group < 17:
        Group.objects.get_or_create(tournament=Tournament.objects.get(current=True, season__current=True), number=group,playerCnt=4)
        group += 1

    print (group)
    return group

@transaction.atomic
def create_groups(tournament_number):

    '''takes in a tournament number for pgatour.com to get json files for the field and score.  initializes all tables for the tournament'''
    print ('executing PopulateMPField')
    season = Season.objects.get(current=True)

    if Tournament.objects.filter(season=season).count() > 0:
        try:
            last_tournament = Tournament.objects.get(current=True, complete=True, season=season)
            last_tournament.current = False
            last_tournament.save()
            key = {}
            key['pk']=last_tournament.pk
            #try:
            #    calc_score.calc_score(key)
            #except:
            #    print ('error calc scores for last tournament', last_tournament)

        except ObjectDoesNotExist:
            print ('no current tournament')
    else:
        print ('setting up first tournament of season')

    print ('going to get_field')
    field = populateField.get_field(tournament_number)
    OWGR_rankings =  populateField.get_worldrank()
    #OWGR_rankings = {}
   
    print ('a')
    configure_groups(field)
    print ('c')
    tournament = Tournament.objects.get(current=True, season=season)
    print ('d')

    bracket = scrape_scores_picks.ScrapeScores(tournament, 'https://www.pgatour.com/competition/2021/wgc-dell-technologies-match-play/group-stage.html').mp_brackets()
    #prior_year_sd(tournament)

    #print (len(field))

    group_dict = {}
    name_switch = False
    name_issues = []
    for player in field:
        #print (player)
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
                lookup = utils.fix_name(player, OWGR_rankings)
                print ('not in owgr', player, lookup)
                name_issues.append((player, lookup))
                rank = lookup[1]
                #rank = PGA_rankings[player]
            except Exception as e:
                print ('no rank found', player, e)
                rank = [9999, 9999, 9999]

        if name_switch:
            print ('name switch', player, name)
            player = name.PGA_name
            name_switch = False

        group_dict[player] = [rank, field.get(player)]
 

    player_cnt = 1
    group_num = 1

    groups = Group.objects.get(tournament=tournament, number=group_num)
    print ('name issues: ', name_issues)
    #print ('group_dict before field save', group_dict)

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
    espn_players = get_espn_players()
    print ('xxxxxxx', espn_players)
    #for k, v in sorted(group_dict.items(), key=lambda x: x[1][0]):
        #print ('key/val: ', k, v)
        #map_link = get_flag(k, v, espn_players)
        #print (k, map_link)
        #print (k)
    for golfer, group in bracket.items():
            #print (golfer.split(' ')[1], len(golfer.split(' ')[1]),  k.split(' ')[1].rstrip(), len(k.split(' ')[1].rstrip()))
        #print (golfer, group, group_dict.get(golfer))
        #map_link = get_flag(golfer, group_dict.get(golfer), espn_players)
            #if golfer.split(' ')[1] == k.split(' ')[1].rstrip():
            #    print ('MAtch', golfer.split(' ')[1], len(golfer.split(' ')[1]),  k.split(' ')[1].rstrip(), len(k.split(' ')[1].rstrip()))
        g = group.split(' ')[1]
         #       break

        #print ('group: ', k, group)
        print ('1 ', golfer)
        golfer_n = golfer.split('(')[0].rstrip()

        ranks = utils.fix_name(golfer_n, OWGR_rankings)
        print ('2', golfer, golfer_n, ranks)
        
        golfer_obj, created = Golfer.objects.get_or_create(golfer_name=golfer_n)
        flag = get_flag(golfer_n, golfer_n, espn_players)
        pic = get_pick_link(golfer_obj.golfer_pga_num)
        g_obj = Group.objects.get(tournament=tournament, number=g)
        Field.objects.get_or_create(tournament=tournament, playerName=golfer_n, \
             currentWGR=ranks[1][0], sow_WGR=ranks[1][1], soy_WGR=ranks[1][2], \
             group=g_obj, alternate=None, \
             playerID=None, pic_link= pic, \
             map_link= flag, golfer=golfer_obj, handi=0)


    #print ('checking issue field count', Field.objects.filter(tournament=tournament).count(), 'field len: ', len(field), group_num )
    #if Field.objects.filter(tournament=tournament).count() < len(field):
    #groups = Group.objects.get(tournament=tournament,number=group_num)


 

    print ('saved field objects')

def get_pick_link(playerID):
    return "https://pga-tour-res.cloudinary.com/image/upload/c_fill,d_headshots_default.png,f_auto,g_face:center,h_85,q_auto,r_max,w_85/headshots_" + playerID + ".png"

def get_flag(golfer, golfer_data, espn_data):
    #print ('get flag', golfer, golfer_data)
    golfer_obj, created = Golfer_obj = Golfer.objects.get_or_create(
    golfer_name = golfer_data)
    if created:
        golfer_obj.golfer_name = golfer
        golfer_obj.save()

    if golfer_obj.espn_number in [' ', None]:
        espn_number = get_espn_num(golfer, espn_data)
        #print ('get flag espn num', golfer)
        #try:
        if espn_number[1].get('pga_num'):
            print ('inside if on espn num', espn_number[1])
            golfer_obj.espn_number = espn_number[1].get('pga_num')
            print ('golfer_obj espn number', golfer_obj.espn_number)
            golfer_obj.save()
            
    #golfer_obj.save()
    ## add some code to deal with name changes

    try:
        #print ('created', created, 'map_link ', golfer_obj.flag_link)
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

    
def get_espn_num(player, espn_data):
    if espn_data.get(player):
        print ('returning found: ', player, espn_data.get(player))
        return player, espn_data.get(player)
        #print ('found player: ', player)
    else:
        print ('not found, fixing: ', player)
        fixed_data = utils.fix_name(player, espn_data)
        print ('returning fixed: ',  fixed_data)
        if fixed_data[0] == None:
            return (player, {})
        else:
            return player, fixed_data[1]
        
    return

def get_espn_players():
    espn_data = scrape_espn.ScrapeESPN(None, None, True, True).get_data()
    return espn_data

def prior_year_sd(t):
    '''takes a tournament and returns nothing'''
    try:
        prior_season = Season.objects.get(season=int(t.season.season)-1)
        prior_t = Tournament.objects.get(pga_tournament_num=t.pga_tournament_num, season=prior_season)
    except Exception as e:
        print ('no prior tournament, getting 2 years ago', e)
        try:
            prior_season = Season.objects.get(season=int(t.season.season)-2)
            prior_t = Tournament.objects.get(pga_tournament_num=t.pga_tournament_num, season=prior_season)
        except Exception as f:
            print ('no prior 2 years ago, returning nothing', f)
            return {}

    print ('proir T: ', prior_t, prior_t.season)
    sd, created = ScoreDict.objects.get_or_create(tournament=prior_t)
    pga_nums = [v.get('pga_num') for (k,v) in sd.data.items() if k != 'info' and v.get('pga_num')] 
    print ('prior SD # of pga nums: ', len(pga_nums))

    if (not created and (not sd.data or len(sd.data) == 0 or len(pga_nums) == 0)) or created:
        print ('updating prior SD', prior_t)
        espn_t_num = scrape_espn.ScrapeESPN().get_t_num(prior_season)
        url = "https://www.espn.com/golf/leaderboard?tournamentId=" + espn_t_num
        score_dict = scrape_espn.ScrapeESPN(prior_t,url, True, True).get_data()
        sd.data = score_dict
        sd.save()
    return sd.data
                

