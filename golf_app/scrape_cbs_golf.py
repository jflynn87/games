import datetime
import urllib
import json
from bs4 import BeautifulSoup



class ScrapeCBS(object):

    #def __init__(self):


    def get_data(self):
        print ('scraping golf CBS com')

        try:
            score_dict = {}

            html = urllib.request.urlopen("https://www.cbssports.com/golf/leaderboard/")
            #html = urllib.request.urlopen("https://www.cbssports.com/golf/leaderboard/pga-tour/26496762/sentry-tournament-of-champions/")
            soup = BeautifulSoup(html, 'html.parser')
            
            leaderboard = soup.find('div', {'id': 'TableGolfLeaderboard'})
            
            #print (leaderboard)
            if leaderboard == None:
                return {}

            rows = leaderboard.find_all('tr', {'class': 'TableBase-bodyTr'})

            print ('cbs rows length: ', len(rows))
            for r  in rows:
                #print (r)
                pos_sect = r.find_all('td', {'class': "TableBase-bodyTd"})
                #print (pos_sect)
                pos =  pos_sect[1].text
                player = r.find('span', {'class': "CellPlayerName--long"})
                player_name = player.text
                player_num = player.a['href'].split('/')[6]
               
                to_par = r.find('td', {'class': 'GolfLeaderboardTable-bodyTd--toPar'}).text

                #for line in pos_sect: 
                #    if 'GolfLeaderboard-bodyTd--cutLine' in line['class']:
                #        print ('cut line')
                 #   else:
                nums = r.find_all('td', {'class': 'TableBase-bodyTd--number'})
                #print ('nums', len(nums))
                if len(nums)  == 6:  #when not playing so no "thru"
                            
                    r1 = nums[1].text
                    r2  = nums[2].text
                    r3 = nums[3].text  
                    r4 =nums[4].text
                    total_strokes = nums[5].text
                    thru = ' '
                    today = ' '
                else:
                    thru = nums[1].text
                    today = nums[2].text
                    r1 = nums[3].text
                    r2  = nums[4].text
                    r3 = nums[5].text
                    r4 =nums[6].text
                    total_strokes = nums[7].text
                            
                score_dict[player_name] = {'rank': pos, 'total_score': to_par, 'thru': thru, 'round_score': today, 'r1': r1, 'r2':r2, 'r3': r3, 'r4': r4, 'total_strokes': total_strokes, 'change': ' ', 
                                                    'cbs_player_num': player_num
                        }

            #print ('score dict from CBS', score_dict)
            return score_dict


        except Exception as e:
            print ('issue scraping CBS', e)
            return {}   

    def get_players(self):

        try:
            player_dict = {}

            html = urllib.request.urlopen("https://www.cbssports.com/golf/players")
            soup = BeautifulSoup(html, 'html.parser')
            
            players = soup.find('select', {'id': 'playerStatList'})
            
            rows = players.find_all('option')

            print ('cbs rows length: ', len(rows))
            for r  in rows:
                player_dict[r.text]=r['value']
                #print (r)
                #pos_sect = r.find_all('td', {'class': "TableBase-bodyTd"})
                #print (pos_sect)
                #pos =  pos_sect[1].text
        except Exception as e:
            print ('CBS golfer scrape issue', e)
        
        return player_dict