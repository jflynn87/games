from datetime import datetime
import urllib
import json
from bs4 import BeautifulSoup
from golf_app import utils
from golf_app.models import Tournament, Field, Golfer


class ScrapeESPN(object):

    def __init__(self):
        self.tournament = Tournament.objects.get(current=True)


    def get_data(self):
        print ('scraping golf espn com')

        try:
            score_dict = {}

            html = urllib.request.urlopen("https://www.espn.com/golf/leaderboard")
            #html = urllib.request.urlopen('https://www.espn.com/golf/leaderboard?tournamentId=401243401')
            soup = BeautifulSoup(html, 'html.parser')
            
            leaderboard = soup.find_all('tbody', {'class': 'Table__TBODY'})
            
            status = soup.find('div', {'class', 'status'}).span.text
            print ('status: ', status)

            try:
                score_dict['info'] = {'round': int(status.split(' ')[1]),
                                    'complete': False,
                                    'round_status': status}
            except Exception as e:
                if status == "Final":
                    score_dict['info'] = {'round': 4,
                                        'complete': True,
                                        'round_status': status}
                    
                else:
                    score_dict['info'] = {'round': status,
                                        'complete': False,
                                        'round_status': status}
            
            playoff_sect = soup.find('div', {'class': 'leaderboard__playoff--table'})
            if playoff_sect == None:
                playoff = False
                score_dict['info'].update({'playoff': False})
            else:
                playoff = True
                score_dict['info'].update({'playoff': True})

            if playoff:
                table = leaderboard[1].find_all('tr')
            else:
                table = leaderboard[0].find_all('tr')
                
            
            for row in table:
                td = row.find_all('td')
                #print (row['class'], len(row.find_all('td')))
                #print (row.a['href'].split('/'))
                #print (len(row.find_all('td')))
                if len(td) == 1 and 'cutline' in row['class']:
                    if "Projected" in td[0].text:
                        score_dict['info'].update({'cut_line': td[0].text}) 
                    else:
                        score_dict['info'].update({'cut_line': 'Cut Line: ' + td[0].text[-2:]})

                elif len(row.find_all('td')) == 2:  # before start
                    score_dict[row.a.text] =  {
                                                'pga_num': row.a['href'].split('/')[7],
                                                'pos': td[1].text,
                    }
                elif len(td) == 11:  #afer round 1  
                    if td[3].text in self.tournament.not_playing_list():
                        rank = td[3].text 
                    else:
                        rank = td[0].text

                    score_dict[row.a.text] = {
                                        'pga_num': row.a['href'].split('/')[7],
                                        'rank': rank,
                                        'change': str(td[1].span),
                                        'round_score': td[4].text,
                                        'total_score': td[3].text,
                                        'thru': td[5].text,
                                        'r1': td[6].text,
                                        'r2': td[7].text,
                                        'r3': td[8].text,
                                        'r4': td[9].text,  
                                        'tot_strokes': td[10].text,
                    }
                elif len(td) == 10 and score_dict.get('info').get('round') != 1:  #tournament complete 
                    if td[2].text in self.tournament.not_playing_list():
                       rank = td[2].text 
                    else:
                       rank = td[0].text

                    score_dict[row.a.text] = {
                                        'pga_num': row.a['href'].split('/')[7],
                                        'rank': rank,
                                        #'change': str(td[1].span),
                                        'change': '',
                                        'round_score': '',
                                        'total_score': td[2].text,
                                        'thru': "F",
                                        'r1': td[3].text,
                                        'r2': td[4].text,
                                        'r3': td[5].text,
                                        'r4': td[6].text,  
                                        'tot_strokes': td[7].text,
                    }
                

                else: #round 1 make this fit that
                    score_dict[row.a.text] = {
                                        'pga_num': row.a['href'].split('/')[7],
                                        'rank': td[0].text,
                                        'change': '',
                                        'round_score': td[3].text,
                                        'total_score': td[2].text,
                                        'thru': td[4].text,
                                        'r1': td[5].text,
                                        'r2': td[6].text,
                                        'r3': td[7].text,
                                        'r4': td[8].text,  
                                        'tot_strokes': td[9].text,
                    }
                if len(td) > 1 and Field.objects.filter(golfer__espn_number=score_dict[row.a.text]['pga_num'], tournament=self.tournament).exists():
                    f = Field.objects.get(golfer__espn_number=score_dict[row.a.text]['pga_num'], tournament=self.tournament)
                    score_dict[row.a.text].update({'handicap': f.handicap(),
                                                   'group': f.group.number})                           
            start = datetime.now()

            #print (score_dict['Sungjae Im'])
            #print (score_dict['Patrick Reed'])
            #print ([v for v in score_dict.values() if v.get('rank') == '-'])
            print ('info before cut num calc: ', score_dict.get('info'))
            
            if score_dict.get('info').get('round') == 'Tournament Field':
                cut_num = 65
            elif self.tournament.has_cut:
                post_cut_wd = len([v for k,v in score_dict.items() if k!= 'info' and v.get('total_score') in self.tournament.not_playing_list() and \
                    v.get('r3') != '--'])
                #if score_dict.get('info').get('cut_line') == None:
                    #print ('no cut line exists')
                    #print (len([v for (k,v) in score_dict.items() if k != 'info' and v.get('total_score') == "CUT"]))
                if len([v for (k,v) in score_dict.items() if k != 'info' and v.get('total_score') == "CUT"]) != 0:
                    print ('cuts exists. inside if')
                    
                    cut_num = len([v for (k,v) in score_dict.items() if k != 'info' and v.get('total_score') not in self.tournament.not_playing_list()]) \
                        + post_cut_wd +1
                
                else:
                    print ('no cuts in leaderboadr, in else')
                    cut_num = min(utils.formatRank(x.get('rank')) for k, x in score_dict.items() if k != 'info' and int(utils.formatRank(x.get('rank'))) > self.tournament.saved_cut_num) 
            #else:
                 #   print ('cut line')
                 #   cut_num = len([v for k, v in score_dict.items() if k != 'info' and v.get('total_score') not in self.tournament.not_playing_list()]) + post_cut_wd +1
           
            else:
                cut_num = len([v for k, v in score_dict.items() if k != 'info' and v.get('total_score') not in self.tournament.not_playing_list()]) +1

            score_dict['info'].update({'cut_num': cut_num})
            print ('cut_num_duration: ', datetime.now() - start)
            print ('info: ', score_dict['info'])


            return score_dict


        except Exception as e:
            print ('issue scraping espn', e)
            return {}   

    def get_espn_players(self):
        print ('scraping golf espn players')

        try:
            player_dict = {}

            html = urllib.request.urlopen("http://www.espn.com/golf/players")
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
        