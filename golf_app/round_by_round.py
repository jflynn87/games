from golf_app import calc_leaderboard, bonus_details
from golf_app.models import Tournament, ScoreDict, Season, Group, Picks

from datetime import datetime


class RoundData(object):
    
    def __init__(self, tournament=None):
        '''takes an tournament and adds round by round json'''
        if tournament:
            self.tournament = tournament
        else:
            self.tournament = Tournament.objects.get(current=True)

    def update_data(self):
        d = {}
        
        start = datetime.now()

        if self.tournament.special_field():
            return {}
        
        t = self.tournament  #shortening to make code cleaner
        
        sd = ScoreDict.objects.get(tournament=t)
        for r in range(1,5):
            round_start = datetime.now()
            print ('ROUND ', r)
            d.update({'round_' + str(r):{'scores': {}, 'leaders': {}, 'optimal_picks': {} }})
            lb = calc_leaderboard.LeaderBoard(t, r).get_leaderboard()
            if int(t.season.season) > 2019:
                optimal_picks = {}
                optimal_start = datetime.now()
                for g in Group.objects.filter(tournament=t):
                    optimal = g.optimal_pick(lb)
                    optimal_picks[str(g.number)] = {}
                    for espn_num, golfer in optimal.items():
                        optimal_picks.get(str(g.number)).update({espn_num: golfer}) 
                #print ('round ', r, optimal_picks)
                d.get('round_' + str(r)).update({'optimal_picks': optimal_picks})
                print ('optimal duration: ', datetime.now() - optimal_start)
                
            pick_loop_start = datetime.now()
            for pick in Picks.objects.filter(playerName__tournament=t):
                print (pick, pick.playerName.golfer.espn_number)
                if pick.playerName.handi:
                    handi = pick.playerName.handi
                else:
                    handi = 0
                if d.get('round_' + str(r)).get('scores').get(pick.user.username):
                    print ('this is ok', [v.get('rank') - handi for v in lb.values() if v.get('espn_num') == pick.playerName.golfer.espn_number])
                    d.get('round_' + str(r)).get('scores').update({pick.user.username: d.get('round_' + str(r)).get('scores').get(pick.user.username) + \
                    [v.get('rank') - handi for v in lb.values() if v.get('espn_num') == pick.playerName.golfer.espn_number][0]})
                else:
                    d['round_' + str(r)]['scores'].update({pick.user.username: [v.get('rank') - handi for v in lb.values() if v.get('espn_num') == pick.playerName.golfer.espn_number][0]})
                
                if d.get('round_' + str(r)).get('optimal_picks'):
                    bd = bonus_details.BonusDtl(espn_scrape_data=sd.data, tournament=t, inquiry=True)
                    if bd.best_in_group(d.get('round_' + str(r)).get('optimal_picks').get(str(pick.playerName.group.number)) , pick):
                        d.get('round_' + str(r)).get('scores').update({pick.user.username: d.get('round_' + str(r)).get('scores').get(pick.user.username) -10})
            print ('pick loop dur: ', datetime.now() - pick_loop_start)
            low_score = min(d.get('round_' + str(r)).get('scores').items(), key=lambda v: v[1])[1]
            
            leaders = {k:v for k,v in d.get('round_' + str(r)).get('scores').items() if v == low_score}
            d.get('round_' + str(r)).update({'leaders': leaders})

            print ('round dur: ', datetime.now() - round_start)

        print ('dur: ', datetime.now() - start)

        return d