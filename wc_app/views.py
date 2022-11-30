from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from wc_app.models import Event, Group, Team, Picks, Stage, AccessLog, TotalScore, Data
from django.contrib.auth.models import User
from wc_app import wc_group_data
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
        #Picks.objects.filter(user=self.request.user, team__group__stage__current=True).delete()
        Picks.objects.filter(user=self.request.user, stage=stage).delete()
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

    def get(self, request):
        start = datetime.now()
        d = {}
        try:
            stage = Stage.objects.get(event__current=True, name="Group Stage")
            e = wc_group_data.ESPNData(url=stage.score_url, stage=stage)
            espn = e.get_group_data()
            data_obj, created = Data.objects.get_or_create(stage=stage)
            if e.new_data() or data_obj.display_data in [None, '', {}]:
                print ('new data, refresh scores')
            else:
                print ('no updates, use saved data')
                print ('WC scores duration: ', datetime.now() - start)
                return JsonResponse(data_obj.display_data, status=200, safe=False)
          
            
            if stage.pick_type == '1': #rank style
                users = stage.event.get_users()
                for u in users:
                    d[u.username] = {'Score': 0, 'Bonus': 0}
                    
                for team in Team.objects.filter(group__stage__current=True): 
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
                                                    'team_rank': rank,
                                                    'pick_rank': p.rank,
                                                    'points': score
                                                    }
                                                        })
                        else:
                            d.get(p.user.username).update({team.group.group: 
                                    {team.name: 
                                    {'flag': p.team.flag_link,
                                    'team_rank': rank,
                                    'pick_rank': p.rank,
                                    'points': score
                                    }
                                    }})
                
                for g in Group.objects.filter(stage__current=True):
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
                print ('bracket stage')
                d = {}    

            #data = serializers.serialize('json', Picks.objects.filter(team__group__stage__current=True, user=self.request.user))
            
            data_obj.group_data = espn
            data_obj.display_data = d
            data_obj.save()

            print ('WC scores duration: ', datetime.now() - start)
            return JsonResponse(d, status=200, safe=False)
        except Exception as e:
            print ("WC SCORE API ERRor", e)
            d['error'] = str(e)
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
        d = serializers.serialize('json', Team.objects.filter(group__stage=stage), use_natural_foreign_keys=True),
        
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
        d = wc_group_data.ESPNData().get_group_records()
        
        print ('WC GroupStageTableAPI duration: ', datetime.now() - start)
        return JsonResponse(d, status=200, safe=False)


class KnockoutPicksView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'wc_app/knockout_picks.html'


    def get_context_data(self, **kwargs):
        context = super(KnockoutPicksView, self).get_context_data(**kwargs)
        stage = Stage.objects.get(name='Knockout Stage', event__current=True)
        log, created = AccessLog.objects.get_or_create(stage=stage, user=self.request.user, screen='ko_picks')
        log.count +=1
        log.save()


        context.update({
            'stage': stage,
            'groups': Group.objects.filter(stage=stage),
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

    def get(self, request):
        start = datetime.now()
        d = {}
        stage = Stage.objects.get(name='Knockout Stage', event__current=True)
        #games = []
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
                fav_data = Team.objects.get(name=fav.name, group__stage__name="Group Stage")
                dog_data = Team.objects.get(name=dog.name, group__stage__name="Group Stage")

                d[match] = {'fav': fav.name, 
                            'fav_pk': fav.pk, 
                            'fav_flag': fav_data.flag_link,
                            'fav_fifa_rank': fav_data.rank,
                            'dog': dog.name,
                            'dog_pk': dog.pk, 
                            'dog_flag': dog_data.flag_link,
                            'dog_fifa_rank': dog_data.rank,
                
                            }
        if Picks.objects.filter(user=self.request.user, team__group__stage=stage).exists():
            d['picks'] = serializers.serialize('json', Picks.objects.filter(user=self.request.user, team__group__stage=stage).order_by('rank'))
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
            Team.objects.filter(group__group='Final 16').delete()
            stage = Stage.objects.get(name="Group Stage")
            e  = Data.objects.get(stage=stage)
            print (e.group_data.keys())
            ko_group = Group.objects.get(group="Final 16")

            for g in Group.objects.filter(stage=stage):
                #rank = [data.get('rank') for k,v in espn.items() for t, data  in v.items() if t == team.name][0]
                d = [(t,data.get('rank')) for k,v in e.group_data.items() for t, data in v.items() if data.get('rank') in ['1', '2'] and k == g.group ]
                #print (g.group[-1].lower(),ord(g.group[-1].lower()) -96, d)
                for x in d:
                    if int(x[1]) == 1:
                        rank = ord(g.group[-1].lower()) -96
                    else:
                        rank = (ord(g.group[-1].lower()) -96) + 8
                    t_data = Team.objects.get(name=x[0], group__stage__name="Group Stage")
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






