from golf_app.models import Field, Tournament
from unidecode import unidecode
from golf_app import utils
from datetime import datetime

class ScoreDictCommon(object):
    '''takes a dict and tournament object, returns a dict'''
    def __init__(self, score_dict, tournament=None):
        if score_dict.get('info'):
            self.score_dict = score_dict
        else:
            self.score_dict = score_dict.update({'info': {}})

        if tournament:
            self.tournament = tournament
        else:
            self.tournament = Tournament.objects.get(current=True)

    def cut_data(self):
        print ('starting cut calc info: ', self.score_dict.get('info'))
        cut_calc_start = datetime.now()
        try:
            if self.score_dict.get('info').get('round_status') == 'Not Started' and self.score_dict.get('info').get('round') == 1 and self.tournament.has_cut:
                cut_num = self.tournament.saved_cut_num
            elif self.tournament.has_cut:
                post_cut_wd = len([v for k,v in self.score_dict.items() if k!= 'info' and v.get('total_score') in self.tournament.not_playing_list() and \
                    v.get('r3') != '--'])
                #if len([v for (k,v) in self.score_dict.items() if k != 'info' and v.get('total_score') == "CUT"]) != 0:
                if len([v for (k,v) in self.score_dict.items() if k != 'info' and v.get('rank') == "CUT"]) != 0: #changed for cbs
                    print ('cuts exists, inside if')
                    
                    #changed to rank from total score for cbs
                    cut_num = len([v for (k,v) in self.score_dict.items() if k != 'info' and v.get('rank') not in self.tournament.not_playing_list()]) \
                        + post_cut_wd +1 
                    if self.tournament.pga_tournament_num == '018':
                        cut_num = int(((cut_num-1)/2) + 1)
                    print ('caclulated cut num', cut_num)
                    if not self.score_dict.get('info').get('cut_line'):
                        #this will be the wrong number, fix at some point
                        cut_line = min(int(utils.score_as_int(v.get('total_score'))) for k, v in self.score_dict.items() if k != 'info' and v.get('rank') == "CUT") -1
                        self.score_dict['info'].update({'cut_line': 'Actual Cut Line: ' + str(utils.format_score(cut_line))})
                
                else:
                    print ('no cuts in leaderboadr, in else')
                    cut_num = min(utils.formatRank(x.get('rank')) for k, x in self.score_dict.items() if k != 'info' and int(utils.formatRank(x.get('rank'))) > self.tournament.saved_cut_num) 
                    print (cut_num)
                    if self.score_dict.get('cut_line') == None:
                        print ('in cut line none')
                        cut_line = max(int(utils.score_as_int(v.get('total_score'))) for k, v in self.score_dict.items() if k != 'info' and int(utils.formatRank(v.get('rank'))) < cut_num and \
                            v.get('total_score') not in self.tournament.not_playing_list())
                        print ('2 ', cut_line)
                        self.score_dict['info'].update({'cut_line': 'Projected Cut Line: ' + str(utils.format_score(cut_line))})
        
            else:
                cut_num = len([v for k, v in self.score_dict.items() if k != 'info' and v.get('total_score') not in self.tournament.not_playing_list()]) +1

            self.score_dict['info'].update({'cut_num': cut_num})
        
        except Exception as e:
            print ('cut nun calc issue: ', e)
            cut_num = self.tournament.saved_cut_num
            self.score_dict['info'].update({'cut_num': cut_num})
           
        
        if self.score_dict.get('info').get('cut_line') == None:
            self.score_dict['info'].update({'cut_line': 'no cut line'}) 

        print ('cut num duration: ', datetime.now() - cut_calc_start)
        print ('info: ', self.score_dict['info'])

        return self.score_dict['info']
    
    def get_field_data(self):
        pass
        #for f in Field.objects.filter(tournament=self.tournament):
        #    self.score_dict.get(unidecode(f.playerName)).update({'group': f.group.number,
        #                                                        'pga_num': f.golfer.espn_number})


