from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView, View
import urllib.request
from fb_app.models import Games, Week, Picks, Player, League, Teams, WeekScore
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from fb_app.forms import UserForm, CreatePicksForm, PickFormSet
from django.core.exceptions import ObjectDoesNotExist
from fb_app.validate_picks import validate
from django.contrib.auth.models import User
from django.db.models import Q
import urllib3
import json
import datetime
import scipy.stats as ss
from dal import autocomplete
from django.forms import formset_factory


# Create your views here.

def index(request):
    return render(request, 'index.html')

def get_spreads():
    import urllib3.request
    from bs4 import BeautifulSoup

    html = urllib.request.urlopen("https://nypost.com/sports/")
    soup = BeautifulSoup(html, 'html.parser')

    #find nfl section within the html

    nfl_sect = (soup.find("div", {'id': 'line-nfl'}))
    #nfl_sect = (soup.find("div", {'id': 'line-mlb'}))


    #pull out the games and spreads from the NFL section

    spreads = {}
    sep = ' '

    for row in nfl_sect.find_all('tr')[1:]:
         col = row.find_all('td')
         fav = col[0].string
         opening = col[1].string
         spread = col[2].string.split(sep, 1)[0]
         dog =  col[3].string

         fav_obj = Teams.objects.get(long_name__iexact=fav)
         dog_obj = Teams.objects.get(long_name__iexact=dog)

         week = Week.objects.get(current=True)

         try:
            Games.objects.get(week=week, home=fav_obj)
            Games.objects.filter(week=week, home=fav_obj).update(fav=fav_obj, dog=dog_obj, opening=opening, spread=spread)

         except ObjectDoesNotExist:
            Games.objects.filter(week=week,away=fav_obj).update(fav=fav_obj, dog=dog_obj, opening=opening, spread=spread)

    return


class GameListView(LoginRequiredMixin,ListView):
    login_url = '/fb_app/user_login'
    model=Games
    PickFormSet = formset_factory(CreatePicksForm)

    def get_context_data(self, **kwargs):
        context = super(GameListView, self).get_context_data(**kwargs)
        week = Week.objects.get(current=True)
        player=Player.objects.get(name=self.request.user)
        get_spreads()
        games=Games.objects.filter(week=week)
        #form = CreatePicksForm()

        PickFormSet = formset_factory(CreatePicksForm, extra=week.game_cnt)

        form = PickFormSet()

        team_dict = {}
        for team in Teams.objects.all():
            team_dict[team.id] = team.nfl_abbr

        if Picks.objects.filter(week=week, player=player).count() > 0:
            picks = Picks.objects.filter(week=week, player=player).order_by('-pick_num')
            context.update({
            'picks_list': picks,
            'games_list': games,
            'form': form,
            'teams': team_dict
            })
        else:
            context.update({
            'games_list': games,
            'form': form,
            'teams': team_dict
            })

        return context

    def get_success_url(self):
        return redirect('fb_app:picks_list')


    def post(self,request):

         #print (request.POST)
         week = Week.objects.get(current=True)
         player = Player.objects.get(name=request.user)
         team_dict = {}
         for team in Teams.objects.all():
             team_dict[team.id] = team.nfl_abbr
         #PickFormSet = formset_factory(CreatePicksForm, extra=week.game_cnt)
         formset = PickFormSet(request.POST)
         if formset.is_valid():
            print ('valid')
            pick_list = []
            for form in formset:
                cd = form.cleaned_data
                team = cd.get('team')
                pick_list.append(team)
         else:

            print (formset.errors)
            return render (request, 'fb_app/games_list.html', {
            'form': formset,
            'message': formset.errors,
            'games_list': Games.objects.filter(week=week),
            'teams': team_dict
            })

         i = 0
         picks_chk = []
         while i < len(pick_list):
             picks_chk.append(str(Teams.objects.get(nfl_abbr=pick_list[i])))
             i +=1
         print (picks_chk)
         picks_check = validate(picks_chk)

         if picks_check[0]:
            print ('pick valid' + str(picks_check[0]))
         else:

            error = picks_check[1]
            return render (request, 'fb_app/games_list.html', {
            'form': formset,
            'message': error,
            'games_list': Games.objects.filter(week=week),
            'teams': team_dict
              })

         if Picks.objects.filter(week=week, player=player).count() >0:
            Picks.objects.filter(week=week, player=player).delete()
            print ('updating picks')


         #pick_dict = {}

         i = 0  #first item in list is pick 16
         pick_num = 16
         while i < week.game_cnt:
        #     pick_dict[pick_list[i]] = pick_list[i+1]
        #     i +=1
         #print (pick_dict)
         #for picknum, pick in pick_dict.items():

             team = picks_chk[i]
             picks = Picks()
             picks.pick_num = pick_num
             picks.team = Teams.objects.get(nfl_abbr__iexact=team)
             picks.player = player
             picks.week = week
             picks.save()
             i +=1
             pick_num -=1


         return redirect('fb_app:picks_list')



