from datetime import datetime
from urllib import request
from bs4 import BeautifulSoup
from wc_app.models import Event, Stage, Group, Team, Data
#from selenium import webdriver
#from webdriver_manager.chrome import ChromeDriverManager
#from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.common.by import By
import json



class ESPNData(object):
    '''takes an optinal dict and provides funcitons to retrieve espn golf data,
        all_data is a list of dicts
        event_data is the data for the event but most is in competition
        competition_data varoius datat about  the tournament
        field_data is the actual golfers in the tournament'''

    #only use event_data for match play events, other data not reliable.
    def __init__(self, url=None, stage=None):
        start = datetime.now()

        if url:
            self.url = url
        else:
            self.url ='https://www.espn.com/soccer/table/_/league/fifa.world'
        
        html = request.urlopen(self.url)
        self.soup = BeautifulSoup(html, 'html.parser')

        if stage:
            self.stage = stage
        elif Stage.objects.filter(current=True).count() ==1:
            self.stage = Stage.objects.get(current=True)
        else:
            self.stage = Stage.objects.get(name="Group Stage",event__current=True)

        print ('WC Init duration: ', datetime.now() - start)

        # is this updated as games start?  https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard



    def get_group_data(self, create=False):
        t_body = self.soup.find_all('tbody', {'class': "Table__TBODY"})[0]
        data = {}
        for i, row in enumerate(t_body.find_all('tr')):
            if 'subgroup-headers' in row['class']:
                data[row.text] = {}
                g = row.text
            else:    
                #print (row.find_all('a')[1].text)
                #print (row.find_all('a')[2].text)#, row.find_all('td')[1].text)
                team =  row.find_all('a')[1].text
                full_name = str(row.find_all('a')[2].text)
                team_info =  'https://www.espn.com' + str(row.find('a')['href'])
                flag = 'https://a.espncdn.com/combiner/i?img=/i/teamlogos/countries/500/' + str(row.find('img')['alt'].lower()) + '.png&h=40&w=40' 
                data.get(g).update({team: { 
                                'info': team_info, 
                                'flag': flag,
                                'full_name': full_name,
                                'rank': row.find_all('td')[0].find_all('span')[0].text,
                                'index': i}})

        if create:
            rankings = self.get_rankings(use_file=True)
            print ('len rankings; ', len(rankings))
    
            stage = Stage.objects.get(current=True)
            Group.objects.filter(stage=stage).delete()
            Team.objects.filter(group__stage=stage).delete()

            for group, teams in data.items():
                g, g_created = Group.objects.get_or_create(stage=stage, group=group)
                for team, data in teams.items():
                    if rankings.get(team):
                        t, t_created = Team.objects.get_or_create(group=g, name=team,\
                                        rank=rankings.get(team).get('rank'), flag_link=data.get('flag'), \
                                        info_link=data.get('info'), full_name=data.get('full_name')) 
                    else:
                        t, t_created = Team.objects.get_or_create(group=g, name=team,\
                                        flag_link=data.get('flag'), \
                                        info_link=data.get('info'), full_name=data.get('full_name'), rank=65) 
                        print ("NO RANKING :", team)

            print ('Created WC Groups: ', Group.objects.filter(stage=stage).count(), ' Teams: ', Team.objects.filter(group__stage=stage).count())        


        return data

    def get_group_records(self, data=None):
        if not data:
            data = self.get_group_data()

        score_dict = {}
        for i, r in enumerate(self.soup.find_all('tbody', {'class': "Table__TBODY"})[1]):
            #print (r.find_all('td')[0]['class'])
            if 'tar' not in r.find_all('td')[0]['class']:
                team = {k:team for k,v in data.items() for team,d  in v.items() if d.get('index') == i} #[0]
                print (team, [k for k,v in team.items()][0])
                #score_dict[team] = {'played': r.find_all('td')[0].text,
                if score_dict.get([k for k,v in team.items()][0]):
                    score_dict.get([k for k,v in team.items()][0]).update({[v for k,v in team.items()][0]: {'played': r.find_all('td')[0].text,
                                    'wins': r.find_all('td')[1].text,
                                    'draw': r.find_all('td')[2].text,
                                    'loss': r.find_all('td')[3].text,
                                    'for': r.find_all('td')[4].text,
                                    'against': r.find_all('td')[5].text,
                                    'goal_diff': r.find_all('td')[6].text,
                                    'points': r.find_all('td')[7].text,
                                    }})

                else:

                    score_dict[[k for k,v in team.items()][0]] = {[v for k,v in team.items()][0]: {'played': r.find_all('td')[0].text,
                                    'wins': r.find_all('td')[1].text,
                                    'draw': r.find_all('td')[2].text,
                                    'loss': r.find_all('td')[3].text,
                                    'for': r.find_all('td')[4].text,
                                    'against': r.find_all('td')[5].text,
                                    'goal_diff': r.find_all('td')[6].text,
                                    'points': r.find_all('td')[7].text,
                                    }}

        return score_dict

    
    def get_rankings(self, refresh=False, save_file=False, use_file=False):
        d = {}

        if use_file:
            d = open('fifa_rankings_2022.json')
            return json.load(d)
       
        else:
            try:
                options = Options()
                options.add_argument("--no-sandbox")
                options.add_argument("--headless")
                options.add_argument("--disable-gpu")
                #options.headless = True
                #options.sandbox = False
                #options.disable-gpu = True


                driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
                driver.get("https://www.fifa.com/fifa-world-ranking/men?dateId=id13792")
                #url = 'https://www.fifa.com/fifa-world-ranking'
                #table = driver.find_element(By.XPATH,'//*[@id="content"]/main/section[1]/div/div/div[2]/div[1]/div[1]/div/table')
                table = driver.find_element(By.CSS_SELECTOR, '#content > main > section.ff-pt-64.ff-pb-32.ff-bg-grey-lightest > div > div > div:nth-child(1) > table')
                for r in table.find_elements(By.CSS_SELECTOR, 'tr')[1:]:
                    rank = ''
                    team = ''
                    points = ''
                    change = ''
                    for i, cell in enumerate(r.find_elements(By.TAG_NAME, 'td')):
                        if i == 0:
                            rank = cell.text
                        elif i == 2:
                            team = cell.text
                        elif i == 3:
                            points = cell.text
                        elif i == 7:
                            change = cell.text
                    
                    d[team] = {'rank': rank, 'points': points, 'change': change}

                #hard coding over 50 teams to avoid complex scrolling logic
                d['KSA'] = {'rank': '51', 'points': '1437.78', 'change': '2.04'}        
                d['GHA'] = {'rank': '61', 'points': '1393', 'change': '-0.47'}        

                json_obj = json.dumps(d)
                with open ('fifa_rankings_2022.json', 'w') as outfile:
                    outfile.write(json_obj)

            except Exception as e:
                print ("WC rankings error: ", e)
            finally:
                driver.close()
                return d 


    def new_data(self):
        try:
            
            saved_d = Data.objects.get(stage=self.stage)
            if saved_d.force_refresh:
                return True
            if saved_d.group_data == self.get_group_data():
                print ('no new data')
                return False
            else:
                print ('new data')
                return True
        except Exception as e:
            print ('ESPN WC API new data check error: ', e)
            return True