from django import template
from golf_app.models import Picks, mpScores, Field, Tournament, Group
from django.db.models import Count
from string import ascii_letters
import re
import urllib
from bs4 import BeautifulSoup


register = template.Library()

@register.filter
def model_name(obj):
    return obj._meta.verbose_name

@register.filter
def currency(dollars):
    dollars = int(dollars)
    return '$' + str(dollars)

@register.filter
def line_break(count):
    user_cnt = Picks.objects.filter(playerName__tournament__current=True).values('playerName__tournament').annotate(Count('user', distinct=True))
    if (count -1) % (user_cnt[0].get('user__count')) == 0 or count == 0:
        return True
    else:
        return False

@register.filter
def first_round(pick):
    field = Field.objects.get(tournament__pga_tournament_num='470', playerName=pick)
    wins = mpScores.objects.filter(player=field, round__lt=4, result="Yes").count()
    losses = mpScores.objects.filter(player=field, round__lt=4, result="No").exclude(score="AS").count()
    ties = mpScores.objects.filter(player=field, round__lt=4, score="AS").count()

    return str(wins) + '-' + str(losses) + '-' + str(ties)

@register.filter
def leader(group):
    #print ('group', group)
    tournament = Tournament.objects.get(pga_tournament_num="470")
    grp = Group.objects.get(tournament=tournament,number=group)
    field = Field.objects.filter(tournament=tournament, group=grp)
    golfer_dict = {}

    for golfer in field:
        golfer_dict[golfer.playerName] = int(first_round(golfer.playerName)[0]) + (.5*int(first_round(golfer.playerName)[4]))

    #print ('leader', [k for k, v in golfer_dict.items() if v == max(golfer_dict.values())])
    winner= [k for k, v in golfer_dict.items() if v == max(golfer_dict.values())]
    return winner

@register.filter
def partner(partner):
    regex = re.compile('[^a-zA-Z" "]')
    name = (regex.sub('', partner))
    return (name)


#
# @register.filter
# def get_pic(playerID):
#     if playerID != None:
#         return "https://pga-tour-res.cloudinary.com/image/upload/c_fill,d_headshots_default.png,f_auto,g_face:center,h_85,q_auto,r_max,w_85/headshots_" + playerID + ".png"
#     else:
#         return None
#
# @register.filter
# def get_flag(playerID):
#
#     if playerID != None:
#         json_url = 'https://www.pgatour.com/players.html'
#         html = urllib.request.urlopen("https://www.pgatour.com/players.html")
#         soup = BeautifulSoup(html, 'html.parser')
#
#
#         players =  (soup.find("div", {'class': 'directory-select'}).find_all('option'))
#         golfer_dict = {}
#
#         for p in players:
#         #    if first< 2:
#                 link = ''
#                 p_text = str(p)[47:]
#                 for char in p_text:
#                     if char == '"':
#                         break
#                     else:
#                         link = link + char
#                 golfer_dict[link[:5]]=link
#         #print(golfer_dict)
#
#         #for golfer in Field.objects.filter(tournament__pga_tournament_num='026'):
#
#         link_text = golfer_dict.get(playerID)
#
#         if link_text != None:
#
#             link = "https://www.pgatour.com/players/player." + link_text
#             player_html = urllib.request.urlopen(link)
#             player_soup = BeautifulSoup(player_html, 'html.parser')
#             country = (player_soup.find('img', {'class': 's-flag'}))
#             flag = country.get('src')
#             print (playerID, flag)
#             return  "https://www.pgatour.com" + flag
#         else:
#             return None
#     else:
#         return None
