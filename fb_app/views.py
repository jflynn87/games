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
from django.db.models import Q, Min
import urllib3
import json
import datetime
import scipy.stats as ss
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
        print (self.request.GET)
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
            loser_list = []
            proj_loser_list = []
            winners = self.request.POST.getlist('winners')
            for winner in winners:

                team_obj = Teams.objects.get(nfl_abbr=winner)
                game = Games.objects.get(winner=team_obj)
                loser_list.append(Teams.objects.get(nfl_abbr=game.loser))
            projected = self.request.POST.getlist('projected')
            print (self.request.POST, 'tie')
            for team in self.request.POST.getlist('tie'):
                print ('ties',team)
                projected.append(team)


            for proj in projected:

                proj_obj = Teams.objects.get(nfl_abbr=proj)

                try:
                    if Games.objects.get(winner=proj_obj, week=week):
                        game = Games.objects.get(winner=proj_obj, week=week)
                        loser_list.append(Teams.objects.get(nfl_abbr=game.loser))
                except ObjectDoesNotExist:
                    try:
                        if Games.objects.get(home=proj_obj, week=week):
                            game = Games.objects.get(home=proj_obj, week=week)
                            loser_list.append(Teams.objects.get(nfl_abbr=game.away))
                    except ObjectDoesNotExist:
                         if Games.objects.get(away=proj_obj, week=week):
                            game = Games.objects.get(away=proj_obj, week=week)
                            loser_list.append(Teams.objects.get(nfl_abbr=game.home))
            print (loser_list)
            scores = self.calc_scores(player, week, player_list, pick_dict, loser_list)
        else:
            scores = self.calc_scores(player, week, player_list, pick_dict)

        scores_list = scores[0]
        ranks = scores[1]
        projected_scores = scores[2]
        projected_ranks = scores[3]
        total_score_list = scores[4]
        season_ranks = scores[5]

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
        pick_list_by_num = []
        pick_pending = []
        pick_dict_by_num = {}
        pick_num = 16

        for player in Player.objects.filter(league=league).order_by('name'):
            if Picks.objects.filter(week=week, player=player):
                player_list.append(player)
            else:
                pick_pending.append(player)

        while pick_num > 0:
            if Picks.objects.filter(week=week, pick_num=pick_num, player__league=league):
               for picks in Picks.objects.filter(week=week, pick_num=pick_num, player__league=league).order_by('player__name'):
                   pick_list_by_num.append(picks.team)
               pick_dict_by_num[pick_num]=pick_list_by_num
               pick_list_by_num = []
            pick_num -= 1

        return (player_list, pick_pending, pick_dict_by_num)


    def calc_scores(self, player, week, player_list, pick_dict, loser_list=None):

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
                    for score in Games.objects.filter(week=week).exclude(final=True):
                        home_score = data[score.eid]['home']['score']['T']
                        home_team = data[score.eid]['home']["abbr"]
                        away_team = data[score.eid]['away']["abbr"]
                        away_score = data[score.eid]['away']['score']['T']
                        qtr = data[score.eid]["qtr"]

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

                        setattr(score, 'home_score',home_score)
                        setattr(score, 'away_score',away_score)
                        setattr(score, 'winner', winner)
                        setattr(score, 'loser', loser)
                        setattr(score, 'qtr',qtr)
                        if qtr == "Final":
                            setattr(score, 'final', True)
                            setattr(score, 'tie', tie)
                        elif qtr == "final overtime":
                            setattr(score, 'final', True)
                            setattr(score, 'tie', tie)
                        else:
                            setattr(score, 'tie', False)

                        score.save()


            except KeyError:
                    print ('NFL score file not ready for the week')
                    pass

        print ('player and score object creation start')
        print (datetime.datetime.now())
        scores_list = []
        projected_scores_list = []
        total_score_list = []

        proj_loser_list = []

        if not loser_list:
            loser_list = []
            games = Games.objects.filter(week=week).exclude(qtr=None)
            for game in games:
                if game.final:
                    if game.tie:
                        loser_list.append((game.home))
                        loser_list.append((game.away))
                    else:
                        loser_list.append((game.loser))
                elif game.qtr == "None" or (game.qtr != "None" and game.home_score == game.away_score):
                    print ('no loser yet', game.home)
                    continue
                elif game.home_score > game.away_score:
                    proj_loser_list.append((game.away))
                elif game.away_score > game.home_score:
                    print (home_team)
                    proj_loser_list.append((game.home))
                else:
                    print ('losers list issue', game)

        for player in player_list:
            score_obj, created = WeekScore.objects.get_or_create(player=player, week=week)
            score = 0
            projected_score = 0

            for pick in Picks.objects.filter(Q(player=player) & Q(week=week) & (Q(team__in=loser_list) | Q(team__in=proj_loser_list))):
                if pick.team in loser_list:
                    score += pick.pick_num
                elif pick.team in proj_loser_list:
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

        return (scores_list, ranks, projected_scores_list, projected_ranks, total_score_list, season_ranks)

class SeasonTotals(ListView):
    model = WeekScore
    template_name = 'fb_app/season_total.html'

    def get_context_data(self,**kwargs):
        context = super(SeasonTotals, self).get_context_data(**kwargs)

        base_data = self.get_base_data()
        score_dict = {}
        week = base_data[3]
        week_cnt = 1
        winner_dict = {}

        #week by week scores and winner
        while week_cnt <= week.week:
            score_list = []
            score_week = Week(week=week_cnt)
            week_score = WeekScore.objects.filter(week__week=week_cnt, player__league__league=base_data[2])
            for score in week_score:
                score_list.append(score.score)
            winner = Player.objects.get(pk=(week_score.filter()\
                      .values_list('player').annotate(Min('score'))\
                      .order_by('score')[0])[0])
            score_list.append(winner)
            winner_dict[winner]= score

            score_dict[week_cnt]=score_list
            week_cnt +=1

        #total scores
        total_score_list = []

        for player in Player.objects.filter(league=base_data[2]):
            total_score = 0
            for weeks in WeekScore.objects.filter(player=player, week__week__lte=week.week):
                total_score += weeks.score
            total_score_list.append(total_score)

        #winnings section
        for key, value in winner_dict.items():
            if base_data[2] == "Golfers":
                winner_dict[key] = len(winner_dict.values()), '$' + str((len(winner_dict.values())*25))
            else:
                winner_dict[key] = len(winner_dict.values()), '$' + '0'


        context.update({
        'players': Player.objects.filter(league=base_data[2]),
        'scores': score_dict,
        'totals': total_score_list,
        'wins': winner_dict

        })
        return context


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
