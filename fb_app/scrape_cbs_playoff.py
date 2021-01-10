import datetime

import urllib.request
import json
from bs4 import BeautifulSoup
from fb_app.models import Week, Teams, Games


class ScrapeCBS(object):

    def __init__(self):
        pass

    def get_data(self):


        print ('scraping CBS playoff class')

        try:
            stat_dict = {}

            game = Games.objects.get(week__current=True, playoff_picks=True)
            

            print ('url', 'https://www.cbssports.com/nfl/gametracker/boxscore/NFL_' + str(game.game_time.date()).replace('-', '') + '_' + game.away.typo_name + '@' + game.home.nfl_abbr + '/')
            html = urllib.request.urlopen('https://www.cbssports.com/nfl/gametracker/boxscore/NFL_' + str(game.game_time.date()).replace('-', '') + '_' + game.away.nfl_abbr + '@' + game.home.nfl_abbr + '/')
            #html = urllib.request.urlopen("https://www.cbssports.com/nfl/gametracker/boxscore/NFL_20210103_DAL@NYG/")

            soup = BeautifulSoup(html, 'html.parser')

            player_sect = soup.find('div', {'id': 'game-data-container'})
            team_sect = soup.find('div', {'id': 'team-stats-container'})

            teams = player_sect.find_all('div', {'class': 'abbr'})
            home = teams[1].text.rstrip().lstrip()
            away = teams[0].text.rstrip().lstrip()
            print (home, away)
            stat_dict['home'] = {'team': home}
            stat_dict['away'] = {'team': away}
## player stats section
            stats = soup.find('div', {'id': 'player-stats-container'})

            away_stats = stats.find('div', {'id': 'player-stats-away'})
            home_stats = stats.find('div', {'id': 'player-stats-home'})
            
            #passing yards section
            home_passing_dtl = self.passing_stats(home_stats.find('div', {'class': 'passing-ctr'}))
            away_passing_dtl = self.passing_stats(away_stats.find('div', {'class': 'passing-ctr'}))
            stat_dict['home']['passing'] = home_passing_dtl
            stat_dict['away']['passing'] = away_passing_dtl

            #rushing section
            home_rushing_dtl = self.rushing_stats(home_stats.find('div', {'class': 'rushing-ctr'}))
            away_rushing_dtl = self.rushing_stats(away_stats.find('div', {'class': 'rushing-ctr'}))
            stat_dict['home']['rushing'] = home_rushing_dtl
            stat_dict['away']['rushing'] = away_rushing_dtl

            #receiving section
            home_receiving_dtl = self.receiving_stats(home_stats.find('div', {'class': 'receiving-ctr'}))
            away_receiving_dtl = self.receiving_stats(away_stats.find('div', {'class': 'receiving-ctr'}))
            stat_dict['home']['receiving'] = home_receiving_dtl
            stat_dict['away']['receiving'] = away_receiving_dtl

            #FG section
            home_fg_dtl = self.fg_stats(home_stats.find('div', {'class': 'kicking-ctr'}))
            away_fg_dtl = self.fg_stats(away_stats.find('div', {'class': 'kicking-ctr'}))
            stat_dict['home']['fg'] = home_fg_dtl
            stat_dict['away']['fg'] = away_fg_dtl
            

            # DEF section
            home_def_dtl = self.def_stats(home_stats.find('div', {'class': 'defense-ctr'}))
            away_def_dtl = self.def_stats(away_stats.find('div', {'class': 'defense-ctr'}))
            stat_dict['home']['def'] = home_def_dtl
            stat_dict['away']['def'] = away_def_dtl


## end player stats

