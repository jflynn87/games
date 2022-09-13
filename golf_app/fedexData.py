from golf_app.models import FedExField, FedExSeason, Season, Golfer
from golf_app import populateField, utils
import urllib
from bs4 import BeautifulSoup



class FedEx(object):
   def __init__(self, season=None):
      if season:
         self.season = season
      else:
         self.season = Season.objects.get(current=True)

      self.prior_season = Season.objects.get(season=int(self.season.season) -1)


   def get_data(self):
      '''returns a dict'''
      # data = populateField.get_fedex_data()
      # if not FedExSeason.objects.filter(season__season=self.prior_season).exists():
      #    season = FedExSeason()
      #    season.season = Season.objects.get(season=self.prior_season)
      # else:
      #    season = FedExSeason.objects.get(season__season=self.prior_season) 

      # if save:
      #    season.prior_season_data = data
      #    season.save()
      
      # return data
      
      # moved prior season data logic to populatefield for first tournament of season
      total = 214  # need to find this manually from the pga web
      r = 50
      start = 1
      m = 50
      d = {}
      while total >= m:
         url = 'https://www.pgatour.com/news/2022/09/08/2022-2023-pga-tour-full-membership-fantasy-rankings-' + str(start) + '-' + str(m) + '.html'
         print (url)
         html = urllib.request.urlopen(url)
         soup = BeautifulSoup(html, 'html.parser')
         div = soup.find('div', {'class': 'table parbase section'})
         table = div.find('table')
         for row in table.find_all('tr')[1:]:
            d[row.find_all('td')[1].text.strip()] = {
                  'fantasy_rank': row.find_all('td')[0].text.strip(),
                  'age': row.find_all('td')[2].text.strip(),
                  '2022_earnings': row.find_all('td')[3].text.strip(),
                  'status': row.find_all('td')[4].text.strip(),
                  'comment': row.find_all('td')[5].text.strip()
                  
            }

         start = start + r
         m = m + r
         if m > total:
            m = total
         if start > total:
            print ('get fedex start of season done looping thru pages ', m)
            break

      #print (d, len(d))

      return d


   def create_field(self):
      owgr = populateField.get_worldrank()
      d = {}
      for g in Golfer.objects.all().exclude(golfer_pga_num=''):
         golfer_owgr = utils.fix_name(g.golfer_name, owgr)
         if int (golfer_owgr[1][0]) < 201:
            #d[g.golfer_name] = golfer_owgr[1]
            season = FedExSeason.objects.get(season__current=True)
            print (g,  golfer_owgr[1][0])
            
            field, created= FedExField.objects.get_or_create(season=season, golfer=g)
            field.soy_owgr = golfer_owgr[1][0]
            prior = utils.fix_name(g.golfer_name, season.prior_season_data)
            print ('PRIOR ', prior, type(prior))
            if type(prior[1]) == dict and prior[1].get('rank'):
               field.prior_season_data = prior[1]    
            else:
               field.prior_season_data = {}
            
               
            d[g.golfer_name] = {'soy_owgr' : golfer_owgr[1][0], 'prior_season': field.prior_season_data}
            field.save()
         #print (d)
      return d

