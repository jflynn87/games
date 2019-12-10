import urllib.request
import json

class PGAScore(object):
    
    def __init__(self, tournament_num):
        self.tournament_num = tournament_num
        self.json_url = 'https://statdata.pgatour.com/r/' + self.tournament_num + '/2020/leaderboard-v2mini.json'
        
        with urllib.request.urlopen(self.json_url) as field_json_url:
                self.json = json.loads(field_json_url.read().decode())

    def has_cut(self):
                
        return self.json['leaderboard']['cut_line']['show_cut_line']
            
    def players_making_cut(self):
       
        if self.json['leaderboard']['cut_line']['paid_players_making_cut']:
            return self.json['leaderboard']['cut_line']['paid_players_making_cut']
        else:
            return len(self.json['leaderboard']['players'])
    
    def cut_status(self):
       if self.json['leaderboard']['cut_line']['show_projected'] == "False":
           return "Projected"
       else:
           return "Actual"
    
    def cut_count(self):
        if self.json['leaderboard']['cut_line']['cut_count'] is False:
            return self.players_making_cut()
        else:
            return self.json['leaderboard']['cut_line']['cut_count']
    
    def round(self):
        
        return self.json['debug']["current_round_in_setup"]
    
    def started(self):
        return self.json['leaderboard']['is_started']
    
    def finished(self):
        self.json['leaderboard']['is_finished']
    
    def get_golfer_by_id(self, player_id):
        row = self.json["leaderboard"]['players']
        for golfer in row:
            if golfer['player_id'] == player_id:
               return golfer
        return "Golfer ID not found"

    def get_golfer_dict(self):
        return self.json['leaderboard']['players']
