from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from wc_app.models import Event, Group, Team, Picks, Stage, AccessLog, TotalScore, Data
from django.contrib.auth.models import User
from wc_app import wc_group_data, wc_ko_data, wbc_group_standings, mlb_group_stage
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime
from rest_framework.views import APIView
from django.http import JsonResponse
from datetime import datetime
from django.db.models import Q
import json

# Create your views here.

class GroupPicksView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'wc_app/group_picks.html'


    def get_context_data(self, **kwargs):
        context = super(GroupPicksView, self).get_context_data(**kwargs)
        #event = Event.objects.all().first()
        stage = Stage.objects.get(name='Group Stage',event__current=True)
        context.update({
            #'event': event, 
            'stage': stage,
            #'teams': serializers.serialize('json', Team.objects.filter(group__stage=stage), use_natural_foreign_keys=True),
            'groups': Group.objects.filter(stage=stage),
            #'picks': serializers.serialize('json', Picks.objects.filter(team__group__stage=stage, user=self.request.user))
        })

        return context

    def post(self, request, *args, **kwargs):
        print (self.request.user, request.POST)

        stage = Stage.objects.get(event__current=True, name="Group Stage")
        if stage.started():
            return HttpResponse('Too late to make picks')
        Picks.objects.filter(user=self.request.user, team__group__stage=stage).delete()
        #Picks.objects.filter(user=self.request.user, group__stage=stage).delete()
        for t, r in request.POST.items():
            if t != 'csrfmiddlewaretoken':
                print (t, r)
                p = Picks()
                p.user=self.request.user
                p.team=Team.objects.get(pk=t)
                #p.stage= Stage.objects.get(current=True)
                p.rank = r
                p.save()
        print ('picks usubmitted: ', self.request.user, ' ', datetime.now(), '  ', Picks.objects.filter(user=self.request.user, team__group__stage__current=True))

        return HttpResponseRedirect('wc_group_picks_summary')


class GroupPicksSummaryView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'wc_app/group_picks_summary.html'

    def get_context_data(self, **kwargs):
        context = super(GroupPicksSummaryView, self).get_context_data(**kwargs)
        stage = Stage.objects.get(name="Group Stage",event__current=True)
        context.update({
            'stage': stage, 
            #'picks': serializers.serialize('json', Picks.objects.filter(team__group__event=event, user=self.request.user))
            'picks': Picks.objects.filter(team__group__stage=stage, user=self.request.user).order_by('team__group', 'rank')
        })
        
        return context


class ScoresView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'wc_app/scores.html'
    
    def dispatch(self, request, *args, **kwargs):
        print ('kwargs', kwargs)
        #start = datetime.datetime.now()

        if kwargs.get('stage'):
            self.kwargs = kwargs
        #print ('finsihed new score dispatch: ', datetime.datetime.now() - start)
        return super(ScoresView, self).dispatch(request, *args, **kwargs)

    
    def get_context_data(self, **kwargs):
        context = super(ScoresView, self).get_context_data(**kwargs)
        if self.kwargs.get('stage')  == 'group':
            stage = Stage.objects.get(name='Group Stage', event__current=True )
        elif self.kwargs.get('stage')  == 'ko':
            stage = Stage.objects.get(name='Knockout Stage', event__current=True )
        elif Stage.objects.filter(current=True).count() == 1:
            stage = Stage.objects.get(current=True)
        else:
            stage = Stage.objects.get(name='Group Stage', event__current=True )

        log, created = AccessLog.objects.get_or_create(stage=stage, user=self.request.user, screen='scores')
        log.count +=1
        log.save()
        
        users = []
        if not stage.started():
            users = stage.event.get_users()

        ko_users = {}
        for s in TotalScore.objects.filter(stage=Stage.objects.get(name='Group Stage', event__current=True)):
            ko_users[s.user.username] = {'score': s.score, 
                                    'picks': Picks.objects.filter(user=s.user, team__group__stage=stage).count()
            }
        
        
        context.update({
            'stage': stage, 
            'users': users,
            'ko_users': ko_users
            #'picks': serializers.serialize('json', Picks.objects.filter(team__group__event=event, user=self.request.user))
            #'picks': Picks.objects.filter(team__group__stage=stage, user=self.request.user).order_by('team__group', 'rank')
        })
        
        return context


class AboutView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'wc_app/about.html'


