from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from wc_app.models import Event, Group, Team, Picks
from django.core import serializers
from django.http import HttpResponse
from datetime import datetime

# Create your views here.

class GroupPicksView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'wc_app/group_picks.html'


    def get_context_data(self, **kwargs):
        context = super(GroupPicksView, self).get_context_data(**kwargs)
        event = Event.objects.all().first()
        context.update({
            'event': event, 
            'teams': serializers.serialize('json', Team.objects.filter(group__event=event), use_natural_foreign_keys=True),
            'groups': Group.objects.filter(event=event),
            'picks': Picks.objects.filter(team__group__event=event, user=self.request.user)
        })

        return context

    def post(self, request, *args, **kwargs):
        print (self.request.user, request.POST)

        Picks.objects.filter(user=self.request.user, team__group__event__current=True).delete()
        for t, r in request.POST.items():
            if t != 'csrfmiddlewaretoken':
                print (t, r)
                p = Picks()
                p.user=self.request.user
                p.team=Team.objects.get(pk=t)
                p.stage='1'
                p.rank = r
                p.save()
        print ('picks usubmitted: ', self.request.user, ' ', datetime.now(), '  ', Picks.objects.filter(user=self.request.user, team__group__event__current=True))

        return HttpResponse('ok')
