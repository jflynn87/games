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
        stage = Stage.objects.get(current=True)
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

        Picks.objects.filter(user=self.request.user, team__group__stage__current=True).delete()
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
        stage = Stage.objects.get(current=True)
        context.update({
            'stage': stage, 
            #'picks': serializers.serialize('json', Picks.objects.filter(team__group__event=event, user=self.request.user))
            'picks': Picks.objects.filter(team__group__stage=stage, user=self.request.user).order_by('team__group', 'rank')
        })
        
        return context


class ScoresView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'wc_app/scores.html'

    def get_context_data(self, **kwargs):
        context = super(ScoresView, self).get_context_data(**kwargs)
        stage = Stage.objects.get(current=True)
        log, created = AccessLog.objects.get_or_create(stage=stage, user=self.request.user, screen='scores')
        log.count +=1
        log.save()
        
        users = []
        if not stage.started():
            users = stage.event.get_users()
        context.update({
            'stage': stage, 
            'users': users
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
        try:
            stage = Stage.objects.get(current=True)
            e = wc_group_data.ESPNData(url=stage.score_url)
            espn = e.get_group_data()

            if e.new_data():
                print ('new data, refresh scores')
            else:
                print ('no updates, use saved data')
                d = Data.objects.get(stage=stage)
                print ('WC scores duration: ', datetime.now() - start)
                return JsonResponse(d.display_data, status=200, safe=False)
            d = {}
            
            
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
            data_obj, created = Data.objects.get_or_create(stage=stage)
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
        stage = Stage.objects.get(current=True)
        d = serializers.serialize('json', Team.objects.filter(group__stage=stage), use_natural_foreign_keys=True),
        
        #print ('WC GroupBonusAPI duration: ', datetime.now() - start)
        return JsonResponse(d, status=200, safe=False)


class GroupStagePicksAPI(APIView):

    def get(self, request):
        start = datetime.now()
        stage = Stage.objects.get(current=True)
        d = serializers.serialize('json', Picks.objects.filter(team__group__stage=stage, user=self.request.user))
        
        #print ('WC GroupBonusAPI duration: ', datetime.now() - start)
        return JsonResponse(d, status=200, safe=False)

class KnockoutPicksView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'wc_app/knockout_picks.html'


    def get_context_data(self, **kwargs):
        context = super(KnockoutPicksView, self).get_context_data(**kwargs)
        #event = Event.objects.all().first()
        stage = Stage.objects.get(name='Knockout Stage', event__current=True)
        games = []
        order = [1,10, 3, 12, 5, 14, 7, 16, 2, 9, 4, 11, 6, 13, 8, 15]

        #for t in Team.objects.filter(group__stage=stage).order_by('rank')[0:8]:
        for i, team in enumerate(order):
            print (i)
            if i % 2 == 0:
                fav = Team.objects.get(group__stage=stage, rank=order[i])
                opponent = Team.objects.get(group__stage=stage, rank=order[i+1])
                games.append([fav.name, opponent.name])

        print (games)

        context.update({
            #'event': event, 
            'stage': stage,
            'games': json.dumps(games),
            #'teams': serializers.serialize('json', Team.objects.filter(group__stage=stage), use_natural_foreign_keys=True),
            'groups': Group.objects.filter(stage=stage),
            #'picks': serializers.serialize('json', Picks.objects.filter(team__group__stage=stage, user=self.request.user))
        })

        return context

    def post(self, request, *args, **kwargs):
        print (self.request.user, request.POST)

        Picks.objects.filter(user=self.request.user, team__group__stage__current=True).delete()
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