class ScoresAPI(APIView):

    def get(self, request, stage_pk):
        start = datetime.now()
        
        try:
            #stage = Stage.objects.get(event__current=True, name="Group Stage")
            stage = Stage.objects.get(pk=stage_pk)
            print ('score api stage: ', stage)
            users = stage.event.get_users()          
            data_obj, created = Data.objects.get_or_create(stage=stage)
            if stage.event.data.get('event_type') == 'wbc':
                score = wbc_scores(stage, users, data_obj)
            else:
                score = wc_scores(stage, users, data_obj)

            return JsonResponse(score, status=200, safe=False)
        except Exception as e2:
            print ("WC SCORE init API ERRor", e2)
            score = {}
            score['error'] = str(e2)
            return JsonResponse(score, status=200, safe=False)

def wbc_scores(stage, users, data_obj):
    start = datetime.now()
    d = {}
    for u in users:
        d[u.username] = {'Score': 0, 'Bonus': 0}
    #data_obj, created = Data.objects.get_or_create(stage=stage)
    if stage.pick_type == '1': #rank style
        if not stage.current:
            print ('WBC Group stage complete use saved data')
            return data_obj.display_data
            #return JsonResponse(data_obj.display_data, status=200, safe=False)
        
        #e = wbc_group_standings.ESPNData(url=stage.score_url, stage=stage)
        e = mlb_group_stage.MLBData()
        espn = e.get_team_data()
        
        if e.new_data() or data_obj.display_data in [None, '', {}]:
            print ('WBC new data, refresh scores')
        else:
            print ('no updates, use saved data')
            print ('WC scores duration: ', datetime.now() - start)
            return data_obj.display_data
            #return JsonResponse(data_obj.display_data, status=200, safe=False)
        
        for team in Team.objects.filter(group__stage=stage): 
           
            rank = [data.get('rank') for k,v in espn.items() for t, data in v.items() if t == team.full_name][0]
            print ('RANKS: ', team, rank)
            for p in Picks.objects.filter(team=team):
                if p.rank == 1 and rank == 1:
                    score = round(5 + p.team.upset_bonus(),2)
                elif p.rank in [1,2] and rank in [1,2]:
                    score = round(3 + p.team.upset_bonus(),2)
                else:
                    score = 0
                
                d.get(p.user.username).update({'Score': d.get(p.user.username).get('Score') + score})
                
                if d.get(p.user.username).get(team.group.group):
                    d.get(p.user.username).get(team.group.group).update(
                                            {team.name: 
                                            {'flag': p.team.flag_link,
                                            'rank': rank,
                                            'pick_rank': p.rank,
                                            'points': score
                                            }
                                                })
                else:
                    d.get(p.user.username).update({team.group.group: 
                            {team.name: 
                            {'flag': p.team.flag_link,
                            'rank': rank,
                            'pick_rank': p.rank,
                            'points': score
                            }
                            }})

        for g in Group.objects.filter(stage=stage):
            for u in users:
                #if g.perfect_picks(espn, u):
                if g.wbc_perfect_picks(espn, u):
                    d.get(u.username).update({'Score': round(d.get(u.username).get('Score') + 5,2)})
                    d.get(u.username).update({'Bonus': d.get(u.username).get('Bonus') + 5})
                    d.get(u.username).get(g.group).update({'bonus': 'perfect picks'})
                ts, created = TotalScore.objects.get_or_create(stage=stage, user=u)
                ts.score = d.get(u.username).get('Score')
                ts.save()
        #print ('score data: ', d)
        try: 
            data_obj.group_data = espn
            data_obj.display_data = d
            data_obj.save()
        except Exception as e1:
            print ('WC data save failed', stage, e1)


    elif stage.pick_type == '2': #braket
        #espn  = wc_ko_data.ESPNData(source='web')
        #data = espn.web_get_data()
        if stage.complete:
            d = data_obj.display_data
        else:
            espn = wc_ko_data.ESPNData(source='api')
            winners_losers = espn.api_winners_losers()
            
            for u, stats in d.items():
                score = 0
                best_score = 0
                pick_list = []
                group_ts = TotalScore.objects.get(user__username=u, stage=Stage.objects.get(event__current=True, name='Group Stage'))
                for p in Picks.objects.filter(team__group__stage=stage, user=User.objects.get(username=u)).order_by('team__group', 'rank'):
                    #if p.rank in [13, 14]:
                    #    fix = p.ko_fix_picks()
                    #    p = fix
                    p_score = p.calc_score(winners_losers, 'api')

                    pick_list.append([p.team.name, p.team.flag_link, p.rank, p_score[0], p.in_out(winners_losers)])
                    score += p_score[0]
                    best_score += p_score[1]
                d.get(u).update({'group_stage_score': group_ts.score,
                                'ko_stage_score': score,
                                'Score': group_ts.score + score,
                                'best_score': best_score + group_ts.score,
                                'picks': pick_list})

            d['results'] = winners_losers    
            if espn.stage_complete():
                stage.complete = True
                stage.save()
                max_score = max([v.get('Score') for k, v in d.items() if k != 'results'])
                print ('min score', max_score)
                winner  = [k for k, v in d.items() if k != 'results' and v.get('Score') == max_score]
                d.get('results').update({'complete': True, 'winner': winner})
        
            try: 
                data_obj.group_data = espn.api_data
                data_obj.display_data = d
                data_obj.save()
            except Exception as e1:
                    print ('WC data save failed', stage, e1)

    print ('WC scores duration: ', datetime.now() - start)
    return d