class PicksListView(LoginRequiredMixin,ListView):
    login_url = '/fb_app/user_login/'
    redirect_field_name = 'fb_app/pick_list.html'
    model = Picks

    def get_queryset(self):
        print ('in queryset' + str(self.request.user))
        user = User.objects.get(username=self.request.user)
        player = Player.objects.get(name=user)
        #picks = Picks.objects.filter(player=player).order_by('-pick_num')
        return Picks.objects.filter(player=player, week__current=True).order_by('-pick_num')

    def get_context_data(self,**kwargs):
        context = super(PicksListView, self).get_context_data(**kwargs)
        context.update({
        'week': Week.objects.get(current=True),
        'picks_list': self.get_queryset(),
        })
        return context


class ScoresView(TemplateView):
    template_name="fb_app/scores.html"
    model = Picks

    def get_queryset(self):
        return Picks.objects.all().order_by('-pick_num')

    def get_context_data(self, **kwargs):
        context = super(ScoresView, self).get_context_data(**kwargs)

        print (self.request.user)

        if self.request.user.is_authenticated:
            user = User.objects.get(username=self.request.user)
            player = Player.objects.get(name=user)
            league = player.league
        else:
            league = League.objects.get(league="Football Fools")


        week = Week.objects.get(current=True)
        #league = League.objects.get(league="Football Fools")
        player_list = []
        pick_dict = {}
        pick_list = []
        pick_num = 16
        pick_pending = []

        #player list for header or footnote if no picks
        for player in Player.objects.filter(league=league):

            if Picks.objects.filter(week=week, player=player):
               player_list.append(player)
            else:
               pick_pending.append(player)

        #gets picks for any player with picks
        while pick_num > 0:
             if Picks.objects.filter(week=week, pick_num=pick_num, player__league=league):
                for picks in Picks.objects.filter(week=week, pick_num=pick_num, player__league=league):
                    pick_list.append(picks.team)
                pick_dict[pick_num]=pick_list
                pick_list = []
             pick_num -= 1

        #get scores

        #get game id's to look up score in json files
        print ('getting json')
        print (datetime.datetime.now())
        json_url = 'http://www.nfl.com/liveupdate/scores/scores.json'

        with urllib.request.urlopen(json_url) as field_json_url:
            data = json.loads(field_json_url.read().decode())


        try:
          for game in Games.objects.filter(week=week):
            home_score = data[game.eid]['home']['score']['T']
            home_team = data[game.eid]['home']["abbr"]
            away_team = data[game.eid]['away']["abbr"]
            away_score = data[game.eid]['away']['score']['T']
            qtr = data[game.eid]["qtr"]

            #  hack - do something to fix this with the team object
            if away_team == "JAC":
                away_team = "JAX"


            if home_score == away_score:
                tie = True
                winner = None
                loser = None
            elif home_score > away_score:
                winner = Teams.objects.get(nfl_abbr=home_team)
                loser = Teams.objects.get(nfl_abbr=away_team)
            else:
                winner = Teams.objects.get(nfl_abbr=away_team)
                loser = Teams.objects.get(nfl_abbr=home_team)



            setattr(game, 'home_score',home_score)
            setattr(game, 'away_score',away_score)
            setattr(game, 'winner', winner)
            setattr(game, 'loser', loser)
            setattr(game, 'qtr',qtr)

            game.save()


        except KeyError:
            print ('error')


        print ('starting player loop')
        print (datetime.datetime.now())
        scores_list = []
        projected_scores_list = []
        for player in Player.objects.filter(league=league):
            score_obj, created = WeekScore.objects.get_or_create(player=player, week=week)
            score = 0
            projected_score = 0

            for pick in Picks.objects.filter(player=player, week=week):
                game = Games.objects.get((Q(home=pick.team) | Q(away=pick.team)))
                if game.qtr == "Final":
                    if pick.team == game.loser:
                        score += pick.pick_num
                else:
                    if pick.team == game.loser:
                        projected_score += pick.pick_num

                setattr (score_obj, "score", score)
                setattr (score_obj, "projected_score", projected_score)
                score_obj.save()
            scores_list.append(score)
            projected_scores_list.append(score + projected_score)


        ranks = ss.rankdata(scores_list, method='min')
        print (datetime.datetime.now())

        context.update({
        'players': player_list,
        'picks': pick_dict,
        'week': week,
        'pending': pick_pending,
        'games': Games.objects.filter(week=week),
        'scores': scores_list,
        'projected_scores': projected_scores_list,
        'ranks': ranks,
        })

        return context

    def post(self, request):
        print (request.POST)

        return HttpResponse('done')





@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

@login_required
def special(request):
    return HttpResponse("You are logged in!")


def register(request):
    registered = False

    if request.method == "POST":
        user_form = UserForm(data=request.POST)


        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            registered = True
        else:
            print(user_form.errors)

    else:
        user_form = UserForm()


    return render(request,'fb_app/registration.html',
                            {'user_form': user_form,
                             'registered': registered})

def user_login(request):

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username,password=password)

        if user:
            if user.is_active:
                login(request, user)
                #if Picks.objects.filter(user=user):
                #    return HttpResponseRedirect(reverse('fb_app:index'))
                #else:
                return HttpResponseRedirect(reverse('fb_app:games_list'))
            else:
                return HttpResponse("Your account is not active")
        else:
            print ("someone tried to log in and failed")
            print ("Username: {} and".format(username))
            return HttpResponse("invalid login details supplied")
    else:
        return render(request, 'fb_app/login.html', {})
