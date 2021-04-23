from datetime import datetime
import urllib
import json
from bs4 import BeautifulSoup
from golf_app.models import Field, Picks
from unidecode import unidecode
from golf_app import score_dict_common


class ScrapeCBS(object):
    '''only works for partner events'''
    #def __init__(self):


    def get_data(self):
        print ('scraping golf CBS com')

        try:
            score_dict = {}

            html = urllib.request.urlopen("https://www.cbssports.com/golf/leaderboard/")
            #html = urllib.request.urlopen("https://www.cbssports.com/golf/leaderboard/pga-tour/26496856/zurich-classic-of-new-orleans/")
            #html = urllib.request.urlopen("https://www.cbssports.com/golf/leaderboard/pga-tour/18271952/zurich-classic-of-new-orleans/")
            
            soup = BeautifulSoup(html, 'html.parser')
            
            leaderboard = soup.find('div', {'id': 'TableGolfLeaderboard'})
            
            if leaderboard == None:
                return {}

            r = soup.find('span', {'id': 'hudRound'})['data-roundnumber']
            status = soup.find('span', {'id': 'hudRound'})['data-roundstatus']
            try:
                if round != 4:
                    score_dict['info'] = {'round': int(r),
                                        'complete': False,
                                        'round_status': 'Round ' + str(r)  + ': ' + str(status)}
                else:
                    if status == "Final":
                        score_dict['info'] = {'round': 4,
                                            'complete': True,
                                            'round_status': status}
                    else:
                        score_dict['info'] = {'round': int(r),
                        'complete': False,
                        'round_status': 'Round ' + str(r)  + str(status)}
            except Exception as e:
                print ('cbs scrape round/status execeptin', e)
                score_dict['info'] = {}
            
            
            score_dict['info'].update({'source': 'cbs'})
            score_dict['info'].update({'playoff': False})


            rows = leaderboard.find_all('tr', {'class': 'TableBase-bodyTr'})

            print ('cbs rows length: ', len(rows))
            loop_start = datetime.now()
            for r  in rows:
                this_loop_start = datetime.now()
                #print (r)
                if r.text == 'projected cut':
                    continue
                pos_sect = r.find_all('td', {'class': "TableBase-bodyTd"})
                #print (pos_sect)
                pos =  pos_sect[1].text
                player = r.find('span', {'class': "CellPlayerName--long"})
                player_name = player.text
                player_num = player.a['href'].split('/')[6]
               
                to_par = r.find('td', {'class': 'GolfLeaderboardTable-bodyTd--toPar'}).text
                
                nums = r.find_all('td', {'class': 'TableBase-bodyTd--number'})
                #print ('nums', len(nums), nums)
                if len(nums)  == 6:  #when not playing so no "thru"
                            
                    r1 = nums[1].text
                    r2  = nums[2].text
                    r3 = nums[3].text  
                    r4 =nums[4].text
                    total_strokes = nums[5].text
                    thru = ' '
                    today = ' '
                elif len(nums) == 7:  #when complete, no thru or today but with earnings
                    #thru = nums[1].text
                    #today = nums[2].text
                    r1 = nums[2].text
                    r2  = nums[3].text
                    r3 = nums[4].text
                    r4 =nums[5].text
                    total_strokes = nums[6].text
                    thru = 'F'
                    today = ''
                elif len(nums) == 8:
                    thru = nums[1].text
                    today = nums[2].text
                    r1 = nums[3].text
                    r2  = nums[4].text
                    r3 = nums[5].text
                    r4 =nums[6].text
                    total_strokes = nums[7].text
                else:
                    print ('scrape cbs leaderboard issue, nums len not 6, 7, 8.  it is" : ', len(nums), nums)
                
                
                group = 99
                pga_num = 0


                score_dict[player_name] = {'rank': pos, 'total_score': to_par, 'thru': thru, 'round_score': today, 'r1': r1, 'r2':r2, 'r3': r3, 'r4': r4, 'total_strokes': total_strokes, 'change': ' ', 
                                                    'cbs_player_num': player_num, 'pga_num': pga_num, 'handicap': int(0), 'group': group
                        }
            print ('cbs scrape loop duration: ', datetime.now() - loop_start)
            
            for f in Field.objects.filter(tournament__current=True):
                score_dict.get(unidecode(f.playerName)).update({'group': f.group.number,
                                                                'pga_num': f.golfer.espn_number})

            cuts = score_dict_common.ScoreDictCommon(score_dict).cut_data()
            score_dict.update({'info': cuts})
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