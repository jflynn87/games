from golf_app.models import FedExField, FedExSeason, Season, Golfer, Field
from golf_app import utils, fedexData, populateField



class FedExSetup(object):
    def __init__(self, season=None):

        if season:
            self.season = season
        elif FedExSeason.objects.filter(season__current=True).exists():
            self.season = FedExSeason.objects.get(season__current=True)
        else:
            print ('setup Fedex season')
            self.season = self.setup_season()

        # if update:
        #     self.update = True
        # else:
        #     self.update = False

        self.data = fedexData.FedEx().get_data()


    def setup(self):
        
        g_dict = {}
        d = {}
        for golfer in Golfer.objects.all():
            g_dict[golfer.golfer_name] = {golfer.golfer_pga_num}

        owgr = populateField.get_worldrank()
        
        for k,v in self.data.items():
            if Golfer.objects.filter(golfer_name=k).exists():
                pga_num = Golfer.objects.get(golfer_name=k).golfer_pga_num
                g = populateField.get_golfer(k, pga_num)  #use this to update pic or flag if required
            else:
                fix_name = utils.fix_name(k, g_dict)
                if not fix_name[0]:
                    pga_num = populateField.find_pga_num(k)
                    if pga_num:
                        if Golfer.objects.filter(golfer_pga_num=str(pga_num)).exists():
                            g = populateField.get_golfer(Golfer.objects.get(golfer_pga_num=str(pga_num)), pga_num)
                        else:
                            print ('create here ', k, pga_num)
                            g = populateField.get_golfer(k, pga_num)
                    else:
                        print ('NO PGA num found', k)
                        g = populateField.get_golfer(k)
                else:
                    g = Golfer.objects.get(golfer_name=fix_name[0])
            print (self.season, g)
            f, created = FedExField.objects.get_or_create(season=self.season, golfer=g)
            ranks = utils.fix_name(g.golfer_name, owgr)
            if not ranks[0]:
                print ("OWGR LOOKUP ISSUe", k, g.golfer_name)
                f.soy_owgr = 9999
            else:
                f.soy_owgr = ranks[1][1]
            
            f.prior_season_data = v
            if self.season.prior_season_data.get(k):
               prior_season_fedex_rank = self.season.prior_season_data.get(k).get('rank')
            else:
                prior_season_fedex_rank = 'n/a'
            f.prior_season_data.update({'rank': prior_season_fedex_rank})
            prior_season = Season.objects.get(season=int(self.season.season.season) - 1)
            f.prior_season_data.update({'starts': Field.objects.filter(tournament__season=prior_season, golfer=g).count()})
            f.save()

        return d

    def setup_season(self):
        fs = FedExSeason()
        fs.season = Season.objects.get(current=True)
        fs.allow_picks = True
        d = populateField.get_fedex_data()
        print (d)
        fs.prior_season_data = d
        fs.save()

        return fs

