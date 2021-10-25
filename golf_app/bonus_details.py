from golf_app.models import Picks, Tournament, BonusDetails, PickMethod

class BonusDtl(object):
    
    def __init__(self, espn_data, tournament=None):
    
        if tournament:
            self.tournament = tournament
        else:
            self.tournament = Tournament.objects.get(current=True)

        self.espn_data = espn_data

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
        if self.t_complete and self.espn_data.get_rank(pick.playerName.golfer.espn_number) == '1':
            print ('winner: ', pick, pick.user)
            for winner in Picks.objects.filter(playerName=pick.playerName):
                if not PickMethod.objects.filter(user=winner.user, method=3, tournament=winner.playerName.tournament).exists():
                    #bd = BonusDetails.objects.get(user=winner.user, tournament=winner.playerName.tournament)
                    if self.tournament.pga_tournament_num == '999':
                        if winner.playerName.group.number > 5:
                            group = winner.playerName.group.number - 5
                        else:
                            group = winner.playerName.group.number
                        winner_bonus =  bd.winner_bonus + 50 + (group * 2)
                        bd, created = BonusDetails.objects.get_or_create(user=winner.user, tournament=winner.playerName.tournament, bonus_type='1')
                        bd.bonus_points = winner_bonus
                       #bd.save()
            return True
        return False

    
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
 

    def weekly_winner(self):
        pass

    def no_cut(self):
        pass

    