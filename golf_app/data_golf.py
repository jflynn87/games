import ast 
from requests import get
from golf_app.utils import fix_name, name_first_last, convert_floats_to_decimal
from datetime import datetime
import os
import boto3
from golf_app.models import Tournament, Field
from user_app.services import DynamoStatsTable
import json

STATS_TABLE = DynamoStatsTable()


class GolferSG:
    def __init__(self, t, field, data=None):
        '''takes a tournament object, field object or data'''
        
        self.t = t

        if isinstance(field, Field):
            self.field = field
        else:
            raise Exception('GolferSG exception - field must be Field object')

        if data and isinstance(data, dict):
            self.data = data
        elif not data:
            try:
                self.data = self.get_stats()
            except Exception as e:
                print ('GolferSG exception: ', e)
                self.data = None
        else:
            raise Exception(f'GolferSG exception - data must be dict but is:, {type(data)}')


    def format_data(self):
        d = {'ts': str(datetime.now())}
        d.update(self.data)
        return convert_floats_to_decimal(d)
    
    def save_data(self):
        formatted_data = self.format_data()
        STATS_TABLE.upsert_item(formatted_data)


    def get_stats(self):
        try:
            resp = STATS_TABLE.table.get_item(Key={'pk': str(self.t.pk),
                                        'sk': str(self.field.pk)})
            return resp.get('Item')       
        except Exception as e:
            print ('GolferSG get stats exception: ', e)
            return None
    

class DataGolf(object):
    def __init__(self, t, create=False, data=None, save=False):
        start = datetime.now()
        self.t = t

        if data:
            self.data = data
        else:
            if create:
                season = str(self.t.season.season)
                print (f'Creating ShotsGained for t: {self.t}')
                headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
                html = get("https://datagolf.com/performance-table", headers=headers).text
                table = html.split('var reload_data = ')[1].split("'")[1].split('var tour_dict = ')[0].replace(';', '').replace('\n', '').replace(' ', '')
                #print (season, type(season), json.loads(table))
                #self.data = ast.literal_eval(table).get('data').get(season).get('table')
                self.data = json.loads(table).get('data').get(season).get('table')
                #print (self.data)
                if save:
                    self.save_all_data()
            else:
                raise Exception('DataGolf exception - need data or create=True')

        print (f"Data Golf init complete, dur: {datetime.now() - start}")

    @property
    def data_as_dict(self):
        if not hasattr(self, '_data_as_dict'):
            self._data_as_dict = self.get_data_as_dict()
        return self._data_as_dict

    
    def get_data_as_dict(self):
        data = {}
        for row in self.data:
            f_name = name_first_last(row.get('player_name'))
            if f_name not in data.keys():
                data[f_name] = {}
            data[f_name] = row
        
        return data


    def get_player_stats(self, player_name):
        d = [x for x in self.data if name_first_last(x.get('player_name')) == player_name]
        if len(d) == 1:
            return d[0]
        else:
            fix_player = fix_name(player_name, self.data_as_dict)
            if fix_player[0]:
                return fix_player[1]
        
        print ('Shots Gained stat not found for : ', player_name)
        return None
    
    def save_all_data(self):
        #batch save 50 at a time
        l = []
        for f in Field.objects.filter(tournament=self.t):
            stats = self.get_player_stats(f.playerName)
            if stats:
                g = GolferSG(self.t, f, stats).format_data()
                g = convert_floats_to_decimal(g)
                l.append({'pk': str(f.tournament.pk),
                          'sk': str(f.pk),
                          **g})
            #else:
            #    print ('Shot Gained - no stats for: ', f.playerName)

        resp = STATS_TABLE.batch_upsert(l)
        # with STATS_TABLE.batch_writer() as batch:
        #     for i, row in enumerate(l):
        #         print (f"{row.get('player_name')} - saving ")
        #         try:
        #             batch.put_item(row)
        #         except Exception as e:
        #             print ('error saving: ', row.get('player_name'), e)
        #         print (f"save processed {i+1} records of {len(l)}")
        return True