def wc_scores(stage, users, data_obj):  ## fix this, just copied during wbc
    start = datetime.now()
    d = {}
    for u in users:
        d[u.username] = {'Score': 0, 'Bonus': 0}
    data_obj, created = Data.objects.get_or_create(stage=stage)
    if stage.pick_type == '1': #rank style
        if not stage.current:
            print ('WC Group stage complete use saved data')
            return JsonResponse(data_obj.display_data, status=200, safe=False)
        
        e = wc_group_data.ESPNData(url=stage.score_url, stage=stage)
        espn = e.get_group_data()
        
        if e.new_data() or data_obj.display_data in [None, '', {}]:
            print ('new data, refresh scores')
        else:
            print ('no updates, use saved data')
            print ('WC scores duration: ', datetime.now() - start)
            return JsonResponse(data_obj.display_data, status=200, safe=False)
        
        for team in Team.objects.filter(group__stage=stage): 
            rank = [data.get('rank') for k,v in espn.items() for t, data  in v.items() if t == team.name][0]
            
            #print (team, rank)
            for p in Picks.objects.filter(team=team):
                
                if p.rank == 1 and rank == '1':
                    score = round(5 + p.team.upset_bonus(),2)
                elif p.rank in [1,2] and rank in ['1','2']:
                    score = round(3 + p.team.upset_bonus(),2)
                else:
                    score = 0
            
                d.get(p.user.username).update({'Score': d.get(p.user.username).get('Score') + score})
                if d.get(p.user.username).get(team.group.group):
                    d.get(p.user.username).get(team.group.group).update(
                                            {team.name: 
                                            {'flag': p.team.flag_link,
                                            'rank': rank,
                                            'pick_rank': p.rank,
                                            'points': score
                                            }
                                                })
                else:
                    d.get(p.user.username).update({team.group.group: 
                            {team.name: 
                            {'flag': p.team.flag_link,
                            'rank': rank,
                            'pick_rank': p.rank,
                            'points': score
                            }
                            }})
        
        for g in Group.objects.filter(stage=stage):
            for u in users:
                if g.perfect_picks(espn, u):
                    d.get(u.username).update({'Score': round(d.get(u.username).get('Score') + 5,2)})
                    d.get(u.username).update({'Bonus': d.get(u.username).get('Bonus') + 5})
                    d.get(u.username).get(g.group).update({'bonus': 'perfect picks'})
                ts, created = TotalScore.objects.get_or_create(stage=stage, user=u)
                ts.score = d.get(u.username).get('Score')
                ts.save()

        #print ('score data: ', d)
    elif stage.pick_type == '2': #braket
        #espn  = wc_ko_data.ESPNData(source='web')
        #data = espn.web_get_data()
        if stage.complete:
            d = data_obj.display_data
        else:
            espn = wc_ko_data.ESPNData(source='api')
            winners_losers = espn.api_winners_losers()
            
            for u, stats in d.items():
                score = 0
                best_score = 0
                pick_list = []
                group_ts = TotalScore.objects.get(user__username=u, stage=Stage.objects.get(event__current=True, name='Group Stage'))
                for p in Picks.objects.filter(team__group__stage=stage, user=User.objects.get(username=u)).order_by('team__group', 'rank'):
                    #if p.rank in [13, 14]:
                    #    fix = p.ko_fix_picks()
                    #    p = fix
                    p_score = p.calc_score(winners_losers, 'api')

                    pick_list.append([p.team.name, p.team.flag_link, p.rank, p_score[0], p.in_out(winners_losers)])
                    score += p_score[0]
                    best_score += p_score[1]
                d.get(u).update({'group_stage_score': group_ts.score,
                                'ko_stage_score': score,
                                'Score': group_ts.score + score,
                                'best_score': best_score + group_ts.score,
                                'picks': pick_list})

            d['results'] = winners_losers    
            if espn.stage_complete():
                stage.complete = True
                stage.save()
                max_score = max([v.get('Score') for k, v in d.items() if k != 'results'])
                print ('min score', max_score)
                winner  = [k for k, v in d.items() if k != 'results' and v.get('Score') == max_score]
                d.get('results').update({'complete': True, 'winner': winner})
        
            try: 
                data_obj.group_data = espn.api_data
                data_obj.display_data = d
                data_obj.save()
            except Exception as e1:
                print ('WC data save failed', stage, e1)

    print ('WC scores duration: ', datetime.now() - start)
    return JsonResponse(d, status=200, safe=False)