## team stats section
            team_stats = soup.find('div', {'id': 'stats-graph-container'})
            pass_row = team_stats.find('tr', {'data-category': 'passing_yards'})
            rush_row = team_stats.find('tr', {'data-category': 'rushing_yards'})
            total_row = team_stats.find('tr', {'data-category': 'total_yards'})
            
            stat_dict['home']['team_stats'] = {'passing': pass_row.find('td', {'class': 'stat-value home'}).text,
                                               'rushing': rush_row.find('td', {'class': 'stat-value home'}).text,
                                               'total': total_row.find('td', {'class': 'stat-value home'}).text}

            stat_dict['away']['team_stats'] = {'passing': pass_row.find('td', {'class': 'stat-value away'}).text,
                                               'rushing': rush_row.find('td', {'class': 'stat-value away'}).text,
                                               'total': total_row.find('td', {'class': 'stat-value away'}).text 
            }


## end team stats


## scores
            stat_dict['home']['team_stats'].update({'score': soup.find('div', {'class': 'hud-table-cell team-score-container home'}).text.strip()})
            stat_dict['away']['team_stats'].update({'score': soup.find('div', {'class': 'hud-table-cell team-score-container away'}).text.strip()})
            stat_dict['qtr'] = soup.find('div', {'class': 'final-text'}).text
            
## end scores

## turnovers
            turnovers = team_sect.find_all('tr')[21].find_all('td')
            stat_dict['home']['team_stats']['turnovers'] = turnovers[2].text
            stat_dict['away']['team_stats']['turnovers'] = turnovers[1].text

##end turnovers

## other TD's
            other_tds = team_sect.find_all('tr')[20].find_all('td')
            stat_dict['home']['team_stats']['other_tds'] = other_tds[2].text
            stat_dict['away']['team_stats']['other_tds'] = other_tds[1].text

##end other TD's

## QB rating 



## end QB rating

            #print (stat_dict)
            return stat_dict

        except Exception as e:
            print ('issue scraping CBS', e)
            return {}   

    def passing_stats(self, ele):
            stat_dict = {}
            for row in ele.find_all('tr', {'class': 'no-hover data-row'}):
                player = row.find('td', {'class': 'name-element'})
                data = row.find_all('td', {'class': 'number-element'})
                rating = row.find_all('td', {'class': 'hover-data'})[3].text
                stat_dict.update( {player.text.strip(): {'cp/att': data[0].text,
                    'yards': data[1].text,
                    'tds': data[2].text,
                    'ints': data[3].text,
                    #'rating': rating  - stat is wrong on cbs.com so will calc separately
                }})

            return stat_dict

    def rushing_stats(self, ele):
            stat_dict = {}
            for row in ele.find_all('tr', {'class': 'no-hover data-row'}):
                player = row.find('td', {'class': 'name-element'})
                data = row.find_all('td', {'class': 'number-element'})
                stat_dict.update({player.text.strip(): {'att': data[0].text,
                    'yards': data[1].text,
                    'tds': data[2].text,
                    'lg': data[3].text,
                }})

            return stat_dict


    def receiving_stats(self, ele):
            stat_dict = {}
            for row in ele.find_all('tr', {'class': 'no-hover data-row'}):
                player = row.find('td', {'class': 'name-element'})
                data = row.find_all('td', {'class': 'number-element'})
                stat_dict.update({player.text.strip(): {'targets': data[0].text,
                    'rec': data[1].text,
                    'yards': data[2].text,
                    'tds': data[3].text,
                    'lg:': data[4].text,
                }})

            return stat_dict


    def fg_stats(self, ele):
            stat_dict = {}
            for row in ele.find_all('tr', {'class': 'no-hover data-row'}):
                player = row.find('td', {'class': 'name-element'})
                data = row.find_all('td', {'class': 'number-element'})
                stat_dict.update({player.text.strip(): {'fg/att': data[0].text,
                    'long': data[1].text,
                    'xpts': data[2].text,
                    
                }})

            return stat_dict


    def def_stats(self, ele):
            stat_dict = {}
            for row in ele.find_all('tr', {'class': 'no-hover data-row'}):
                player = row.find('td', {'class': 'name-element'})
                data = row.find_all('td', {'class': 'number-element'})
                stat_dict.update({player.text.strip(): {'t-a': data[0].text,
                    'sacks': data[1].text,
                    'int': data[2].text,
                    
                }})

            return stat_dict



