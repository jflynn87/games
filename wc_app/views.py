from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from wc_app.models import Event, Group, Team, Picks, Stage
from django.contrib.auth.models import User
from wc_app import wc_group_data
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime
from rest_framework.views import APIView
from django.http import JsonResponse
from datetime import datetime
from django.db.models import Q

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
            'teams': serializers.serialize('json', Team.objects.filter(group__stage=stage), use_natural_foreign_keys=True),
            'groups': Group.objects.filter(stage=stage),
            'picks': serializers.serialize('json', Picks.objects.filter(team__group__stage=stage, user=self.request.user))
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
        context.update({
            'stage': stage, 
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
        espn = wc_group_data.ESPNData().get_group_data()
        d = {}
        
        #users = Picks.objects.filter(team__group__stage__current=True).values('user').distinct()
        stage = Stage.objects.get(current=True)
        users = stage.event.get_users()
        for u in users:
            #print (u)
            #user= User.objects.get(pk=u.get('user'))
            d[u.username] = {'score': 0}
            
        for team in Team.objects.filter(group__stage__current=True): 
            rank = [data.get('rank') for k,v in espn.items() for t, data  in v.items() if t == team.name][0]
             
            print (team, rank)
            for p in Picks.objects.filter(team=team):
                if p.rank == 1 and rank == '1':
                    score = 5
                elif p.rank in [1,2] and rank in ['1','2']:
                    score = 3
                else:
                    score = 0
            
                d.get(p.user.username).update({'score': d.get(p.user.username).get('score') + score})
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
                    d.get(u.username).update({'score': d.get(u.username).get('score') + 5})
                    d.get(u.username).get(g.group).update({'bonus': 'perfect picks'})
            
        
        data = serializers.serialize('json', Picks.objects.filter(team__group__stage__current=True, user=self.request.user))
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