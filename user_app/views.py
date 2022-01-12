from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, TemplateView, ListView, DetailView, CreateView, UpdateView, FormView
from golf_app.models import Tournament, Season  
from fb_app.models import Week, Games, PlayoffPicks 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateResponseMixin
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from user_app.forms import UserCreateForm
from golf_app import utils
from django.db.models import Q, Max


class SignUp(CreateView):
    #form_class = UserCreationForm
    form_class = UserCreateForm
    success_url = reverse_lazy('login')
    template_name = 'user_app/signup.html'

# def user_login(request):

#     if request.method == "POST":
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         user = authenticate(username=username,password=password)

#         if user:
#             if user.is_active:
#                 login(request, user)
#                 #return HttpResponseRedirect(reverse('index'))
#                 return render (request, 'index.html', {}
#                 )
#             else:
#                 return HttpResponse("Your account is not active")
#         else:
#             print ("someone tried to log in and failed")
#             #print ("Username: {} and password {}".format(username,password))
#             print ("Username: {} ".format(username))
#             return HttpResponse("invalid login details supplied")
#     else:
#         return render(request, 'login.html', {})


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
            week = Week.objects.filter(season_model__current=True).last()
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

        sb_user_list = ['john', 'jcarl62', 'BigDipper', 'shishmeister', 'JoeLong', 'Laroqm']
        golf_auction_user_list = ['john', 'jcarl62', 'ryosuke']
        print ('game', game)
        print ('picks', picks)
        return render(request, 'index.html', {
            'fb_week': week,
            'sb_user_list': User.objects.filter(username__in=['john', 'jcarl62']),
            'game': game,
            'picks': picks,
            #'sb_user_list': sb_user_list,
            'golf_auction_user_list': golf_auction_user_list,
            't': t,

                })


@login_required
def special(request):
    return HttpResponse("You are logged in!")


# def register(request):
#     registered = False

#     if request.method == "POST":
#         user_form = UserForm(data=request.POST)


#         if user_form.is_valid():
#             user = user_form.save()
#             user.set_password(user.password)
#             user.save()

#             registered = True
#         else:
#             print(user_form.errors)

#     else:
#         user_form = UserForm()


#     return render(request,'registration.html',
#                             {'user_form': user_form,
#                              'registered': registered})


# @login_required
# def user_logout(request):
#     logout(request)
#     return HttpResponseRedirect(reverse('index'))
