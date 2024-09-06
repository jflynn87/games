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
#import scipy.stats as ss
from django.forms import formset_factory
from fb_app import calc_score


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

        base_data = self.get_base_data()

        user = base_data[0]
        player = base_data[1]
        league = base_data[2]
        week = base_data[3]


        pick_data = self.get_picks(player, league, week)

        player_list = pick_data[0]
        pick_pending = pick_data[1]
        pick_dict = pick_data[2]

        if self.request.POST:
            winners = self.request.POST.getlist('winners')
            projected = self.request.POST.getlist('projected')
            win_list = winners + projected
            scores = self.calc_scores(player, week, player_list, pick_dict, win_list)
        else:
            scores = self.calc_scores(player, week, player_list, pick_dict)

        scores_list = scores[0]
        ranks = scores[1]
        projected_scores = scores[2]
        projected_ranks = scores[3]
        total_score_list = scores[4]
        season_ranks = scores[5]
        #gets picks for any player with picks
        #get scores

        #get game id's to look up score in json files
        #add a query to skip if all games are done and updated in db

        context.update({
        'players': player_list,
        'picks': pick_dict,
        'week': week,
        'pending': pick_pending,
        'games': Games.objects.filter(week=week).order_by('eid'),
        'scores': scores_list,
        'projected_ranks': projected_ranks,
        'projected_scores': projected_scores,
        'ranks': ranks,
        'totals': total_score_list,
        'season_ranks': season_ranks,
        })
        #print (context)
        return context

    def post(self, request):

        context = self.get_context_data()
        #print (context)

        return render(request, 'fb_app/scores.html', {
        'players': context['players'],
        'picks': context['picks'],
        'week': context['week'],
        'pending': context['pending'],
        'games': context['games'],
        'scores': context['scores'],
        'projected_ranks': context['projected_ranks'],
        'projected_scores': context['projected_scores'],
        'ranks': context['ranks'],
        'totals': context['totals'],
        'season_ranks': context['season_ranks'],
        })



#        base_data = get_base_data()

#        user = base_data[0]
#        player = base_data[1]
#        league = base_data[2]
#        week = base_data[3]

#        scores = calc_score.calc_score(league, win_list)

#        ranks = ss.rankdata(scores[0], method='min')
#        projected_ranks = ss.rankdata(scores[1], method='min')

#        return render('fb_app:scores', {
#            'players': player_list,
#            'picks': pick_dict,
#            'week': week,
#            'pending': pick_pending,
#            'games': Games.objects.filter(week=week),
#            'scores': scores[0],
#            'projected_ranks': projected_ranks,
#            'projected_scores': scores[1],
#            'ranks': ranks,
#            'totals': total_score_list,
#            'season_ranks': season_ranks,
#        })


    def get_base_data(self):
        '''takes in self object and calculates the user, player, league and week,
         returns a tuple of objects'''

        week = Week.objects.get(current=True)

        if self.request.user.is_authenticated:
            user = User.objects.get(username=self.request.user)
            player = Player.objects.get(name=user)
            league = player.league

        else:
            league = League.objects.get(league="Football Fools")
            user= None
            player = None

        return (user, player, league, week)



    def get_picks(self, player, league, week):
        '''takes in objects from base and returns a tuple with player lists and
        a dictionary of picks'''

        player_list = []
        pick_list = []
        pick_pending = []
        pick_dict = {}
        pick_num = 16

        for player in Player.objects.filter(league=league).order_by('name'):
            if Picks.objects.filter(week=week, player=player):
                player_list.append(player)
            else:
                pick_pending.append(player)

        while pick_num > 0:
            if Picks.objects.filter(week=week, pick_num=pick_num, player__league=league):
               for picks in Picks.objects.filter(week=week, pick_num=pick_num, player__league=league).order_by('player__name'):
                   pick_list.append(picks.team)
               pick_dict[pick_num]=pick_list
               pick_list = []
            pick_num -= 1

        return (player_list, pick_pending, pick_dict)


    def calc_scores(self, player, week, player_list, pick_dict, winner_list=None):

        print ('starting nfl json lookup')
        print (datetime.datetime.now())

        if Games.objects.filter(week=week).exclude(final=True).exists():
            json_url = 'http://www.nfl.com/liveupdate/scores/scores.json'

            with urllib.request.urlopen(json_url) as field_json_url:
                data = json.loads(field_json_url.read().decode())

            #use for testing
            #with open ('c:/users/john/pythonProjects/games/gamesProj/fb_app/nfl_scores.json') as f:
            #    data = json.load(f)

            try:
                    for game in Games.objects.filter(week=week).exclude(final=True):
                        home_score = data[game.eid]['home']['score']['T']
                        home_team = data[game.eid]['home']["abbr"]
                        away_team = data[game.eid]['away']["abbr"]
                        away_score = data[game.eid]['away']['score']['T']
                        qtr = data[game.eid]["qtr"]

                        if home_score == away_score:
                            tie = True
                            winner = None
                            loser = None
                        elif home_score > away_score:
                            winner = Teams.objects.get(nfl_abbr=home_team)
                            loser = Teams.objects.get(nfl_abbr=away_team)
                            tie = False
                        else:
                            winner = Teams.objects.get(nfl_abbr=away_team)
                            loser = Teams.objects.get(nfl_abbr=home_team)
                            tie = False

                        setattr(game, 'home_score',home_score)
                        setattr(game, 'away_score',away_score)
                        setattr(game, 'winner', winner)
                        setattr(game, 'loser', loser)
                        setattr(game, 'qtr',qtr)
                        if qtr == "Final":
                            setattr(game, 'final', True)
                            setattr(game, 'tie', tie)
                        else:
                            setattr(game, 'tie', False)

                        game.save()


            except KeyError:
                    print ('NFL score file not ready for the week')
                    pass

        print ('player and score object creation start')
        print (datetime.datetime.now())
        scores_list = []
        projected_scores_list = []
        total_score_list = []


        for player in player_list:
            score_obj, created = WeekScore.objects.get_or_create(player=player, week=week)
            score = 0
            projected_score = 0

            for pick in Picks.objects.filter(player=player, week=week):
                game = Games.objects.get((Q(home=pick.team) | Q(away=pick.team)) & Q(week=week))
                if game.qtr == "Final":
                    if game.tie:
                        score += pick.pick_num
                    elif pick.team == game.loser:
                        score += pick.pick_num
                else:
                    if winner_list:
                        if pick.team.nfl_abbr not in winner_list:
                            projected_score += pick.pick_num
                    else:
                        if pick.team == game.loser:
                            projected_score += pick.pick_num

                setattr (score_obj, "score", score)
                setattr (score_obj, "projected_score", projected_score)
                score_obj.save()

            scores_list.append(score)
            projected_scores_list.append(score + projected_score)

            #calculate season totals
            total_score = 0

            for weeks in WeekScore.objects.filter(player=player, week__week__lte=week.week):
                total_score += weeks.score
            total_score_list.append(total_score)


        ranks = ss.rankdata(scores_list, method='min')
        projected_ranks = ss.rankdata(projected_scores_list, method='min')
        season_ranks = ss.rankdata(total_score_list, method='min')
        print ('sending context')
        print (datetime.datetime.now())

        return (scores_list, ranks, projected_scores_list, projected_ranks, total_score, season_ranks)


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
