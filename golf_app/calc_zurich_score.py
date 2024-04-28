from datetime import datetime
import urllib
from bs4 import BeautifulSoup
from golf_app.models import Field, Picks, Group, ScoreDetails, PickMethod, BonusDetails, TotalScore
from django.db.models import Sum
from django.contrib.auth.models import User

class CalcZurichScore(object):
    def __init__(self, t, d, data=None):
        print ('CALC ZURICH SCORE INIT')
        self.t = t
        self.d = d
        
        if data:
            self.data = data
        else:
            self.data = self.get_espn_score_data()


    def calc_score(self):
        '''takes a tornament object and dict, updates and returns the dict'''
        start = datetime.now()
        score_data = self.get_espn_score_data()

        s = self.pick_calc_score(score_data)
        print (s)

        return (s)

    def get_espn_score_data(self):
        url = f'https://www.espn.com/golf/leaderboard'
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:82.0) Gecko/20100101 Firefox/82.0'}
        req = urllib.request.Request(url, headers=headers)
        html = urllib.request.urlopen(req)
        print ('OPEN WORKS')
        soup = BeautifulSoup(html, 'html.parser')
        print ('SOUP WORKS')
        print ('SOUP ', len(soup.find_all('div', {'class': 'Wrapper'})[0]))
        golfers = []
        for data in soup.find_all('div', {'class': 'Wrapper'})[1]:
            print ('DATa WORKS', data)
            for i, line in enumerate([x for x in data.text.split('\n') if x != '']):
                if 'Round' in line:
                    self.current_round = line.strip('<pre>')
                elif i < 5:
                    continue
                else:
                    rank = line.split('.',1)[0].strip()
                    golfer = line.split('.', 1)[1].lstrip().split('/')[0]
                    if '.' in golfer and 'Jr.' not in golfer: golfer = golfer.split('.')[1]
                    if 'Jr' in golfer: golfer = golfer.split(' ')[0]
                    if golfer == 'Lahsley': golfer = 'Lashley'
                    if 'Jr.' in line.split('.', 1)[1].lstrip().split('/')[1] or 'de' in line.split('.', 1)[1].lstrip().split('/')[1]:
                        partner = ''.join(x for x in line.split('.', 1)[1].lstrip().split('/')[1].split(' ')[0]).rstrip()
                    else:
                        partner = line.split('.', 1)[1].lstrip().split('/')[1].split(' ')[0].rstrip()
                        partner = partner.split('.')[-1] if '.' in partner else partner
                    if '-' in line:
                        
                        score = '-' + str(line.split('-')[1][:2].rstrip())
                    elif '+' in line:
                        score = '+' + str(line.split('+')[1][:2].rstrip())
                    else:
                        score = 'E'
                    thru = line[-16:].strip()
                    golfers.append({'rank': rank, 'golfer': golfer, 'partner': partner, 'score': score, 'thru': thru})
                
                #print ('Rank: {}, Team: {}, {}, score: {}, {}'.format(rank, golfer, partner, score, thru))
        for f in Field.objects.filter(tournament=self.t):
            if len([x for x in golfers if x.get('golfer') in f.playerName.split(' ')[1] and x.get('partner') in f.partner_golfer.golfer_name]) == 1:
                update = [x.update({'espn_number': f.golfer.espn_number, 'lookup': 'golferboth', 'group': f.group.number}) for x in golfers if x.get('golfer') in f.playerName.split(' ')[1] and x.get('partner') in f.partner_golfer.golfer_name] 
                #print ('BOTh', f.playerName, f.golfer.golfer_name, f.golfer.espn_number, f.partner_golfer.golfer_name, f.partner_golfer.espn_number, f.group.number)
            elif len([x for x in golfers if x.get('partner') in f.playerName.split(' ')[1] and x.get('golfer') in f.partner_golfer.golfer_name]) == 1:
                update = [x.update({'espn_number': f.golfer.espn_number, 'lookup': 'partner', 'group': f.group.number}) for x in golfers if x.get('partner') in f.playerName.split(' ')[1] and x.get('golfer') in f.partner_golfer.golfer_name] 
                #print ('BOTh Parner', f.playerName, f.golfer.golfer_name, f.golfer.espn_number, f.partner_golfer.golfer_name, f.partner_golfer.espn_number, f.group.number)
            elif len([x for x in golfers if x.get('golfer') in f.playerName.split(' ')[1]]) == 1:
                update = [x.update({'espn_number': f.golfer.espn_number, 'lookup': 'golfer', 'group': f.group.number}) for x in golfers if x.get('golfer') in f.playerName.split(' ')[1]]
            else:
                print ('check ', f.playerName)
        for g in golfers: print(g)
        return golfers

    def best_in_group(self, data=None):
        if not data:
            data=self.data

        d = {}
        for group in Group.objects.filter(tournament=self.t):   
            best = min([int(x.get('rank')) for x in data if int(x.get('group')) == int(group.number) and x.get('rank') != 'CUT'])
            big = [x for x in data if x.get('rank') != 'CUT' and int(x.get('group')) == int(group.number) and int(x.get('rank')) == int(best)]
            cuts = len([x for x in data if x.get('rank') == 'CUT' and int(x.get('group')) == int(group.number)])
            print ('Group: {}, Best: {}, big: {}'.format(group, best, big))
            golfer_names = [f.playerName for f in Field.objects.filter(tournament=self.t, group=group, golfer__espn_number__in=[x.get('espn_number') for x in big])]
            d[str(group.number)] = {'golfers': golfer_names,
                                'golfer_espn_nums': [x.get('espn_number') for x in big],
                                'cuts': cuts,
                                'total_golfers': group.playerCnt

                       }
            
        return d

    def pick_calc_score(self, data=None):
        if not data:
            self.data = data
        big = self.best_in_group()
        g_list = Picks.objects.filter(playerName__tournament=self.t).values_list('playerName__pk', flat=True)
        golfers = [*set(g_list)]

        for golfer in golfers:
            print (golfer)
            f_obj = Field.objects.get(pk=golfer)
            g_data = [x for x in data if x.get('espn_number') == f_obj.golfer.espn_number][0]
            p = Picks.objects.filter(playerName__pk=golfer).first()
            score = p.playerName.calc_score(api_data=data)
            
            picks = Picks.objects.filter(playerName__pk=golfer, playerName__tournament=self.t).update(score=score.get('score'))
            gross_score = g_data.get('rank') if g_data.get('rank') != 'CUT' else int(self.t.cut_score) + self.cut_penalty(f_obj.group.number, big)
            thru = 'CUT' if  g_data.get('rank') == 'CUT' else g_data.get('thru')
            sd = ScoreDetails.objects.filter(pick__playerName=p.playerName, pick__playerName__tournament=self.t).update(score=gross_score,
                                                                                                                 thru=thru, toPar=g_data.get('score'),
                                                                                                                 gross_score=gross_score)

            print (p.playerName, score.get('score'))
        score_d = {}
        for u in self.d:
            user = User.objects.get(pk=u.get('user'))
            player_score = Picks.objects.filter(playerName__tournament=self.t, user=user).aggregate(Sum('score'))
            c = 0
            if not PickMethod.objects.filter(tournament=self.t, user=user, method='3').exists():
                for p in Picks.objects.filter(playerName__tournament=self.t, user=user):
                    if [v for k,v in big.items() if str(k) == str(p.playerName.group.number) and p.playerName.golfer.espn_number in v.get('golfer_espn_nums')]:
                        player_score.update({'score__sum': player_score.get('score__sum') - 10})
                        c += 1
            cuts = Picks.objects.filter(playerName__tournament=self.t, user=user, score=self.t.cut_score).count()
            ts, ts_created = TotalScore.objects.get_or_create(tournament=self.t, user=user)
            ts.score=player_score.get('score__sum')
            ts.save()
            bd, created = BonusDetails.objects.get_or_create(tournament=self.t, user=user, bonus_type='5')
            bd.bonus_points = c * 10
            bd.save()
            score_d[user.username] = {'score': player_score.get('score__sum'),
                                      'cuts': cuts}
        score_d.update({'group_stats': big})
        print (score_d)
        return score_d



    def cut_penalty(self, group, big):
        if group in [1,2,3]:
            big_group = big.get(str(group))
            print ('BIG GROUP: ', big_group)
            return 10 - int(big_group.get('cuts'))
        else:
            return 0

    def leaders(self, data=None):
        if not data:
            data=self.data  
        return [x.get('golfer') for x in data if x.get('rank') != 'CUT' and int(x.get('rank')) == 1]
    
    def leader_score(self, data=None):
        if not data:
            data=self.data
        return [x.get('score') for x in data if x.get('rank') != 'CUT' and int(x.get('rank')) == 1]
    
    def current_round(self, data=None):
        if not data:
            data=self.data
        return self.data[0]
        


