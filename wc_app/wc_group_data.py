from datetime import datetime
from wc_app.models import Stage, Group, Team, Data
import json
import os

JSON_FILE = os.path.join(os.path.dirname(__file__), 'wc_groups.json')



class ESPNData(object):
    '''takes an optinal dict and provides funcitons to retrieve espn golf data,
        all_data is a list of dicts
        event_data is the data for the event but most is in competition
        competition_data varoius datat about  the tournament
        field_data is the actual golfers in the tournament'''

    #only use event_data for match play events, other data not reliable.
    def __init__(self, stage=None):
        start = datetime.now()

        with open(JSON_FILE) as f:
            self.wc_data = json.load(f)

        if stage:
            self.stage = stage
        elif Stage.objects.filter(current=True).count() == 1:
            self.stage = Stage.objects.get(current=True)
        else:
            self.stage = Stage.objects.get(name="Group Stage", event__current=True)

        print('WC Init duration: ', datetime.now() - start)


    def get_group_data(self, create=False):
        teams_lookup = self.wc_data['teams']
        data = {
            g['name']: {
                abbr: {
                    'full_name': teams_lookup[abbr]['name'],
                    'flag': teams_lookup[abbr]['flag_url'],
                    'rank': teams_lookup[abbr]['fifa_ranking'],
                    'info': '',
                }
                for abbr in g['teams']
            }
            for g in self.wc_data['groups']
        }

        if create:
            stage = self.stage
            Group.objects.filter(stage=stage).delete()
            Team.objects.filter(group__stage=stage).delete()

            for group_name, teams in data.items():
                g, _ = Group.objects.get_or_create(stage=stage, group=group_name)
                for abbr, td in teams.items():
                    Team.objects.get_or_create(
                        group=g, name=abbr,
                        defaults=dict(full_name=td['full_name'], flag_link=td['flag'],
                                      info_link=td['info'], rank=td['rank'])
                    )

            print('Created WC Groups: ', Group.objects.filter(stage=stage).count(),
                  ' Teams: ', Team.objects.filter(group__stage=stage).count())

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