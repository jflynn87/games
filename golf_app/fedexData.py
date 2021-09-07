from golf_app.models import FedExField, FedExSeason, Season, Golfer
from golf_app import populateField, utils



class FedEx(object):
   def __init__(self, season=None):
      if season:
         self.season = season
      else:
         self.season = Season.objects.get(current=True)

      self.prior_season = Season.objects.get(season=int(self.season.season) -1)


   def get_data(self, save=True):
      '''takes a season object and optional bool, returns a dict'''
      data = populateField.get_fedex_data()
      if not FedExSeason.objects.filter(season__season=self.prior_season).exists():
         season = FedExSeason()
         season.season = Season.objects.get(season=self.prior_season)
      else:
         season = FedExSeason.objects.get(season__season=self.prior_season) 

      if save:
         season.prior_season_data = data
         season.save()
      
      return data

   def get_field(self):
      owgr = populateField.get_worldrank()
      
      for g in Golfer.objects.all():
         golfer_owgr = utils.fix_name(g.golfer_name, owgr)
         if int (golfer_owgr[1][0]) < 201:
            print (g, golfer_owgr)
      return
