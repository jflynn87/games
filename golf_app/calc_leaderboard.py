from golf_app.models import Picks, ScoreDict
#from scipy.stats import rankdata


class LeaderBoard(object):
    '''takes a tournamament object and round, returns a dict'''
    
    def __init__(self, tournament, t_round):
        self.tournament = tournament
        sd = ScoreDict.objects.get(tournament=self.tournament)
        self.score_dict = sd.data
        self.t_round = t_round


    def get_leaderboard(self):
        d = {}
        playing = {k:v for k,v in self.score_dict.items() if k != 'info' and v.get('rank') not in self.tournament.not_playing_list()}
        cuts = {k:v for k,v in self.score_dict.items() if k != 'info' and v.get('rank') in self.tournament.not_playing_list()}
        for g, data in playing.items():
            if g != 'info':
                s = self.golfer_score(data.get('pga_num'))
                d[g] = {'espn_num': data.get('pga_num'),
                    'pga_num': data.get('pga_num'),  #hack for optimal pick, fix
                    'score': s,
                    'handicap': data.get('handicap'),
                    'group': data.get('group')}

        for i, (k, v) in enumerate(sorted(d.items(), key=lambda x: x[1]['score'])):
            #print (i, k, v)
            if i == 0:
                d.get(k).update({'rank': 1})
                rank = 1
            elif d.get(k).get('score') == prior:
                d.get(k).update({'rank': rank})
            else:
                rank = i + 1
                d.get(k).update({'rank': rank})

            prior = v.get('score')

        if len(cuts) > 0:
            for g, data in cuts.items():
                #if g != 'info':
                s = self.score_dict.get('info').get('cut_num')
                d[g] = {'espn_num': data.get('pga_num'),
                        'pga_num': data.get('pga_num'),  #hack for optimal pick, fix 
                        'score': s,
                        'rank': data.get('rank'),
                        'handicap': data.get('handicap'),
                        'group': data.get('group')}

        d['info'] = self.score_dict.get('info')
        d.get('info').update({'leaderboard': True, 
                    'round': self.t_round})


        #print (d)
        return d


    def golfer_score(self, espn_num):
        
        if self.t_round == 1:
            return [int(v.get('r1')) for k,v in self.score_dict.items() if v.get('pga_num') == espn_num][0]
        elif self.t_round == 2:
            return [int(v.get('r2')) + int(v.get('r1')) for k,v in self.score_dict.items() if v.get('pga_num') == espn_num][0]
        elif self.t_round == 3:
            return [int(v.get('r3')) + int(v.get('r2')) + int(v.get('r1')) for k,v in self.score_dict.items() if v.get('pga_num') == espn_num][0]
        elif self.t_round == 4:
            return [int(v.get('r4')) + int(v.get('r3')) + int(v.get('r2')) + int(v.get('r1')) for k,v in self.score_dict.items() if v.get('pga_num') == espn_num][0]

