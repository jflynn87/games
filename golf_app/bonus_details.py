from re import search
from django.db.models.expressions import F
from golf_app.models import Picks, Tournament, BonusDetails, PickMethod, Field, ScoreDetails

class BonusDtl(object):
    
    def __init__(self, espn_api=None, espn_scrape_data=None, tournament=None, inquiry=False):
        '''takes an optional espn api object or score dict and optional tournament.  source="scrape for non api data'''
        if not espn_api and not espn_scrape_data:
            raise Exception('bonus detail class requires either an espn api or score dict')

        if tournament:
            self.tournament = tournament
        else:
            self.tournament = Tournament.objects.get(current=True)

        if not espn_api and not espn_scrape_data:
            raise Exception('must provide either an espn_api object or a score_dict from scraping')

        self.espn_api = espn_api  #only used for API object
        self.espn_scrape_data= espn_scrape_data


        #self.field = espn_data.field()
        #print (type(self.field), len(self.field))

        if self.tournament.complete:
            self.t_complete = True
        elif espn_api:
            self.t_complete = self.espn_api.tournament_complete()
        elif espn_scrape_data:
            self.t_complete = self.espn_scrape_data.get('info').get('complete')
            
        
        if espn_api:
            self.t_playoff = self.espn_api.playoff()
        elif espn_scrape_data:
            self.t_playoff = self.espn_scrape_data.get('info').get('playoff')
        elif tournament.playoff:
            self.t_playoff = True
        elif tournament.complete and not tournament.playoff:
            self.t_playoff = False
        else:
            tournament.playoff
            

        self.inquiry = inquiry  #use to just check and not update DB.  default to update/save
        
    def pick_bonuses(self, pick, optimal_picks):
        big = self.best_in_group(pick, optimal_picks)
        if self.tournament.complete:
            winner = self.winner()
            playoff = self.playoff_loser()


    def other_bonuses(self, user):
        if self.tournament.complete:
            weekly_winner = self.weekly_winner()
            trifecta = self.trifecta( )


    def best_in_group(self, optimal_picks, pick):
        '''takes a dict of optimal picks (for a single group only) and a pick object, optionally updates DB, returns a bool'''
        
        big = False
        if pick.playerName.golfer.espn_number in optimal_picks.keys():
            exclude_users = PickMethod.objects.filter(tournament=self.tournament, method='3').values('user')
            for best in Picks.objects.filter(playerName__golfer__espn_number=pick.playerName.golfer.espn_number, playerName__tournament=self.tournament).exclude(user__pk__in=exclude_users):
                if self.big_eligible(best):
                    big = True
                    if not self.inquiry:
                        big_bd, created = BonusDetails.objects.get_or_create(user=best.user, tournament=self.tournament, bonus_type='5')
                        big_bd.bonus_points += 10
                        #big_bd.save()
        return big
    
    def big_eligible(self, pick):
        '''takes a pick and returns a bool'''
        #if not PickMethod.objects.filter(user=pick.user, method=3, tournament=pick.playerName.tournament).exists() \
        if not self.winner(pick) \
            and not self.playoff_loser(pick) \
            and pick.playerName.group.playerCnt > 4:
                return True
        else:
            return False
        

    def winner(self, pick):
        '''takes an api object and pick, saves the bonus details and returns a bool'''
        if not self.t_complete:  #add the api logic and fix this.
            return False
        if self.t_complete and self.espn_scrape_data:
            return bool([v for k,v in self.espn_scrape_data.items() if k != 'info' and v.get('pga_num') == pick.playerName.golfer.espn_number and v.get('rank') in [1, '1']])
            
        if self.t_complete and self.espn_api.get_rank(pick.playerName.golfer.espn_number) == '1':
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
        if not self.t_complete:
            return False
        if self.espn_scrape_data:
            if self.espn_scrape_data and self.espn_scrape_data.get('info').get('playoff'):
                return [v for k,v in self.espn_scrape_data.items() if k != 'info' and v.get('rank') in [2, '2', 'T2']]

            if self.t_complete and self.t_playoff and self.espn_api.get_rank(pick.playerName.golfer.espn_number) == '2':
                print ('playoff', pick, pick.user)
                for loser in Picks.objects.filter(playerName=pick.playerName):
                    if not PickMethod.objects.filter(user=loser.user, method=3, tournament=loser.playerName.tournament).exists():
                        bd, created = BonusDetails.objects.get_or_create(user=loser.user, tournament=loser.playerName.tournament, bonus_type='4')
                        bd.bonus_points = 25
                        #bd.save()
                return True

        #add api logic

        return False

    def trifecta(self, user):
        '''takes and bd object and user object, returns a bool'''
        if Field.objects.filter(tournament=self.tournament).count() < 71:
            return False
        elif not self.t_complete:
            return False
        
        top_3 = self.espn_api.winner()+self.espn_api.second_place()+self.espn_api.third_place()
        
        if Picks.objects.filter(user=user, playerName__tournament=self.tournament, playerName__golfer__espn_number=self.espn_api.winner()[0]).exists() and \
            Picks.objects.filter(user=user, playerName__tournament=self.tournament, playerName__golfer__espn_number__in=self.espn_api.second_place()).exists() and \
            Picks.objects.filter(user=user, playerName__tournament=self.tournament, playerName__golfer__espn_number__in=top_3).count() >= 3:
                    print ('Trifecta! : ', user)
                    bd, created = BonusDetails.objects.get_or_create(user=user, tournament=self.tournament, bonus_type='6')
                    bd.bonus_points = 50
                    #bd.save()
                    return True

        return False
                


    def no_cut(self):
        if not self.t.has_cut:
            return None
        
        # if cuts == 0 an d len([v for (k,v) in self.score_dict.items() if k != 'info' and v.get('total_score') == "CUT"]) != 0:
        #             print (player, 'no cut bonus')
        #             post_cut_wd = len([v for k,v in self.score_dict.items() if k!= 'info' and v.get('total_score') in self.tournament.not_playing_list() and \
        #                 v.get('r3') != '--'])

        #             cut_bonus = (len(self.score_dict) -1) - (len([k for k,v in self.score_dict.items() if k != 'info' and v.get('rank') not in self.tournament.not_playing_list()]) + post_cut_wd)
        #             print (cut_bonus)
        #             bd, created = BonusDetails.objects.get_or_create(tournament=self.tournament, user=user, bonus_type='2')
        #             bd.bonus_points = cut_bonus
        #             bd.save()


    