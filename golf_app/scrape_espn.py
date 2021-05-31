from datetime import datetime, timedelta
import pytz
import urllib
import json
from bs4 import BeautifulSoup
from golf_app import utils
from golf_app.models import Tournament, Field, Golfer, ScoreDict
from collections import OrderedDict


class ScrapeESPN(object):

    def __init__(self, tournament=None, url=None, setup=False, ignore_name_mismatch=False):
        if not tournament:
            self.tournament = Tournament.objects.get(current=True)
        else:
            self.tournament=tournament
        
        if not url:
            self.url = "https://www.espn.com/golf/leaderboard"
        else:
            self.url = url

        self.ignore_name_mismatch = ignore_name_mismatch

        self.setup = setup

    def get_data(self):
        start = datetime.now()
        print ('scraping golf espn com')
        
        sd, created = ScoreDict.objects.get_or_create(tournament=self.tournament)
        if self.setup:
            print ('set up mode, scraping')
        elif self.tournament.complete:
            print ('T Complete returning saved score dict ', 'sd saved time: ', sd.updated, 'current time: ', datetime.utcnow().replace(tzinfo=pytz.utc))
            sd.data.get('info').update({'dict_status': 'from_db'})
            return OrderedDict(sd.data)
        elif not created and (sd.updated + timedelta(minutes = 1)) > datetime.utcnow().replace(tzinfo=pytz.utc):
            print ('returning saved score dict ', 'sd saved time: ', sd.updated, 'current time: ', datetime.utcnow().replace(tzinfo=pytz.utc))
            sd.data.get('info').update({'dict_status': 'from_db'})
            return OrderedDict(sd.data)
        
 
        try:
            score_dict = {}

            html = urllib.request.urlopen(self.url)
            soup = BeautifulSoup(html, 'html.parser')
            
            leaderboard = soup.find_all('tbody', {'class': 'Table__TBODY'})

            status = soup.find('div', {'class', 'status'}).span.text
            t_name = soup.find('h1', {'class', 'Leaderboard__Event__Title'}).text
            start = datetime.now()
            
            if t_name != self.tournament.name and not self.tournament.ignore_name_mismatch and not self.ignore_name_mismatch:
                match = utils.check_t_names(t_name, self.tournament)
                if not match:
                    return {}


            print ('espn T Name: ', t_name)
            print ('status: ', status, status[0:5])

            try:
                score_dict['info'] = {'round': int(status.split(' ')[1]),
                                    'complete': False,
                                    'round_status': status}
            except Exception as e:
                if status == "Final":
                    score_dict['info'] = {'round': 4,
                                        'complete': True,
                                        'round_status': status}
                    
                elif status == "Playoff - Play Complete":
                    score_dict['info'] = {'round': 4,
                                        'complete': False,
                                        'round_status': status}
                elif status == "Tournament Field":
                    score_dict['info'] = {'round': 1,
                                        'complete': False,
                                        'round_status': "Not Started"}
                elif status[0:5] == "First":
                     score_dict['info'] = {'round': 1,
                                        'complete': False,
                                        'round_status': status}
                elif status[0:5] == "Secon":
                     score_dict['info'] = {'round': 2,
                                        'complete': False,
                                        'round_status': status}
                elif status[0:5] == "Third":
                     score_dict['info'] = {'round': 3,
                                        'complete': False,
                                        'round_status': status}
                elif status[0:5] == "Final Round":
                     score_dict['info'] = {'round': 4,
                                        'complete': False,
                                        'round_status': status}
    

                else:
                    score_dict['info'] = {'round': 0,
                                        'complete': False,
                                        'round_status': status}
            
            score_dict['info'].update({'source': 'espn'})
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
            

            #print (score_dict['Sungjae Im'])
            #print (score_dict['Patrick Reed'])
            #print ([v for v in score_dict.values() if v.get('rank') == '-'])
            print ('info before cut num calc: ', score_dict.get('info'), 'scrape duration: ', datetime.now() - start)
            cut_calc_start = datetime.now()
            try:
                if score_dict.get('info').get('round_status') == 'Not Started' and score_dict.get('info').get('round') == 1 and self.tournament.has_cut:
                    cut_num = self.tournament.saved_cut_num
                elif self.tournament.has_cut:
                    post_cut_wd = len([v for k,v in score_dict.items() if k!= 'info' and v.get('total_score') in self.tournament.not_playing_list() and \
                        v.get('r3') != '--'])
                    #if score_dict.get('info').get('cut_line') == None:
                        #print ('no cut line exists')
                        #print (len([v for (k,v) in score_dict.items() if k != 'info' and v.get('total_score') == "CUT"]))
                    if len([v for (k,v) in score_dict.items() if k != 'info' and v.get('total_score') == "CUT"]) != 0:
                        print ('cuts exists, inside if')
                        
                        cut_num = len([v for (k,v) in score_dict.items() if k != 'info' and v.get('total_score') not in self.tournament.not_playing_list()]) \
                            + post_cut_wd +1
                    
                    else:
                        print ('no cuts in leaderboadr, in else')
                        cut_num = min(utils.formatRank(x.get('rank')) for k, x in score_dict.items() if k != 'info' and int(utils.formatRank(x.get('rank'))) > self.tournament.saved_cut_num) 
                        print (cut_num)
                        if score_dict.get('cut_line') == None:
                            print ('in cut line none')
                            cut_line = max(int(utils.score_as_int(v.get('total_score'))) for k, v in score_dict.items() if k != 'info' and int(utils.formatRank(v.get('rank'))) < cut_num and \
                                v.get('total_score') not in self.tournament.not_playing_list())
                            print ('2 ', cut_line)
                            score_dict['info'].update({'cut_line': 'Projected Cut Line: ' + str(utils.format_score(cut_line))})
            
                else:
                    cut_num = len([v for k, v in score_dict.items() if k != 'info' and v.get('total_score') not in self.tournament.not_playing_list()]) +1

                score_dict['info'].update({'cut_num': cut_num})
            
            except Exception as e:
                print ('cut nun calc issue: ', e)
                cut_num = self.tournament.saved_cut_num
                score_dict['info'].update({'cut_num': cut_num})

            
            
            if score_dict.get('info').get('cut_line') == None:
                score_dict['info'].update({'cut_line': 'no cut line'}) 

            print ('cut num duration: ', datetime.now() - cut_calc_start)
            print ('info: ', score_dict['info'])
            
            # if {k:v for k,v in sd.data.items() if k != 'info'} == \
            #    {k:v for k,v in score_dict.items() if k != 'info'}  and \
            #    {k:v for k,v in sd.data.get('info').items() if k != 'dict_status'} == \
            #    {k:v for k,v in score_dict.get('info').items() if k != 'dict_status'}:
            #     score_dict.get('info').update({'dict_status': 'no change'})
            # else:
            #     score_dict.get('info').update({'dict_status': 'updated'})

            sd.data = OrderedDict(score_dict)
            sd.save()
            print ('espn scrape duration: ', datetime.now() - start)
            return OrderedDict(score_dict)


        except Exception as e:
            print ('issue scraping espn', e)
            return {}   

    def get_espn_players(self):
        '''note that some espn numbers are out of date on this link'''
        print ('scraping golf espn players')

        try:
            player_dict = {}

            html = urllib.request.urlopen("http://www.espn.com/golf/players")
            soup = BeautifulSoup(html, 'html.parser')
            
            player_table = soup.find('div', {'id': 'my-players-table'})
            players = player_table.find_all('tr')
            
            for row in players:
                exclude_class = ['stathead', 'colhead']
                #print ('my set: ', set(row['class']).intersection(exclude_class))
                if row.has_attr('class') and not bool(set(row['class']).intersection(exclude_class)):
                    td = row.find_all('td')
                    try:
                        name = (' '.join(reversed(td[0].text.split(', '))))
                        #player_dict[name]= {'espn_num': td[0].a['href'].split('/')[7]}
                        player_dict[name] = {'espn_num': get_espn_num(td[0].a['href']),
                                            'detail_link': td[0].a['href']}
                    except Exception as e:
                        print ('scrape espn players execption: ', e, row)

            return player_dict


        except Exception as e:
            print ('issue scraping espn', e)
            return {}   
        
    def get_t_num(self, season=None):
        '''takes either a season object or none.  returns a string '''
        if season:
            html = urllib.request.urlopen('https://www.espn.com/golf/schedule/_/season/' + season.season)
            soup = BeautifulSoup(html, 'html.parser')
            rows = soup.find_all('tr', {'class': 'Table__TR'})
            for row in rows:
                try:
                    if row.find('div', {'class': 'eventAndLocation__innerCell'}):
                        n = row.find('p').text
                        match = utils.check_t_names(n, self.tournament)
                        if match:
                            if row.find('a'):
                                print ('t match hyper link: ', row.find('a')['href'])
                                return (row.find('a')['href'].split('=')[1])
                            else:
                                print ('no link available')
                except Exception as e:
                    print ('ESPN get_t_num error: ', e)
                    print (row)
                    return ('error' + str(e))

        else:
            html = urllib.request.urlopen(self.url)
            soup = BeautifulSoup(html, 'html.parser')
            t = soup.find('select', {'class': 'dropdown__select'})
            print (t.find('option').get('data-url').split('/')[5])
            return t.find('option').get('data-url').split('/')[5]

        return ('no link available')



    # def get_mp_data(self):
    #     print ('scraping golf espn com match play')
        
    #     sd, created = ScoreDict.objects.get_or_create(tournament=self.tournament)
    #     if self.setup:
    #         print ('set up mode, scraping')
    #     elif not created and (sd.updated + timedelta(minutes = 1)) > datetime.utcnow().replace(tzinfo=pytz.utc):
    #         print ('returning saved score dict ', 'sd saved time: ', sd.updated, 'current time: ', datetime.utcnow().replace(tzinfo=pytz.utc))
    #         return sd.data
 
    #     try:
    #         score_dict = {}

    #         html = urllib.request.urlopen(self.url)
    #         soup = BeautifulSoup(html, 'html.parser')
            
    #         leaderboard = soup.find_all('div', {'class': 'MatchPlay__Match'})
    #         start = datetime.now()
    #         status = soup.find('li', {'class': 'tabs__list__item tabs__list__item--active'}).text
    #         day = status.find('data-track-name')
    #         print ('day', soup.find('li', {'class': 'tabs__list__item tabs__list__item--active'}))
    #         score_dict['info'] = {'source': 'espn', 
    #                             'status': status}
            
    #         for row in leaderboard:
    #             for p in row.find_all('div', {'class': 'ScoreCell__TeamName ScoreCell__TeamName--displayName truncate db'}):
    #                 score_dict[p.text.lstrip('(a) ')] = {'rank': 0, 'change': '', 'handicap': 0, 'sod_position': ''}
    #                 #score_dict[row.a.text] = {
    #                 #                    'pga_num': row.a['href'].split('/')[7],
    #                 #                    'rank': td[0].text,
    #                 #                    'change': '',
    #                 #                    'round_score': td[3].text,
    #                 #                    'total_score': td[2].text,
    #                 #                    'thru': td[4].text,
    #                 #                    'r1': td[5].text,
    #                 #                    'r2': td[6].text,
    #                 #                    'r3': td[7].text,
    #                 #                    'r4': td[8].text,  
    #                 #                    'tot_strokes': td[9].text,
    #                 #}
    #             #if len(td) > 1 and Field.objects.filter(golfer__espn_number=score_dict[row.a.text]['pga_num'], tournament=self.tournament).exists():
    #             #    f = Field.objects.get(golfer__espn_number=score_dict[row.a.text]['pga_num'], tournament=self.tournament)
    #             #    score_dict[row.a.text].update({'handicap': f.handicap(),
    #                                      #          'group': f.group.number})                           
            
    #         return score_dict

    #     except Exception as e:
    #         print ('issue scraping espn MP', e)
    #         return {}   

    def get_field(self):
        
        field_dict = {}
        html = urllib.request.urlopen(self.url)
        soup = BeautifulSoup(html, 'html.parser')
            
        leaderboard = soup.find('div', {'class': 'competitors'})
        table = leaderboard.find('tbody', {'class': 'Table__TBODY'})
        player_dict = self.get_espn_players()

        #print (leaderboard)
        for row in table.find_all('tr', {'class', 'Table__TR'}):
            #print (row)
            try:
                espn_num = get_espn_num(row.a['href'])
                detail = [v.get('detail_link') for k,v in player_dict.items() if v.get('espn_num') ==  espn_num]
                if len(detail) == 1:
                    d = detail[0]
                else:
                    d = ''
                field_dict[row.a.text] = {'espn_num': espn_num,
                                          'detail_link': d}

            except Exception as e:
                print ('get espn field row logic exception: ', e, row)
        
        return field_dict


    def status_check(self):
        start = datetime.now()
        html = urllib.request.urlopen(self.url)
        soup = BeautifulSoup(html, 'html.parser')
        
        status = soup.find('div', {'class', 'status'}).span.text
        print ('start status check dur: ', datetime.now() - start, status)
        
        return status

        


def get_espn_num(row):
    '''takes a sting formatted as an a tag href and returns a string'''
    #return row.a['href'].split('/')[7]
    return row.split('/')[7]

