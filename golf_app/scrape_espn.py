import datetime
import urllib
import json
from bs4 import BeautifulSoup



class ScrapeESPN(object):

    #def __init__(self):


    def get_data(self):
        print ('scraping golf espn com')

        try:
            score_dict = {}

            html = urllib.request.urlopen("https://www.espn.com/golf/leaderboard")
            #html = urllib.request.urlopen("https://www.cbssports.com/golf/leaderboard/pga-tour/26496766/sony-open-in-hawaii/")
            soup = BeautifulSoup(html, 'html.parser')
            
            leaderboard = soup.find('tbody', {'class': 'Table__TBODY'})
            status = soup.find('div', {'class', 'status'}).span.text
            #print ('status: ', status)
            score_dict['info'] = {'round': status}
            table = leaderboard.find_all('tr')
            
            for row in table:
                td = row.find_all('td')
                score_dict[row.a.text] = {
                                    'espn_num': row.a['href'].split('/')[7],
                                    'pos': td[0].text,
                                    'score': td[2].text,
                                    'r1': td[3].text,
                                    'r2': td[4].text,
                                    'r3': td[5].text,
                                    'r4': td[6].text,
                                    'tot': td[7].text,
                }
                

                            
#                score_dict[player_name] = {'rank': pos, 'total_score': to_par, 'thru': thru, 'round_score': today, 'r1': r1, 'r2':r2, 'r3': r3, 'r4': r4, 'total_strokes': total_strokes, 'change': ' ', 
#                                                    'cbs_player_num': player_num
            return score_dict


        except Exception as e:
            print ('issue scraping espn', e)
            return {}   

    def get_espn_players(self):
        print ('scraping golf espn players')

        try:
            player_dict = {}

            html = urllib.request.urlopen("http://www.espn.com/golf/players")
            #html = urllib.request.urlopen("https://www.cbssports.com/golf/leaderboard/pga-tour/26496766/sony-open-in-hawaii/")
            soup = BeautifulSoup(html, 'html.parser')
            
            player_table = soup.find('div', {'id': 'my-players-table'})
            players = player_table.find_all('tr')
            
            for row in players:
                td = row.find_all('td')
                try:
                    name = (' '.join(reversed(td[0].text.split(', '))))
                    player_dict[name]= {'espn_num': td[0].a['href'].split('/')[7]}
                except Exception as e:
                    pass
                #print (row.a)
                #score_dict[row.a.text] = {
                #                    'espn_num': row.a['href'].split('/')[7],
                #                    'pos': td[0].text,
                #                    'score': td[2].text,
                #                    'r1': td[3].text,
                #                    'r2': td[4].text,
                #                    'r3': td[5].text,
                #                    'r4': td[6].text,
                #                    'tot': td[7].text,
                #}
                

                            
#                score_dict[player_name] = {'rank': pos, 'total_score': to_par, 'thru': thru, 'round_score': today, 'r1': r1, 'r2':r2, 'r3': r3, 'r4': r4, 'total_strokes': total_strokes, 'change': ' ', 
#                                                    'cbs_player_num': player_num
            return player_dict


        except Exception as e:
            print ('issue scraping espn', e)
            return {}   
        