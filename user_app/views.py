from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, TemplateView, ListView, DetailView, CreateView, UpdateView, FormView
from user_app import espn_baseball
from golf_app.models import Tournament, Season  
from fb_app.models import Week, Games, PlayoffPicks 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
#from django.contrib.auth.mixins import LoginRequiredMixin
#from django.views.generic.base import TemplateResponseMixin
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
#from django.contrib.auth.forms import UserCreationForm
from user_app.forms import UserCreateForm
from golf_app import utils
#from django.db.models import Q, Max

from django.http import JsonResponse
import json
import random
from django.db import transaction
import urllib.request
import csv
from rest_framework.views import APIView 



class SignUp(CreateView):
    #form_class = UserCreationForm
    form_class = UserCreateForm
    success_url = reverse_lazy('login')
    template_name = 'user_app/signup.html'


def index(request):

        if request.user.is_authenticated:
            utils.save_access_log(request, 'home page')

        
        try:
            week = Week.objects.get(current=True)        
            if Games.objects.filter(week=week, playoff_picks=True).exists():
                game = Games.objects.get(week=week, playoff_picks=True)
            else:
                game = None
        except Exception as e:
            game = None
            #week = Week.objects.filter(season_model__current=True).last()
            week = Week.objects.latest('pk')
            print ('week', week)
    
        try:
            if PlayoffPicks.objects.filter(player__name=request.user, game=game).exists():
                picks = PlayoffPicks.objects.get(player__name=request.user, game=game)
            else:
                picks = None
        except Exception as e:
            picks = None

        try:
            t = Tournament.objects.get(current=True)
        except Exception as e:
            t = None

        #sb_user_list = ['john', 'jcarl62', 'BigDipper', 'shishmeister', 'JoeLong', 'Laroqm']
        sb_user_list = ['john', 'jcarl62']
        golf_auction_user_list = ['john', 'jcarl62', 'ryosuke']
        print ('game', game)
        print ('picks', picks)
        return render(request, 'index.html', {
            'fb_week': week,
            #'sb_user_list': User.objects.filter(username__in=['john', 'jcarl62']),
            'game': game,
            'picks': picks,
            'sb_user_list': sb_user_list,
            'golf_auction_user_list': golf_auction_user_list,
            't': t,

                })


@login_required
def special(request):
    return HttpResponse("You are logged in!")


class GetBaseballScore(APIView):

    def get(self, request):
        
        try:
            d = espn_baseball.ESPNData().get_score(['21'])
        except Exception as e:
            print ('Baseball score API Error: ', e)
            d['error'] = {'msg': str(e)}
        
        return JsonResponse(d, status=200, safe=False)
