from datetime import datetime
from wc_app.models import Stage, Group, Team, Data
import json
import os
import requests

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

        if stage:
            self.stage = stage
        elif Stage.objects.filter(current=True).count() == 1:
            self.stage = Stage.objects.get(current=True)
        else:
            self.stage = Stage.objects.get(name="Group Stage", event__current=True)

        if self.stage.score_url:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            response = requests.get(self.stage.score_url, headers=headers)

            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                self.wc_data = response.json()
                print("Success! Data loaded.")
                # Print the tournament name to verify
            else:
                print('ESPN Group Stage Data Error:', response.text)
        else:   
            with open(JSON_FILE) as f:
                self.wc_data = json.load(f)

        print('WC Init duration: ', datetime.now() - start)


    def get_group_data(self, create=False):
        data = {}
        for child in self.wc_data.get('children', []):
            group_name = child.get('name')
            entries = child.get('standings', {}).get('entries', [])
            data[group_name] = {
                team.get('team', {}).get('abbreviation'): {
                    'full_name': team.get('team', {}).get('displayName'),
                    'flag': team.get('team', {}).get('flag', ''),
                    'rank': next((x.get('value') for x in team.get('stats', []) if x.get('name') == 'rank'), None),
                    'info': '',
                }
                for team in entries
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
        stat_keys = ['gamesPlayed', 'wins', 'ties', 'losses', 'pointsFor', 'pointsAgainst', 'pointDifferential', 'points']
        score_dict = {}
        for child in self.wc_data.get('children', []):
            group_name = child.get('name')
            score_dict[group_name] = {}
            for team in child.get('standings', {}).get('entries', []):
                abbr = team.get('team', {}).get('abbreviation')
                stats = {x.get('name'): x.get('value') for x in team.get('stats', [])}
                score_dict[group_name][abbr] = {
                    'played': stats.get('gamesPlayed'),
                    'wins': stats.get('wins'),
                    'draw': stats.get('ties'),
                    'loss': stats.get('losses'),
                    'for': stats.get('pointsFor'),
                    'against': stats.get('pointsAgainst'),
                    'goal_diff': stats.get('pointDifferential'),
                    'points': stats.get('points'),
                }
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