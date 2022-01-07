from golf_app import calc_leaderboard, bonus_details
from golf_app.models import Tournament, ScoreDict, Group, Picks, TotalScore, BonusDetails

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
        #print ("ROUND BY ROUND")
        start = datetime.now()

        if self.tournament.special_field():
            return {}
        
        t = self.tournament  #shortening to make code cleaner
        
        sd = ScoreDict.objects.get(tournament=t)
        for r in range(1,5):
            round_start = datetime.now()
            #print ('ROUND ', r)
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
                #print ('optimal duration: ', datetime.now() - optimal_start)
                
            pick_loop_start = datetime.now()
            for pick in Picks.objects.filter(playerName__tournament=t):
                #print (pick, pick.playerName.golfer.espn_number)
                # if pick.playerName.handi:
                #     handi = pick.playerName.handi
                # else:
                #     handi = 0
                if d.get('round_' + str(r)).get('scores').get(pick.user.username):
                    
                    d.get('round_' + str(r)).get('scores').update({pick.user.username: d.get('round_' + str(r)).get('scores').get(pick.user.username) + \
                        pick.playerName.calc_score(lb)})
                    #[v.get('rank') - handi for v in lb.values() if v.get('espn_num') == pick.playerName.golfer.espn_number][0]})
                else:
                    #d['round_' + str(r)]['scores'].update({pick.user.username: [v.get('rank') - handi for v in lb.values() if v.get('espn_num') == pick.playerName.golfer.espn_number][0]})
                    d['round_' + str(r)]['scores'].update({pick.user.username: pick.playerName.calc_score(lb)})
                
                if d.get('round_' + str(r)).get('optimal_picks'):
                    bd = bonus_details.BonusDtl(espn_scrape_data=sd.data, tournament=t, inquiry=True)
                    if bd.best_in_group(d.get('round_' + str(r)).get('optimal_picks').get(str(pick.playerName.group.number)) , pick):
                        d.get('round_' + str(r)).get('scores').update({pick.user.username: d.get('round_' + str(r)).get('scores').get(pick.user.username) -10})
                #if r == 4 and pick.user.pk == 1:
                #    print (d.get('round_4').get('scores').get('john'))
            #print ('pick loop dur: ', datetime.now() - pick_loop_start)

            low_score = min(d.get('round_' + str(r)).get('scores').items(), key=lambda v: v[1])[1]
            
            leaders = {k:v for k,v in d.get('round_' + str(r)).get('scores').items() if v == low_score}
            d.get('round_' + str(r)).update({'leaders': leaders})

            if r == 4:
                d['db_scores'] = {}
                for ts in TotalScore.objects.filter(tournament=self.tournament):
                    d.get('db_scores').update({ts.user.username: ts.score})
                d['bonuses'] = {}
                for bd in BonusDetails.objects.filter(tournament=self.tournament).exclude(bonus_type='5'):
                    if d.get('bonuses').get(bd.user.username):
                        d.get('bonuses').update({bd.user.username: d.get('bonuses').get(bd.user.username) + bd.bonus_points})
                    else:
                        d.get('bonuses').update({bd.user.username: bd.bonus_points})

            
            #print ('round dur: ', datetime.now() - round_start)
        results = self.validate_data(d)
        if results:
            print ("XXXXXXXXXXXXXXXXXX Validation error in round by round", results)
        #print ('dur: ', datetime.now() - start)

        return d

    def validate_data(self, d):

        results = {}

        r4 = d.get('round_4')
        db = d.get('db_scores')
        bd = d.get('bonuses')

        if (self.tournament.pk >= 184 and self.tournament.pk < 199 and len(r4) != len(db) - 1) or \
             (self.tournament.pk < 184 and self.tournament.pk >= 199 and len(r4) != len(db)):  #for Tournaments with TS but no picks for Hiro
            
            results['len_error']= {'tournament': self.tournament,
                                   'DB_data': len(db), 
                                   'calculated_data': len(r4)}

        for u, score in db.items():
            if bd.get(u):
                if db.get(u) != r4.get('scores').get(u) - bd.get(u):
                    results['calc_error' + u]= {'tournament': self.tournament,
                                                'DB_data': db, 
                                                'calculated_data': r4, 
                                                'bonus_dtl_data': bd}
            else:
                if db.get(u) != r4.get('scores').get(u):
                    results['calc_error' + u]= {'tournament': self.tournament,
                                                'DB_data': db, 
                                                'calculated_data': r4, 
                                                'bonus_dtl_data': 'no BD data'}


        return results
