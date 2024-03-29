import urllib.request
import json
from golf_app.models import Season, Tournament
from datetime import date, datetime
import ssl

class PGAData(object):
    
    def __init__(self, season=None, update=False, t=None):
        '''takes an optional season object, optional pga season tournament data'''
        if not season:
            self.season = Season.objects.get(current=True)
        else:
            self.season = season

        if self.season.data and not update:
            self.data = self.season.data
        else:
            ssl._create_default_https_context = ssl._create_unverified_context
            url = 'https://statdata.pgatour.com/r/current/schedule.json'
            with urllib.request.urlopen(url) as schedule_json_url:
                self.data = json.loads(schedule_json_url.read().decode())

        if t:
            self.t = t
        elif Tournament.objects.filter(season=self.season, current=True):
            self.t = Tournament.objects.get(current=True) 
        else:
            self.t = Tournament()
        
        if update:
            self.season.data = self.data
            self.season.save()

        for s in self.data.get('schedule'):
            for year in s.get('years'):
                if str(year.get('year')) == str(self.season.season):
                    for tour in year.get('tour'):
                        if tour.get('desc') == 'PGA TOUR':
                            self.t_data = tour.get('trns')
           
    
    def get_t_type(self, t_num):
        try:
            return [x.get('trnType') for x in self.t_data if str(x.get('permNum')) == str(t_num)][0]
        except Exception as e:
            print ('pga_t_data get_t_type error: ', e)
            return None

    def get_purse(self, t_num):
        try:
            return [x.get('Purse') for x in self.t_data if str(x.get('permNum')) == str(t_num)][0]
        except Exception as e:
            print ('pga_t_data get_t_type error: ', e)
            return None


    def get_t_name(self, t_num):
        try:
            return [x.get('trnName')[0].get('official') for x in self.t_data if str(x.get('permNum')) == str(t_num)][0]
        except Exception as e:
            print ('pga_t_data get_t_type error: ', e)
            return None
        

    def get_full_list(self):
        '''returns a dict'''
        d = {}
        for l in self.t_data:
            #if l.get('primaryEvent'):
            d[l.get('permNum')] = {'name': self.get_t_name(l.get('permNum')),
                                   'purse': self.get_purse(l.get('permNum')),
                                   'primary_event':  l.get('primaryEvent') }
            #else:
            #    print ('alt', l.get('trnName')[0].get('short'))
        return d

    def fedex_stats(self):
        '''no input, returns a dict'''
        
        total = len([x for x in self.t_data if x.get('trnType') in ['PLF', 'PLS']])
        complete_t = Tournament.objects.filter(season=self.season, complete=True).values_list('pga_tournament_num', flat=True)
        complete_count = len([x for x in self.t_data if x.get('permNum') in complete_t and x.get('trnType') in ['PLF', 'PLS']])
        remaining = total - complete_count

        d = {}
        d.update({'total': total, 'complete': complete_count, 'remaining': remaining})    
        
        return d

               
    def ryder_or_pres(self):
        if '468' in self.get_full_list().keys():
            return 'ryder'
        elif '500' in self.get_full_list().keys():
            return 'presidents'
        else:
            return None

    def next_t(self):

        curr_week = datetime.today().isocalendar()[1]
        if curr_week > 50:
            curr_week = 1
        next_week = min([x.get('date')[0].get('weeknumber') for x in self.t_data if int(x.get('date')[0].get('weeknumber')) == int(curr_week)])
        if next_week:
            w = next_week
        else:
            w = min([x.get('date')[0].get('weeknumber') for x in self.t_data])
              
        return [x.get('permNum') for x in self.t_data if str(x.get('date')[0].get('weeknumber')) == str(w)  and x.get('primaryEvent') == "Y"][0]


    # copied from espn schedule, use to fix this class
    # def current_event(self):
    #     if [v for v in self.schedule.get('events') if v.get('status')  == 'in']:
    #         return [v for v in self.schedule.get('events') if v.get('status') == 'in']

    #     end_date = datetime.now() + timedelta(days=5)
    #     start_date = datetime.utcnow()
        
    #     event = [v for v in self.schedule.get('events') if datetime.strptime(v.get('startDate')[:-1], '%Y-%m-%dT%H:%M') >= start_date \
    #                 and  datetime.strptime(v.get('startDate')[:-1], '%Y-%m-%dT%H:%M') < end_date]
    #     return event
