from golf_app.models import Picks, ScoreDict, Field, Golfer, Tournament
#from django.contrib.auth.models import User
from datetime import datetime, timedelta

#from django.db.models import Min, Q, Count, Sum, Max
from requests import get
# from selenium import webdriver
# import urllib
# from selenium.webdriver import Chrome, ChromeOptions
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.by import By
import json
from golf_app import utils
from bs4 import BeautifulSoup
import time



class ScrapeScores(object):

    def __init__(self, tournament=None, url=None, mode=None):
        print (url)
        if tournament:
            self.tournament = tournament
        else:
            self.tournament = Tournament.objects.get(current=True)

        if url:
            self.url = url
        elif tournament == None or self.tournament.current:
            self.url = "https://www.pgatour.com/leaderboard.html"
            #self.url = "https://www.pgatour.com/competition/2021/mayakoba-golf-classic/leaderboard.html"
        else:
            t_name = self.tournament.name.replace(' ', '-').lower()
            self.url = "https://www.pgatour.com/competition/2020/" + t_name + "/leaderboard.html"
        print (self.url)

        if mode == 'picks':
            self.mode = 'picks'
        else:
            self.mode = 'all'


    def scrape_zurich(self):
        start = datetime.now()
        score_dict = {'info': {'source': 'PGA'}}
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--window-size=1920,1080")

        driver = Chrome(options=options)
        print ('driver pre url: ', datetime.now() - start)
        driver.get(self.url)
        print ('driver after url: ', datetime.now() - start)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        print ('driver after soup: ', datetime.now() - start)
        #table = (soup.find("div", {'id':'team-play-container'}))
        table = (soup.find("div", {'id':'team-play-container'}))
        print ('tble len; ', len(table))
        print ('driver after table: ', datetime.now() - start)
        t = self.tournament
        t_ok = False

        print ('driver initialized: ', datetime.now() - start)
        try:
            
            title = soup.find('h1', {'class', 'name'})
            name = title.text.lstrip().rstrip()
            print ('t name', name)

            if t.name == name.lstrip().rstrip():
               t_ok = True
            elif t.name == name.replace(' - Leaderboard', '').lstrip().rstrip():
                t_ok = True
            else: 
                print ('scrape name issue', 'db: ', t.name, 'scrape: ', name)
        
            if t_ok:
                try:
                    cut_line = driver.find_elements_by_class_name("cut-line")
                    for c in cut_line:
                        cut_score  = c.text.rsplit(' ', 1)[1]
                        #print ('full cutt text: ', c.text, 'cut score: ', c.text.rsplit(' ', 1)[1])
                        if "Projected" in c.text:
                            t.cut_score = "Projected cut score: " + c.text.rsplit(' ', 1)[1]
                            t.save()
                        else:
                            t.cut_score = "Cut Score: " + c.text.rsplit(' ', 1)[1]
                            t.save()
                except Exception as e:
                    print ('issue scraping cut-info class from pga leaderboard', e)
                    

                #find playoff data
                playoff = driver.find_elements_by_class_name("playoff-module")
                print (t.name, '-------playoff--------')
                print ('length', len(playoff))
                for p in playoff:
                    print (p.text)
                print (t.name, '-------end playoff------')

                if len(playoff) > 0:
                    t.playoff = True
                    score_dict['info'].update({'playoff': True})
                else:
                    score_dict['info'].update({'playoff': False})

                #table = driver.find_element_by_id("stroke-play-container")
                
                sd, created = ScoreDict.objects.get_or_create(tournament=self.tournament)                
                
                if self.mode == 'picks':
                    for pick in Picks.objects.filter(playerName__tournament=self.tournament).values('playerName__playerID').distinct():
                        row =  table.find("tr", {'class': 'line-row-' + str(pick.get('playerName__playerID'))})
                        data = get_data(self, row)
                        data[1].update({'pga_num': pick.playerID})
                        score_dict[data[0]] =  data[1]
                    #sd.pick_data = score_dict
                else:  #doing for "all" or None 
                    for row in table.find_all("tr", {'class': 'line-row'}):
                        #print(row)
                        ele_class = row['class'][1].split('-')[2]
                        #print (ele_class)
                        if self.tournament.pga_tournament_num == '018':
                            for p in row.find_all('div', {'class': 'player-name-col'}):
                                #print (p.text)                            
                                player_name = p.text
                                if row.find('td', {'class': 'status'}):
                                    rank = row.find('td', {'class': 'status'}).text
                                    movement = ''
                                else:
                                    rank = row.find('div', {'class': 'position'}).text
                                    movement = str(row.find('div', {'class': 'position-movement'}))
                                to_par = row.find('td', {'class': 'total'}).text
                                thru = row.find('div', {'class': 'thru'}).text
                                today = row.find('div', {'class': 'round'}).text
                                for i, r in enumerate(row.find_all('td', {'class': 'round-x'})):
                                    if i == 0:
                                        r1 = r.text
                                    elif i ==1:
                                        r2 = r.text
                                    elif i == 2:
                                        r3 = r.text
                                    elif i ==3:
                                        r4 = r.text
                                total_strokes = row.find('td', {'class': 'strokes'}).text
                                
                                if Field.objects.filter(tournament=self.tournament, playerName=player_name).exists():
                                    f = Field.objects.get(tournament=self.tournament, playerName=player_name)
                                    pga_num = f.golfer.espn_number
                                elif Field.objects.filter(tournament=self.tournament, partner=player_name).exists():
                                    f = Field.objects.get(tournament=self.tournament, partner=player_name)
                                    pga_num = f.partner_golfer.espn_number
                                else:
                                    print ('XXXXXXfield lookup issue: ', player_name)
                                    break
                            
                    
                                score_dict[player_name] = {'rank': rank, 'total_score': to_par, 'thru': thru, 'round_score': today, 'r1': r1, 'r2':r2, 'r3': r3, 'r4': r4, 'total_strokes': total_strokes, 'change': movement, 
                                                    'pga_num': pga_num, 'handicap': int(0), 'group': f.group.number}
                                #print ('PGA scrape dict: ', score_dict)

                        else:
                            return {'error': 'Only for Zurich, t_num 018'}
                        # try:
                        #     field = Field.objects.get(golfer__golfer_pga_num=ele_class, tournament=self.tournament)
                        #     field.rank = data[1]['rank']
                        #     field.save()
                        # except Exception as e:
                        #     print ('field lookup issue in scrape', ' pga_num: ', ele_class, data[0], e)
                        #     #field.handi = 0
                        # data[1].update({'pga_num': ele_class,
                        #                 'handicap': 'not found'
                        #                 })
                        # score_dict[data[0]] =  data[1]
                    #print (score_dict)
                    #sd.data = score_dict
                    #print (len(sd.data))
                
                #sd.save()
                #print (score_dict)
                #self.tournament.saved_cut_num = self.tournament.cut_num()
                #self.tournament.saved_round = self.tournament.get_round()
                #self.tournament.saved_cut_round = self.tournament.get_cut_round() 
                #self.tournament.save()
                print ('PGA scrape retunrin score dict len: ', len(score_dict))
                return score_dict                
            else:
                print ('scrape scores t mismatch', t, name)
                return {}
        
        except Exception as e:
            print ('scrape scores failed: ', e)
            return {}

        finally:
            driver.quit()


    
    def scrape(self):
        start = datetime.now()
        # try:

        #     html = urllib.request.urlopen(self.url)
        #     soup = BeautifulSoup(html, 'html.parser')

        #     name = soup.find('h1', {'class': 'name'})
        #     print (name.text.replace(' - Leaderboard', '').lstrip().rstrip())
        
        # except Exception as e:
        #     print ('Scrape Error finding Tournament Name', e)
        print ('starting MP SCRAPE')
        score_dict = {}
        options = ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")

        options.add_argument('--ignore-certificate-errors')
        options.add_argument("--window-size=1920,1080")
        


        driver = Chrome(options=options)

        print ('driver pre url: ', datetime.now() - start)
        driver.get(self.url)
        print ('driver after url: ', datetime.now() - start)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        print ('driver after soup: ', datetime.now() - start)
        table = (soup.find("div", {'id':'stroke-play-container'}))
        print ('tble len; ', len(table.find_all("tbody tr", {'class': 'line-row'})))
        print ('driver after table: ', datetime.now() - start)
        t = self.tournament
        t_ok = False

        print ('driver initialized: ', datetime.now() - start)
        try:
            title = soup.find('h1', {'class', 'name'})
            name = title.text

            if t.name == name.lstrip().rstrip():
               t_ok = True
            elif t.name == name.replace(' - Leaderboard', '').lstrip().rstrip():
                t_ok = True
            else: 
                print ('scrape name issue', 'db: ', t.name, 'scrape: ', name)
        
            if t_ok:
                try:
                    cut_line = driver.find_elements_by_class_name("cut-line")
                    for c in cut_line:
                        cut_score  = c.text.rsplit(' ', 1)[1]
                        #print ('full cutt text: ', c.text, 'cut score: ', c.text.rsplit(' ', 1)[1])
                        if "Projected" in c.text:
                            t.cut_score = "Projected cut score: " + c.text.rsplit(' ', 1)[1]
                            t.save()
                        else:
                            t.cut_score = "Cut Score: " + c.text.rsplit(' ', 1)[1]
                            t.save()
                except Exception as e:
                    print ('issue scraping cut-info class from pga leaderboard', e)
                    

                #find playoff data
                playoff = driver.find_elements_by_class_name("playoff-module")
                print (t.name, '-------playoff--------')
                print ('length', len(playoff))
                for p in playoff:
                    print (p.text)
                print (t.name, '-------end playoff------')

                if len(playoff) > 0:
                    t.playoff = True

                #table = driver.find_element_by_id("stroke-play-container")
                
                sd, created = ScoreDict.objects.get_or_create(tournament=self.tournament)                
                
                if self.mode == 'picks':
                    for pick in Picks.objects.filter(playerName__tournament=self.tournament).values('playerName__playerID').distinct():
                        row =  table.find("tr", {'class': 'line-row-' + str(pick.get('playerName__playerID'))})
                        data = get_data(self, row)
                        data[1].update({'pga_num': pick.playerID})
                        score_dict[data[0]] =  data[1]
                    #sd.pick_data = score_dict
                else:  #doing for "all" or None 
                    for row in table.find_all("tr", {'class': 'line-row'}):
                        print(row)
                        ele_class = row['class'][1].split('-')[2]
                        data = self.get_data(row)
                        try:
                            field = Field.objects.get(golfer__golfer_pga_num=ele_class, tournament=self.tournament)
                            field.rank = data[1]['rank']
                            field.save()
                        except Exception as e:
                            print ('field lookup issue in scrape', ' pga_num: ', ele_class, data[0], e)
                            #field.handi = 0
                        data[1].update({'pga_num': ele_class,
                                        'handicap': 'not found'
                                        })
                        score_dict[data[0]] =  data[1]
                    sd.data = score_dict
                    print (len(sd.data))
                
                sd.save()
                #print (score_dict)
                #self.tournament.saved_cut_num = self.tournament.cut_num()
                #self.tournament.saved_round = self.tournament.get_round()
                #self.tournament.saved_cut_round = self.tournament.get_cut_round() 
                #self.tournament.save()

                return (score_dict)                
            else:
                print ('scrape scores t mismatch', t, name)
                return {}
        
        except Exception as e:
            print ('scrape scores failed: ', e)
            return {}

        finally:
            driver.quit()

    def get_data(self, row):

            
            #print (row)
            #hard cocding courses to strip for RSM, make this extend to others
            n = row.find('td', {'class': 'player-name'}).text.rstrip('(SS)').rstrip('(PL)').rstrip(' ')
            if n[-1] == ' ':
                n = n[:-1]


            rank = row.find('td', {'class': 'position'}).text 
            pos = row.find('td', {'class': 'position-movement'})
            
            movement = pos.find('div', {'class': 'position-movement'})

            try:
                if movement.span != None:
                    c= str(movement.span) + movement.text
                else:
                    c= movement.text
            except Exception as e:
                c = '--'
                print ('cant scrape poasition move span')
            if row.find('td', {'class': 'thru'}) != None:
                thru = row.find('td', {'class': 'thru'}).text 
                round_score = row.find('td', {'class': 'round'}).text 
            elif row.find('td', {'class': 'tee-time'}) != None: 
                thru = row.find('td', {'class': 'tee-time'}).text
                round_score = 'E'
            else: 
                thru = "no info"
                round_score = 'E'

            total_score = row.find('td', {'class': 'total'}).text 

            if total_score == 'E':
                total_score = '0'
            
            round_list = []
            for i in range(len(row.find_all('td', {'class': 'round-x'}))):
                round_list.append(row.find_all('td', {'class': 'round-x'})[i].text)

            return (n, {'rank': rank, 'change': c, \
                'thru': thru, 'round_score': round_score, 'total_score': total_score , 'r1': round_list[0], 'r2': round_list[1], 'r3': round_list[2], 'r4': round_list[3]})

    def mp_final_16(self):
        try:
            start = datetime.now()
            bracket_dict = {}
            options = ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")

            driver = Chrome(options=options)

            print ('driver pre url: ', datetime.now() - start)
            driver.get(self.url)
            print ('driver after url: ', datetime.now() - start)

            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            print ('MP driver after soup: ', datetime.now() - start)
            
            leaderboard = soup.find('div', {'class': 'tab-knock out'})
            print ('after LB ', type(leaderboard), len(leaderboard))
            for round in leaderboard.find_all('div', {'class': 'live-scoring-data-container'}):
                round_title = round.find('div', {'class', 'header'}).text
                print (round_title)
                bracket_dict[round_title] = {}
                data = round.find('table', {'class': 'data-table'})
                matches = {}
                for i, match in enumerate(data.find_all('tr', {'class', 'data-table-row'}), start=1):
                    golfer1 = match.find('li', {'class': 'col-1'}).text
                    #print (self.tournament, self.tournament.season)
                    print ('g1', golfer1.split('(')[0].rstrip(), len(golfer1.split('(')[0].rstrip()))

                    g1_field = Field.objects.get(tournament=self.tournament, playerName=golfer1.split('(')[0].rstrip())
                    golfer2 = match.find('td', {'class': 'col4'}).text
                    print ('g2', golfer2.split('(')[0].rstrip())
                    g2_field = Field.objects.get(tournament=self.tournament, playerName=golfer2.split('(')[0])
                    if match.find('td', {'class': 'col2'}).find('span', {'class': 'icon-flag win'}):
                        print ('winner1', golfer1)
                        winner = golfer1
                        loser = golfer2
                    elif match.find('td', {'class': 'col4'}).find('span', {'class': 'icon-flag win'}):
                        print ('winner1', golfer1)
                        winner = golfer2
                        loser = golfer1
                    else:
                        print ('no winner', golfer1, golfer2)
                        winner = ''
                        loser = ''
                    bracket_dict[round_title]['match' + str(i)] = {'g1': golfer1.split('(')[0].rstrip(),
                                                                 #'g1_espn_num': g1_field.golfer.espn_number,
                                                                 'g2': golfer2.split('(')[0].rstrip(),
                                                                 #'g2_espn_num': g2_field.golfer.espn_number,
                                                                  'winner': winner.split('(')[0].rstrip(), 
                                                                  'loser': loser.split('(')[0].rstrip()}
            
            return bracket_dict

        except Exception as e:
            print ('scrape scores MP Field: ', e)
            return {}

        finally:
            driver.quit()

    def mp_brackets(self):
        try:
            ## commented field as that breaks the field set up process.  Should not need since using espn
            start = datetime.now()
            bracket_dict = {}
            options = ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            
            driver = Chrome(options=options)
            #time.sleep(30)
            print ('driver pre url: ', datetime.now() - start)
            driver.get(self.url)
            print ('driver after url: ', datetime.now() - start)
            print (driver.title)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            print ('MP driver after soup: ', datetime.now() - start)

            table = soup.find('table', {'class': 'chakra-table'})
            bracket_dict = {}
            for row in table.find_all('tr')[2:]:
                print ('Row TExt: ', row.text)
                if len(row.find_all('th')) > 0:
                    bracket_dict[row.text] = {}
                    grp = row.text
                elif len(row.find_all('td')) >1:
                    bracket_dict.get(grp).update({row.find_all('td')[1].text.split('(')[0].strip().replace(u'\xa0', u' '):
                                            {'wins': row.find_all('td')[2].text,
                                            'loss': row.find_all('td')[3].text,
                                            'draw': row.find_all('td')[4].text,
                                            'points': row.find_all('td')[5].text,
                                            'rank': row.find_all('td')[1].text.split('(')[1].split(')')[0],
                                            }})
                
            # first_group = (soup.find("div", {'id':'firstGroupContainer'}))
            # other_groups = (soup.find("div", {'id':'fromSecondToTheLastGroupContainer'}))

            # g_num = first_group.find('div', {'class': 'group-section-title'})
            # print (g_num.text)
            
            # golfer_rows = first_group.find_all('tr', {'class': 't-row'})
            # golfer_list = []
            # for r in golfer_rows[1:]:
            #     golfer_name = r.find('span', {'class': 'name'}).text.split('(')[0].rstrip(),
            #     won = r.find('td', {'class': 't-cell won score'}).text.lstrip('\n').rstrip('\n')
            #     lost = r.find('td', {'class': 't-cell lost score'}).text.lstrip('\n').rstrip('\n')
            #     tie = r.find('td', {'class': 't-cell halved score'}).text.lstrip('\n').rstrip('\n')
            #     total = r.find('td', {'class': 't-cell points score'}).text.lstrip('\n').rstrip('\n')
            #     pos = r.find('td', {'class': 't-cell position'}).text.lstrip('\n').rstrip('\n')
            #     #field = Field.objects.get(tournament=self.tournament, playerName=r.find('span', {'class': 'name'}).text.split('(')[0].rstrip())
            #     #web site doesn't have pga num, assume the field has played in other tornaments.  
            #     golfer_obj = Golfer.objects.get(golfer_name=r.find('span', {'class': 'name'}).text.split('(')[0].rstrip())
            #     #field = Field.objects.get(tournament=self.tournament, golfer=golfer_obj)
            #     #bracket_dict[field.golfer.espn_number] = {'group': g_num.text,
            #     bracket_dict[r.find('span', {'class': 'name'}).text.split('(')[0].rstrip()] = {'group': g_num.text,
            #     #bracket_dict[field.pk] = {'group': g_num.text,
            #                                 'pos': pos,
            #                                 'won': won,
            #                                 'lost': lost,
            #                                 'tie': tie,
            #                                 'total': total,
            #                                 #'golfer': r.find('span', {'class': 'name'}).text.split('(')[0].rstrip(),
            #                                 'espn_num': golfer_obj.espn_number,
            #                                 'pga_num': golfer_obj.golfer_pga_num,
            #                                 'golfer_name': r.find('span', {'class': 'name'}).text.split('(')[0].rstrip()}

            # for g in other_groups.find_all('div', {'class': 'group-stage-section'}):
            #     g_num = g.find('div', {'class': 'group-section-title'})
            #     #print (g_num.text)
            #     #golfer_list = []
            #     golfer_rows = g.find_all('tr', {'class': 't-row'})
            
            #     for r in golfer_rows[1:]:
            #         #golfer_list.append(r.find('span', {'class': 'name'}).text)
            #         #print (r.find('span', {'class': 'name'}).text)
            #         won = r.find('td', {'class': 't-cell won score'}).text.lstrip('\n').rstrip('\n')
            #         lost = r.find('td', {'class': 't-cell lost score'}).text.lstrip('\n').rstrip('\n')
            #         tie = r.find('td', {'class': 't-cell halved score'}).text.lstrip('\n').rstrip('\n')
            #         total = r.find('td', {'class': 't-cell points score'}).text.lstrip('\n').rstrip('\n')
            #         pos = r.find('td', {'class': 't-cell position'}).text.lstrip('\n').rstrip('\n')
            #         #field = Field.objects.get(tournament=self.tournament, playerName=r.find('span', {'class': 'name'}).text.split('(')[0].rstrip())
            #         golfer_obj = Golfer.objects.get(golfer_name=r.find('span', {'class': 'name'}).text.split('(')[0].rstrip())
            #         #field = Field.objects.get(tournament=self.tournament, golfer=golfer_obj)
            #         bracket_dict[r.find('span', {'class': 'name'}).text.split('(')[0].rstrip()] = {'group': g_num.text,
            #         #bracket_dict[field.golfer.espn_number] = {'group': g_num.text,
            #         #bracket_dict[field.pk] = {'group': g_num.text,
            #                                 'pos': pos,
            #                                 'won': won,
            #                                 'lost': lost,
            #                                 'tie': tie,
            #                                 'total': total,
            #                                 'golfer': r.find('span', {'class': 'name'}).text.split('(')[0].rstrip(),
            #                                 'espn_num': golfer_obj.espn_number,
            #                                 'pga_num': golfer_obj.golfer_pga_num, 
            #                                 'golfer_name': r.find('span', {'class': 'name'}).text.split('(')[0].rstrip()}
            
            return bracket_dict

        except Exception as e:
            print ('scrape scores MP Field: ', e)
            return {}

        finally:
            driver.quit()

    def get_field(self):
        try:
            start = datetime.now()
            field_dict = {}
            options = ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument('--ignore-certificate-errors')
            options.add_argument("--window-size=1920x1080")
            #options.add_argument('--no-sandbox')

            driver = Chrome(options=options)

            print ('driver pre url: ', datetime.now() - start)
            driver.get(self.url)
            print ('driver after url: ', datetime.now() - start)
            
            try:
                data = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="stroke-play-container"]/div/div[1]/div[4]/table'))) 
            except Exception as r:
                print ('wait exept', r)
            
            #print (data)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            lb =  soup.find('div', {'id': 'stroke-play-container'})
            tables = lb.find_all('table', {'class': 'leaderboard-table'})
            for t in tables:
                for row in t.find_all('tr', {'class': 'line-row'}):
                    name = row.find('div', {'class': 'player-name-col'}).text
                    
                    pga_num = row.attrs['class'][1].split('-')[2]
                    #print (name, pga_num)
                    field_dict[utils.reverse_names(name)] = (False, pga_num)

            return field_dict

        except Exception as e:
            print ('scrape field issue: ', e)
            return {}

        finally:
            driver.quit()



       