class GroupBonusAPI(APIView):

    def get(self, request, team_pk):
        start = datetime.now()
        d = {}
        team = Team.objects.get(pk=team_pk)
        d[team.pk] = team.upset_bonus()

        #for team in Team.objects.filter(group__stage__current=True):
        #    d[team.pk] = team.upset_bonus()
        
        #print ('WC GroupBonusAPI duration: ', datetime.now() - start)
        return JsonResponse(d, status=200, safe=False)


class GroupStageTeamsAPI(APIView):

    def get(self, request ):
        start = datetime.now()
        stage = Stage.objects.get(name="Group Stage", event__current=True)
        d = serializers.serialize('json', Team.objects.filter(group__stage=stage), use_natural_foreign_keys=True)
        
        #print ('WC GroupBonusAPI duration: ', datetime.now() - start)
        return JsonResponse(d, status=200, safe=False)


class GroupStagePicksAPI(APIView):

    def get(self, request):
        start = datetime.now()
        stage = Stage.objects.get(name="Group Stage", event__current=True)
        d = serializers.serialize('json', Picks.objects.filter(team__group__stage=stage, user=self.request.user))
        
        #print ('WC GroupBonusAPI duration: ', datetime.now() - start)
        return JsonResponse(d, status=200, safe=False)


class GroupStageTableAPI(APIView):

    def get(self, request):
        start = datetime.now()
        stage = Stage.objects.get(name="Group Stage", event__current=True)
        if stage.event.data.get('event_type') == 'wbc':
            d = wbc_group_standings.ESPNData().teams_by_pool()

            d['headers'] = ['Wins', 'Loss', 'PCT', 'GB', 'RS', 'RA']
            d['type'] = 'WBC'
        else:
            d = wc_group_data.ESPNData().get_group_records()
        
        print ('WC GroupStageTableAPI duration: ', datetime.now() - start)
        return JsonResponse(d, status=200, safe=False)


