from django.db.models.expressions import F
from golf_app.models import Picks, Tournament, BonusDetails, PickMethod

class BonusDtl(object):
    
    def __init__(self, espn_data, tournament=None):
    
        if tournament:
            self.tournament = tournament
        else:
            self.tournament = Tournament.objects.get(current=True)

        self.espn_data = espn_data
        #self.field = espn_data.field()
        #print (type(self.field), len(self.field))

        self.t_complete = self.espn_data.tournament_complete()
        self.t_playoff = self.espn_data.playoff()
        
    
    def best_in_group(self, optimal_picks, pick):
        '''takes a dict of optimal picks and a pick object, updates DB, returns a bool'''
        big = False
        if pick.playerName.golfer.espn_number in optimal_picks.keys():
            for best in Picks.objects.filter(playerName__golfer__espn_number=pick.playerName.golfer.espn_number, playerName__tournament=self.tournament):
                if not PickMethod.objects.filter(user=best.user, method=3, tournament=best.playerName.tournament).exists() \
                    and not self.winner(best) \
                    and not self.playoff_loser(best) \
                    and best.playerName.group.playerCnt > 4:
                        big = True
                        big_bd, created = BonusDetails.objects.get_or_create(user=best.user, tournament=self.tournament, bonus_type='5')
                        big_bd.bonus_points += 10
                        
                        #big_bd.save()
        return big
    
    def winner(self, pick):
        '''takes an api object and pick, saves the bonus details and returns a bool'''
        if self.t_complete and self.espn_data.get_rank(pick.playerName.golfer.espn_number) == '1':
            print ('winner: ', pick, pick.user)
            for winner in Picks.objects.filter(playerName=pick.playerName):
                if not PickMethod.objects.filter(user=winner.user, method=3, tournament=winner.playerName.tournament).exists():
                    if self.tournament.pga_tournament_num == '999':
                        if winner.playerName.group.number > 5:
                            group = winner.playerName.group.number - 5
                        else:
                            group = winner.playerName.group.number
                #winner_bonus =  50 + (group * 2)
                bd, created = BonusDetails.objects.get_or_create(user=winner.user, tournament=winner.playerName.tournament, bonus_type='1')
                bd.bonus_points = self.winner_points(pick)
                #bd.save()
            return True
        else: 
            return False


    def winner_points(self, pick):
        return  50 + (pick.playerName.group.number * 2)
        

    def weekly_winner(self, scores):
        '''takes an api object and score dict, returns a list of winners or None'''
        print ('XXXXXXXXXXXXXXXweekly winner ', self.t_complete)
        if self.t_complete:
            winning_score = min(v.get('score') for k,v in scores.items())
            print ('winning socre: ', winning_score)
            weekly_winner = [k for k,v in scores.items() if v.get('score') == winning_score]
            print ('weekly winner', winning_score, weekly_winner)
            return weekly_winner
        else:
            return None


    def weekly_winner_points(self):
        points = 0 
        field_type = self.tournament.field_quality()
        if field_type == 'weak':
            points = 50 / self.tournament.num_of_winners()
        elif field_type == 'strong':
            points = 100 / self.tournament.num_of_winners()
        elif field_type == 'major':
            points = 150 / self.tournament.num_of_winners()

        return points


    
    def playoff_loser(self, pick):
        if self.t_complete and self.t_playoff and self.espn_data.get_rank(pick.playerName.golfer.espn_number) == '2':
            print ('playoff', pick, pick.user)
            for loser in Picks.objects.filter(playerName=pick.playerName):
                if not PickMethod.objects.filter(user=loser.user, method=3, tournament=loser.playerName.tournament).exists():
                    bd, created = BonusDetails.objects.get_or_create(user=loser.user, tournament=loser.playerName.tournament, bonus_type='4')
                    bd.bonus_points = 25
                    #bd.save()
            return True
        return False

    def trifecta(self):
        pass
 

    def no_cut(self):
        pass

    