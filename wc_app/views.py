from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from wc_app.models import Event, Group, Team, Picks, Stage
from wc_app import wc_group_data
from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect
from datetime import datetime
from rest_framework.views import APIView
from django.http import JsonResponse
from datetime import datetime

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
        score = 0
        for p in Picks.objects.filter(team__group__stage__current=True):
            rank = [d.get('rank') for k,v in espn.items() for team,d  in v.items() if team == p.team.name][0]
            
            print (p, p.rank, rank)
            if p.rank in [1,2] and rank in ['1','2']:
                score +=3 

            d[p.user.username] = {'group': p.team.group.group,
                                  'team': p.team.name, 
                                  'pick_rank': p.rank,
                                  'rank': rank,         
                                }
        d[p.user.username].update({'score': score})
        data = serializers.serialize('json', Picks.objects.filter(team__group__stage__current=True, user=self.request.user))
        print ('WC scores duration: ', datetime.now() - start)
        return JsonResponse(d, status=200, safe=False)