class KnockoutPicksView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    #template_name = 'wc_app/knockout_picks.html'

    def stage(self):
        return Stage.objects.get(name='Knockout Stage', event__current=True)
    
    def get_template_names(self):
        #t_name = super().get_template_names()
        if self.stage().event.data.get('event_type') == 'wbc':
            return ['wc_app/wbc_ko_picks.html',]
        else:
            return ['wc_app/knockout_picks.html',]

    def get_context_data(self, **kwargs):
        context = super(KnockoutPicksView, self).get_context_data(**kwargs)
        stage = Stage.objects.get(name='Knockout Stage', event__current=True)
        log, created = AccessLog.objects.get_or_create(stage=stage, user=self.request.user, screen='ko_picks')
        log.count +=1
        log.save()

        if kwargs:
            u = User.objects.get(username=kwargs.get('user'))
        else:
            u = self.request.user

        context.update({
            'stage': stage,
            'groups': Group.objects.filter(stage=stage),
            'picks_user': u
        })

        return context

    def post(self, request, *args, **kwargs):
        print (self.request.user, request.POST)

        stage = Stage.objects.get(event__current=True, name="Knockout Stage")
        picks_valid = validate_ko_picks(self.request.user, stage, request.POST)
        #add if to check and error processing
        Picks.objects.filter(user=self.request.user, team__group__stage=stage).delete()
        #Picks.objects.filter(user=self.request.user, team__group__stage__name="Knockout Stage", team__group__stage__event__current=True).delete()
        for game, team in request.POST.items():
            if game != 'csrfmiddlewaretoken': 
               print (game, Team.objects.get(pk=team))
               p = Picks()
               p.user=self.request.user
               p.team=Team.objects.get(pk=team)
               p.group= Group.objects.get(group='Final 16')
               p.rank = game.split('_')[0][1:]
               p.data = {'from_ele': game[0:]}
               p.save()
        print ('picks submitted: ', self.request.user, ' ', datetime.now(), '  ', Picks.objects.filter(user=self.request.user, team__group__stage=stage))

        return HttpResponseRedirect('wc_ko_picks_summary')
        


class KOBracketAPI(APIView):

    def get(self, request, username=None):
        start = datetime.now()
        d = {}
        stage = Stage.objects.get(name='Knockout Stage', event__current=True)
        #games = []
        if stage.event.data.get('event_type') == 'wbc':
            if stage.early_picks_period:
                order = [1, 4]
            else:
                order = [1, 4, 3, 2, 5, 8, 7, 6]
            m = 1
            data_obj = Data.objects.get(stage__event__current=True, stage__name='Group Stage')
            
            for i, o in enumerate(order):
                if i % 2 == 0:
                    if i == 0:
                        match = 'match_1'
                    else:
                        match = 'match_' + str(m)

                    #print ('MATCH ', match, m, order[i], stage)
                    fav = Team.objects.get(group__stage=stage, rank=order[i])
                    dog = Team.objects.get(group__stage=stage, rank=order[i+1])

                    fav_data = Team.objects.get(full_name=fav.name, group__stage__name="Group Stage", group__stage__event__current=True)
                    dog_data = Team.objects.get(full_name=dog.name, group__stage__name="Group Stage", group__stage__event__current=True)
                    #print ('XXCCX ', data_obj.group_data.get(fav.group.group), fav.group.group)
                    d[match] = {'fav': fav.name, 
                                'fav_pk': fav.pk, 
                                'fav_flag': fav_data.flag_link,
                                'fav_fifa_rank': data_obj.group_data.get(fav_data.group.group).get(fav_data.full_name).get('rank'),
                                'dog': dog.name,
                                'dog_pk': dog.pk, 
                                'dog_flag': dog_data.flag_link,
                                'dog_fifa_rank': data_obj.group_data.get(dog_data.group.group).get(dog_data.full_name).get('rank'),
                                'early_game': fav.early_game            
                                }
                    
                    m +=1
                
        else:    
            order = [1,10, 3, 12, 5, 14, 7, 16, 2, 9, 4, 11, 6, 13, 8, 15]
            m = 1
            for i, team in enumerate(order):
                if i % 2 == 0:
                    fav = Team.objects.get(group__stage=stage, rank=order[i])
                    dog = Team.objects.get(group__stage=stage, rank=order[i+1])
                    #games.append([fav.name, dog.name])
                    if i == 0:
                        match = 'match_1' 
                    else:
                        match = 'match_' + str(m)
                    m += 1
                    fav_data = Team.objects.get(name=fav.name, group__stage__name="Group Stage", group__stage__event__current=True)
                    dog_data = Team.objects.get(name=dog.name, group__stage__name="Group Stage", group__stage__event__current=True)

                    d[match] = {'fav': fav.name, 
                                'fav_pk': fav.pk, 
                                'fav_flag': fav_data.flag_link,
                                'fav_fifa_rank': fav_data.rank,
                                'dog': dog.name,
                                'dog_pk': dog.pk, 
                                'dog_flag': dog_data.flag_link,
                                'dog_fifa_rank': dog_data.rank,
                    
                                }

        print ('picks user ', username)
        if username:
            pick_user = User.objects.get(username=username)
        else:
            pick_user = self.request.user

        if Picks.objects.filter(user=pick_user, team__group__stage=stage).exists():
            d['picks'] = serializers.serialize('json', Picks.objects.filter(user=pick_user, team__group__stage=stage).order_by('rank'))
        else:
            d['picks'] = json.dumps([])

        print ('WC KOBracketAPI duration: ', datetime.now() - start)
        return JsonResponse(d, status=200, safe=False)


class KOPicksSummaryView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'wc_app/ko_picks_summary.html'

    def get_context_data(self, **kwargs):
        context = super(KOPicksSummaryView, self).get_context_data(**kwargs)
        stage = Stage.objects.get(event__current=True, name="Knockout Stage")
        context.update({
            'stage': stage, 
            #'picks': serializers.serialize('json', Picks.objects.filter(team__group__event=event, user=self.request.user))
            'picks': Picks.objects.filter(team__group__stage=stage, user=self.request.user).order_by('team__group', 'rank')
        })
        
        return context

def validate_ko_picks(user, stage, picks):
    '''takes a user obj and a dict of picks returns a tuple with a bool and a string'''
    if stage.started():
        return (False, 'Stage started too late for picks')
    
    order = stage.ko_match_order()


class CreateKOTeamsAPI(APIView):

    def get(self, request):
        start = datetime.now()
        d = {}

        try:
            group = Group.objects.get(stage__event__current=True, group__in=['Final 16', 'Final 8'])
            stage = group.stage
            
            
            if  Picks.objects.filter(team__group__stage__event__current=True, team__group=group).exclude(team__early_game=True).exists():
                print ('CReate KO Team - too late picks already exist')
                d['error'] = 'too late picks already exist'
                return JsonResponse(d, status=200)
            elif Picks.objects.filter(team__group__stage__event__current=True, team__group=group, team__early_game=True).exists():
                Team.objects.filter(group=group).exclude(early_game=True).delete()
            else:
                Team.objects.filter(group=group).delete()

            data_obj = Data.objects.get(stage__event__current=True, stage__name='Group Stage')
            
            ko_group = Group.objects.get(stage=stage)

            pools = ['Pool A', 'Pool B', 'Pool C', 'Pool D']
            for g in Group.objects.filter(stage=Stage.objects.get(current=True, name="Group Stage")):
                #rank = [data.get('rank') for k,v in espn.items() for t, data  in v.items() if t == team.name][0]
                print (data_obj.group_data)
                d = [(t,data.get('rank')) for k,v in data_obj.group_data.items() for t, data in v.items() if data.get('rank') in ['1', '2', 1, 2] and k == g.group ]
                
                #print (g.group[-1].lower(),ord(g.group[-1].lower()) -96, d)
                print ('DD ', d)
                if stage.event.data.get('event_type') == 'wbc':
                    
                    for i, x in enumerate(d):
                        if Team.objects.filter(full_name=x[0], group__stage=stage, group__stage__event__current=True ).exists():
                            print ('Skipping setup game exists: ', stage, x[0])
                        else:
                            t_data = Team.objects.get(full_name=x[0], group__stage__name="Group Stage", group__stage__event__current=True)
                            team = Team()
                            team.group = ko_group
                            team.name = x[0]
                            team.full_name = x[0]
                            team.rank = (pools.index(t_data.group.group) * 2) + x[1]
                            team.flag_link = t_data.flag_link
                            if stage.event.data.get('early_ko_games'):
                                pool = [x for x in stage.event.data.get('early_ko_games') if x.split('_')[0] == t_data.group.group]
                                print ('Early Game POOL ', pool)
                            if pool and int(pool[0].split('_')[1]) == int(x[1]):
                                team.early_game=True
                            team.save()
                else:
                    for x in d:
                        if int(x[1]) == 1:
                            rank = ord(g.group[-1].lower()) -96
                        else:
                            rank = (ord(g.group[-1].lower()) -96) + 8
                        t_data = Team.objects.get(name=x[0], group__stage__name="Group Stage", group__stage__event__current=True)
                        team = Team()
                        team.group = ko_group
                        team.name = x[0]
                        team.rank = rank
                        team.flag_link = t_data.flag_link

                        team.save()

                        print (g, x[0], rank)
                        
        except Exception as e:
            print ('CreateKOTeamsAPI error: ', e)
            d['error'] = {str(e)}

        print ('CreateKOTeamsAPI duration: ', d, datetime.now() - start)
        return JsonResponse(d, status=200, safe=False)






