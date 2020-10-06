from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView, View, DetailView, UpdateView
import urllib.request
from fb_app.models import Games, Week, Picks, Player, League, Teams, WeekScore, calc_scores, Season
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from fb_app.forms import UserForm, CreatePicksForm#, PickFormSet, NoPickFormSet
from django.core.exceptions import ObjectDoesNotExist
from fb_app.validate_picks import validate
from django.contrib.auth.models import User
from django.db.models import Q, Min, Count
import urllib3
import json
import datetime
import scipy.stats as ss
from django.forms import formset_factory, modelformset_factory
from collections import OrderedDict
from rest_framework.views import APIView
from rest_framework.response import Response
from fb_app import scores, scrape_cbs

#from fb_app import calc_score




# Create your views here.

def ajax_get_spreads(request):
    import urllib3.request
    from bs4 import BeautifulSoup

    if request.is_ajax():
        html = urllib.request.urlopen("https://nypost.com/odds/")
        soup = BeautifulSoup(html, 'html.parser')

        nfl_sect = (soup.find("div", {'class':'odds__table-outer--1'}))
    
        games_dict = []
        
        for row in nfl_sect.find_all('tr')[1:]:
        
            try:
                col = row.find_all('td')
                teams = col[0].text.split()
                line = col[5].text.split()

                if line[0][0] == '-':
                    fav = teams[0]
                    dog = teams[1]
                    spread = line[0]
                    #print ('o/a', line[1])
                else:
                    fav = teams[1]
                    dog = teams[0]
                    spread = line [1]
                    #print ('o/a', line[0])

                if fav == "Team":
                    fav = "Football Team"
                elif dog == "Team":
                    dog = "Football Team"

                fav_obj = Teams.objects.get(long_name__iexact=fav)
                dog_obj = Teams.objects.get(long_name__iexact=dog)
                week = Week.objects.get(current=True)
                #print (week)
                if Games.objects.filter(Q(week=week) & Q(home=fav_obj) & Q(away=dog_obj)).exists():
                    game = Games.objects.get(Q(week=week) & Q(home=fav_obj) & Q(away=dog_obj))
                    game.fav=fav_obj
                    game.dog=dog_obj
                    game.spread=spread
                    game.save()
                    #eid = game.eid
                    #game.update(fav=fav_obj, dog=dog_obj, spread=spread)
                    #print (game, eid)
                    #games_dict[game.eid] = (str(game.fav), spread)
                    games_dict.append((game.eid, game.fav.nfl_abbr, str(game.fav.get_record()), game.dog.nfl_abbr.lower(), str(game.dog.get_record()), spread))

                elif Games.objects.filter(Q(week=week) & Q(home=dog_obj) & Q(away=fav_obj)).exists():
                    game = Games.objects.get(Q(week=week) & Q(home=dog_obj) & Q(away=fav_obj))
                    game.fav=fav_obj
                    game.dog=dog_obj
                    game.spread=spread
                    game.save()

                    #eid = game.eid
                    #game.update(fav=fav_obj, dog=dog_obj, spread=spread)
                    #print (game, eid)
                    #games_dict[game.eid] = (str(game_fav), spread)
                    games_dict.append((game.eid, game.fav.nfl_abbr.lower(), str(fav_obj.get_record()), game.dog.nfl_abbr, str(dog_obj.get_record()), spread))
                else:
                    print ('game not found:', fav, dog)
                
                
            except Exception as e:
                print ('spread look up error', e, game, fav, dog)
        print (games_dict)
        data = json.dumps(games_dict)
        return HttpResponse(data, content_type="application/json")
    else:
        print ('not ajax')
        raise Http404




def get_spreads():
    import urllib3.request
    from bs4 import BeautifulSoup

    html = urllib.request.urlopen("https://nypost.com/odds/")
    soup = BeautifulSoup(html, 'html.parser')
    #print (soup)
    #find nfl section within the html

    nfl_sect = (soup.find("div", {'class':'odds__table-outer--1'}))
    
    #pull out the games and spreads from the NFL section
    
    
    for row in nfl_sect.find_all('tr')[1:]:
        
        try:
          col = row.find_all('td')
          teams = col[0].text.split()
          line = col[5].text.split()

          if line[0][0] == '-':
              fav = teams[0]
              dog = teams[1]
              spread = line[0]
              #print ('o/a', line[1])
          else:
              fav = teams[1]
              dog = teams[0]
              spread = line [1]
              #print ('o/a', line[0])

          fav_obj = Teams.objects.get(long_name__iexact=fav)
          dog_obj = Teams.objects.get(long_name__iexact=dog)
          
          week = Week.objects.get(current=True)
          
          if Games.objects.filter(Q(week=week) & Q(home=fav_obj) & Q(away=dog_obj)).exists():
             Games.objects.filter(Q(week=week) & Q(home=fav_obj) & Q(away=dog_obj)).update(fav=fav_obj, dog=dog_obj, spread=spread)
          elif Games.objects.filter(Q(week=week) & Q(home=dog_obj) & Q(away=fav_obj)).exists():
             Games.objects.filter(Q(week=week) & Q(home=dog_obj) & Q(away=fav_obj)).update(fav=fav_obj, dog=dog_obj, spread=spread)
        except Exception as e:
             print ('spread look up error', e)


    return


#old post logic, keep for a while in case they go back
# def get_spreads():
#     import urllib3.request
#     from bs4 import BeautifulSoup
#
#     html = urllib.request.urlopen("https://nypost.com/sports/")
#     soup = BeautifulSoup(html, 'html.parser')
#
#     #find nfl section within the html
#
#     nfl_sect = (soup.find("div", {'id': 'line-nfl'}))
#     #nfl_sect = (soup.find("div", {'id': 'line-mlb'}))
#
#
#     #pull out the games and spreads from the NFL section
#
#     spreads = {}
#     sep = ' '
#
#     for row in nfl_sect.find_all('tr')[1:]:
#          col = row.find_all('td')
#          fav = col[0].string
#          opening = col[1].string
#          spread = col[2].string.split(sep, 1)[0]
#          dog =  col[3].string
#
#          fav_obj = Teams.objects.get(long_name__iexact=fav)
#          dog_obj = Teams.objects.get(long_name__iexact=dog)
#
#          week = Week.objects.get(current=True)
#
#          try:
#             Games.objects.get(week=week, home=fav_obj)
#             Games.objects.filter(week=week, home=fav_obj).update(fav=fav_obj, dog=dog_obj, opening=opening, spread=spread)
#
#          except ObjectDoesNotExist:
#             Games.objects.filter(week=week,away=fav_obj).update(fav=fav_obj, dog=dog_obj, opening=opening, spread=spread)
#
#     return


class GameListView(LoginRequiredMixin,ListView):
    login_url = 'login'
    model=Games

    def get_context_data(self, **kwargs):
        context = super(GameListView, self).get_context_data(**kwargs)
        week = Week.objects.get(current=True)
        player=Player.objects.get(name=self.request.user)
        PickFormSet = modelformset_factory(Picks, form=CreatePicksForm, max_num=(week.game_cnt))
        NoPickFormSet = modelformset_factory(Picks, form=CreatePicksForm, extra=(week.game_cnt))

        try:
            print ('skipping preads')
            #get_spreads()
        except Exception:
            print ('no spreads available')
        #games=Games.objects.filter(week=week).order_by("eid")
        games=Games.objects.filter(week=week).order_by("game_time")
        if Picks.objects.filter(player=player, week=week).exists():
            form = PickFormSet(queryset=Picks.objects.filter(week=week, player=player))
        else:
            form = NoPickFormSet(queryset=Picks.objects.none())

        team_dict = {}
        for team in Teams.objects.all():
            team_dict[team.id] = team.nfl_abbr


        if Picks.objects.filter(week=week, player=player).count() > 0:
            print ('if')
            context.update({
            'week': Week.objects.get(current=True),
            #'week': Week.objects.filter(season_model__current=True, week__gte=week.week),
            'games_list': games,
            'form': form,
            'teams': team_dict
            })
        else:
            print ('else')
            context.update({
            'week': Week.objects.get(current=True),
            #'week': Week.objects.filter(season_model__current=True, week__gte=week.week),
            'games_list': games,
            'form': form,
            'teams': team_dict
            })

        return context

    def get_success_url(self):
        return redirect('fb_app:picks_list')


    def post(self,request):

         print (request.POST)
             
         week = Week.objects.get(current=True)
         print ('week started', week.started())
         player = Player.objects.get(name=request.user)
         print (player, week, "Making picks", datetime.datetime.now())
         team_dict = {}
         for team in Teams.objects.all():
             team_dict[team.id] = team.nfl_abbr

         pick_list = []
         if request.POST.get('favs') == 'favs':
            sorted_spreads = sorted(week.get_spreads().items(), key=lambda x: x[1][2], reverse=True)
            print ('sspreads', sorted_spreads)
            #list of tuples returned by sort, use tuple to find fav
            for g in sorted_spreads:
                pick_list.append(g[1][0])
            print (pick_list)
         else:
            PickFormSet = modelformset_factory(Picks, form=CreatePicksForm, max_num=(week.game_cnt))
            formset = PickFormSet(request.POST)

            if formset.is_valid():
                print ('valid')
                
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
         #print (picks_chk)
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
            print (datetime.datetime.now(), request.user, 'updating picks')


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

         print (datetime.datetime.now(), request.user, 'saved picks')
         return redirect('fb_app:picks_list')


class PicksListView(LoginRequiredMixin,ListView):
    login_url = 'login'
    redirect_field_name = 'fb_app/pick_list.html'
    model = Picks

    def get_queryset(self):
        return Picks.objects.filter(player__name__username=self.request.user, week__current=True).order_by('-pick_num')

    def get_context_data(self,**kwargs):
        context = super(PicksListView, self).get_context_data(**kwargs)
        context.update({
        'week': Week.objects.get(current=True),
        })
        return context


class ScoresView(TemplateView):
    template_name="fb_app/scores.html"
    model = Week


    def dispatch(self, request, *args, **kwargs):
        print ('kwargs', kwargs)

        if kwargs.get('pk')  == None:
            week = Week.objects.get(current=True)
            if request.user.is_anonymous and \
            Picks.objects.filter(week__pk=week.pk, player__league__league="Football Fools").count() < 20:
                print ('debug 1')
                last_week_n = week.week -1
                last_week = Week.objects.get(season_model__current=True, week=last_week_n)
                self.kwargs['pk'] = str(last_week.pk)
            else:
                print ('debug 2')
                self.kwargs['pk']= str(week.pk)
        
        return super(ScoresView, self).dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):

        context = super(ScoresView, self).get_context_data(**kwargs)
        print (self.kwargs)
        week = Week.objects.get(pk=self.kwargs.get('pk'))
    
        base_data = self.get_base_data()

        user = base_data[0]
        player = base_data[1]
        league = base_data[2]

        print ('before pick data')
        pick_data = self.get_picks(player, league, week)

        player_list = pick_data[0]
        pick_pending = pick_data[1]
        pick_dict = pick_data[2]

        print (pick_data)

        if week.started():
            if len(pick_pending) > 0 and week.started():
            #if len(pick_pending) > 0:
                sorted_spreads = sorted(week.get_spreads().items(), key=lambda x: x[1][2],reverse=True)
                for player in pick_pending:
                    for i, game in enumerate(sorted_spreads):
                        pick = Picks()
                        pick.week = week
                        pick.player = player
                        pick.pick_num = 16 - i
                        pick.team = game[1][1]
                        pick.save()

            if self.request.POST:
                loser_list = []
                proj_loser_list = []
                winners = self.request.POST.getlist('winners')
                for winner in winners:
                    team_obj = Teams.objects.get(nfl_abbr=winner)
                    game = Games.objects.get(winner=team_obj,week=week)
                    loser_list.append(Teams.objects.get(nfl_abbr=game.loser))

                projected = self.request.POST.getlist('projected')

                for team in self.request.POST.getlist('tie'):
                    loser_list.append(Teams.objects.get(nfl_abbr=team))

                for proj in projected:
                    proj_obj = Teams.objects.get(nfl_abbr=proj)
                    try:
                        if Games.objects.get(winner=proj_obj, week=week):
                            game = Games.objects.get(winner=proj_obj, week=week)
                            proj_loser_list.append(Teams.objects.get(nfl_abbr=game.loser))
                    except ObjectDoesNotExist:
                        try:
                            if Games.objects.get(home=proj_obj, week=week):
                                game = Games.objects.get(home=proj_obj, week=week)
                                proj_loser_list.append(Teams.objects.get(nfl_abbr=game.away))
                        except ObjectDoesNotExist:
                            if Games.objects.get(away=proj_obj, week=week):
                                game = Games.objects.get(away=proj_obj, week=week)
                                proj_loser_list.append(Teams.objects.get(nfl_abbr=game.home))

                print ('players', player_list)
                print ('losers', loser_list)
                print ('proj', proj_loser_list)
                week_scores = WeekScore
                #scores = (None, None, None, None, None, None)
                scores = calc_scores(week_scores, league, week, loser_list, proj_loser_list)
            else:
                print ("IN GET calling CALC scores", datetime.datetime.now())
                week_scores = WeekScore
                scores = calc_scores(week_scores, league, week)
                #scores = (None, None, None, None, None, None)
                print ("BACK from calc scores", datetime.datetime.now())


            print (datetime.datetime.now())

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
            'league': league
            })

            print (datetime.datetime.now())
            


            #print (context)
            return context
        else:
            print ('week not started')
            context.update ({'players': player_list,
                        #'picks': pick_dict,
                        'week': week,
                        'pending': pick_pending,
                        'games': Games.objects.filter(week=week).order_by('eid'),
                             })
            return context

    def post(self, request, **kwargs):

        context = self.get_context_data()

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
        '''takes in view object and calculates the user, player, league and week,
         returns a tuple of objects'''

        print ('base', self.kwargs)

        if self.kwargs.get('league') == 'ff' and self.request.user.is_superuser:
            user = User.objects.get(username=self.request.user)
            player = Player.objects.get(name=user)
            league = League.objects.get(league="Football Fools")

        elif self.request.user.is_authenticated:
            user = User.objects.get(username=self.request.user)
            player = Player.objects.get(name=user)
            league = player.league

        else:
            league = League.objects.get(league="Football Fools")
            user= None
            player = None

        return (user, player, league)


    def get_picks(self, player, league, week):
        '''takes in objects from base and returns a tuple with player lists and
        a dictionary of picks'''

        player_list = []
        pick_list_by_num = []
        pick_pending = []
        pick_dict_by_num = {}
        pick_num = 16

        for player in Player.objects.filter(league=league, active=True).order_by('name_id'):
            if Picks.objects.filter(week=week, player=player):
                player_list.append(player)
            else:
                pick_pending.append(player)

        if len(player_list) > 0:
            while pick_num > 16- week.game_cnt:
                if Picks.objects.filter(week=week, pick_num=pick_num, player__league=league, player__active=True):
                    for picks in Picks.objects.filter(week=week, pick_num=pick_num, player__league=league, player__active=True).order_by('player__name_id'):
                         pick_list_by_num.append(picks)    #was picks.team
                    pick_dict_by_num[pick_num]=pick_list_by_num
                    pick_list_by_num = []
                    pick_num -= 1

        print ('pic dic', pick_dict_by_num)
        return (player_list, pick_pending, pick_dict_by_num)


class SeasonTotals(ListView):
    model = WeekScore
    template_name = 'fb_app/season_total.html'

    def get_context_data(self,**kwargs):
        context = super(SeasonTotals, self).get_context_data(**kwargs)

        base_data = self.get_base_data()
        score_dict = {}
        week = base_data[3]
        league = base_data[2]
        week_cnt = 1
        winner_dict = {}
        winners_dict = {}

        for player in Player.objects.filter(league=league, active=True).order_by('name_id'):
            winners_dict[player.name] = 0

        #week by week scores and winner
        while week_cnt <= week.week:
            score_list = []
            score_week = Week.objects.get(season_model__current=True, week=week_cnt)
            week_score = WeekScore.objects.filter(week=score_week, player__league__league=league, player__active=True).order_by('player__name_id')
            if len(week_score) == len(Player.objects.filter(league__league=league, active=True)):
                for score in week_score:
                    score_list.append(score.score)
                if not score_week.current:
                    try:
                        winning_score = WeekScore.objects.filter(player__league=league, week=score_week).aggregate(Min('score'))
                        winners = WeekScore.objects.filter(score=winning_score.get('score__min'), week=score_week, player__league=league)
                        for winner in winners:
                                score = winners_dict.get(winner.player.name)
                                winners_dict[winner.player.name] = score + 30/len(winners)
                                score_list.append(winner.player.name)

                    except IndexError:
                        winner = None

                score_dict[score_week]=score_list
            week_cnt +=1

        #total scores
        total_score_list = []
        for player in Player.objects.filter(league=base_data[2], active=True).order_by('name_id'):
            total_score = 0
            for weeks in WeekScore.objects.filter(player=player, week__week__lte=week.week, week__season_model__current=True).order_by('player_id'):
                if weeks.score == None:
                    weeks.score = 0
                total_score += weeks.score
            total_score_list.append(total_score)

        season_ranks = ss.rankdata(total_score_list, method='min') 

        context.update({
        'players': Player.objects.filter(league=league, active=True).order_by('name_id'),
        'scores': score_dict,
        'totals': total_score_list,
        'wins': winners_dict,
        'ranks': season_ranks,
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


class AboutView(TemplateView):
    template_name = 'fb_app/about.html'


# @login_required
# def user_logout(request):
#     logout(request)
#     return HttpResponseRedirect(reverse('index'))

# @login_required
# def special(request):
#     return HttpResponse("You are logged in!")


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


#     return render(request,'fb_app/registration.html',
#                             {'user_form': user_form,
#                              'registered': registered})

# def user_login(request):

#     if request.method == "POST":
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         user = authenticate(username=username,password=password)

#         if user:
#             if user.is_active:
#                 login(request, user)
#                 #if Picks.objects.filter(user=user):
#                 #    return HttpResponseRedirect(reverse('fb_app:index'))
#                 #else:
#                 return HttpResponseRedirect(reverse('fb_app:games_list'))
#             else:
#                 return HttpResponse("Your account is not active")
#         else:
#             print ("someone tried to log in and failed")
#             #print ("Username: {} and".format(username))
#             print ("Username:", username)
#             return HttpResponse("invalid login details supplied")
#     else:
#         return render(request, 'fb_app/login.html', {})


class AllTime(TemplateView):
    template_name="fb_app/all_time.html"

def ajax_get_games(request, week):
    print ('in getting gamesS')
    if request.is_ajax():
        print (request)
        games = Games.objects.filter(week__week='3')
        data = json.dumps(games)
        return HttpResponse(data, content_type="application/json")
    else:
        print ('not ajax')
        raise Http404

class UpdateNFLScores(APIView):
      pass    
#     def get(self, num):
#         week = Week.objects.get(week=self.request.GET.get('week'), \
#              season_model=Season.objects.get(season=self.request.GET.get('season')))
#         player = Player.objects.get(name=User.objects.get(pk=self.request.user.pk))
#         week_scores = WeekScore
#         nfl_scores = scores.Scores(week, player.league).get_nfl_scores()
#         print ('updte scores', scores)
#         data = json.dumps(nfl_scores)
#         print (data)
#         return Response(data, 200)


class UpdateScores(APIView):
    
    def get(self, num):
        week = Week.objects.get(week=self.request.GET.get('week'), \
            season_model=Season.objects.get(season=self.request.GET.get('season')))
        try:
            player = Player.objects.get(name=User.objects.get(pk=self.request.user.pk))
        except Exception as e:
            player = Player.objects.get(name=User.objects.get(username='milt'))
        
        if week.started():
           games = week.update_games()
           if games == None:
               games = scrape_cbs.ScrapeCBS(week).get_data()
           d = {'player-data': week.get_scores(player.league)}
           print ('d: ',  d) 
           print ('***** games', games)
           display = {**d, **games}
           data = json.dumps(display)
           print ('Update Scores data', data)
        else:
            data = json.dumps({'msg': 'week not started'})
        
        return Response(data, 200)

    def post(self, num):
        print ('in post', self.request.POST)

        data = json.dumps({'testing': 'does this work?'})

        return Response(data, 200)

        

class UpdateProj(APIView):
    pass

class UpdateRank(APIView):
    pass

class UpdateProjRank(APIView):
    pass

class UpdateSeasonTotal(APIView):
    pass

class UpdateSeasonRank(APIView):
    pass

class NewScoresView(TemplateView):
    template_name="fb_app/new_scores.html"
    model = Week


    def dispatch(self, request, *args, **kwargs):
        print ('kwargs', kwargs)

        if kwargs.get('pk')  == None:
            week = Week.objects.get(current=True)
            if request.user.is_anonymous and \
            Picks.objects.filter(week__pk=week.pk, player__league__league="Football Fools").count() < 20:
                print ('debug 1')
                last_week_n = week.week -1
                last_week = Week.objects.get(season_model__current=True, week=last_week_n)
                self.kwargs['pk'] = str(last_week.pk)
            else:
                print ('loggedin')
                self.kwargs['pk']= str(week.pk)
        
        return super(NewScoresView, self).dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):

        context = super(NewScoresView, self).get_context_data(**kwargs)
        print (self.kwargs)
        week = Week.objects.get(pk=self.kwargs.get('pk'))
    
        base_data = self.get_base_data()

        user = base_data[0]
        player = base_data[1]
        league = base_data[2]

        print ('before pick data')
        pick_data = self.get_picks(player, league, week)

        player_list = pick_data[0]
        pick_pending = pick_data[1]
        pick_dict = pick_data[2]

        print (pick_data)

        if week.started():

            if len(pick_pending) > 0 and week.started():
                sorted_spreads = sorted(week.get_spreads().items(), key=lambda x: x[1][2],reverse=True)
                for player in pick_pending:
                    for i, game in enumerate(sorted_spreads):
                        pick = Picks()
                        pick.week = week
                        pick.player = player
                        pick.pick_num = 16 - i
                        pick.team = game[1][1]
                        pick.save()

            if self.request.POST:

                print ('POST ****', self.request.POST)

                loser_list = []
                proj_loser_list = []
                winners = self.request.POST.getlist('winners')
                for winner in winners:
                    team_obj = Teams.objects.get(nfl_abbr=winner)
                    game = Games.objects.get(winner=team_obj,week=week)
                    loser_list.append(Teams.objects.get(nfl_abbr=game.loser))

                projected = self.request.POST.getlist('projected')

                for team in self.request.POST.getlist('tie'):
                    loser_list.append(Teams.objects.get(nfl_abbr=team))

                for proj in projected:
                    proj_obj = Teams.objects.get(nfl_abbr=proj)
                    try:
                        if Games.objects.get(winner=proj_obj, week=week):
                            game = Games.objects.get(winner=proj_obj, week=week)
                            proj_loser_list.append(Teams.objects.get(nfl_abbr=game.loser))
                    except ObjectDoesNotExist:
                        try:
                            if Games.objects.get(home=proj_obj, week=week):
                                game = Games.objects.get(home=proj_obj, week=week)
                                proj_loser_list.append(Teams.objects.get(nfl_abbr=game.away))
                        except ObjectDoesNotExist:
                            if Games.objects.get(away=proj_obj, week=week):
                                game = Games.objects.get(away=proj_obj, week=week)
                                proj_loser_list.append(Teams.objects.get(nfl_abbr=game.home))

                print ('players', player_list)
                print ('losers', loser_list)
                print ('proj', proj_loser_list)
                week_scores = WeekScore
                #scores = (None, None, None, None, None, None)
                scores = calc_scores(week_scores, league, week, loser_list, proj_loser_list)
            else:
                print ("XXIN GET calling CALC scores", datetime.datetime.now())
                week_scores = WeekScore
                #scores = calc_scores(week_scores, league, week)
                scores = (None, None, None, None, None, None)
                print ("BACK from calc scores", datetime.datetime.now())


            print (datetime.datetime.now())

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
            'league': league
            })

            print (datetime.datetime.now())
            


            #print (context)
            return context
        else:
            print ('week not started')
            context.update ({'players': player_list,
                        #'picks': pick_dict,
                        'week': week,
                        'pending': pick_pending,
                        'games': Games.objects.filter(week=week).order_by('eid'),
                             })
            return context

    def post(self, request, **kwargs):

        context = self.get_context_data()

        return render(request, 'fb_app/new_scores.html', {
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
        '''takes in view object and calculates the user, player, league and week,
         returns a tuple of objects'''

        print ('base', self.kwargs)

        if self.kwargs.get('league') == 'ff' and self.request.user.is_superuser:
            user = User.objects.get(username=self.request.user)
            player = Player.objects.get(name=user)
            league = League.objects.get(league="Football Fools")

        elif self.request.user.is_authenticated:
            user = User.objects.get(username=self.request.user)
            player = Player.objects.get(name=user)
            league = player.league

        else:
            league = League.objects.get(league="Football Fools")
            user= None
            player = None

        return (user, player, league)


    def get_picks(self, player, league, week):
        '''takes in objects from base and returns a tuple with player lists and
        a dictionary of picks'''

        player_list = []
        pick_list_by_num = []
        pick_pending = []
        pick_dict_by_num = {}
        pick_num = 16

        for player in Player.objects.filter(league=league, active=True).order_by('name_id'):
            if Picks.objects.filter(week=week, player=player):
                player_list.append(player)
            else:
                pick_pending.append(player)

        if len(player_list) > 0:
            while pick_num > 16- week.game_cnt:
                if Picks.objects.filter(week=week, pick_num=pick_num, player__league=league, player__active=True):
                    for picks in Picks.objects.filter(week=week, pick_num=pick_num, player__league=league, player__active=True).order_by('player__name_id'):
                         pick_list_by_num.append(picks)    #was picks.team
                    pick_dict_by_num[pick_num]=pick_list_by_num
                    pick_list_by_num = []
                    pick_num -= 1

        print ('pic dic', pick_dict_by_num)
        return (player_list, pick_pending, pick_dict_by_num)


class UpdateProj(APIView):
    
    def get(self, num):
        try:
            print ('COMNNECTED')
            print (self.request.GET)
            print (self.request.GET.getlist('winners[]'))

            w = Week.objects.get(week=self.request.GET.get('week'), season_model__current=True)
            l = League.objects.get(league=self.request.GET.get('league'))
            proj_dict = {}

            for player in Player.objects.filter(league=l) :
                proj_score = 0
                for pick in Picks.objects.filter(player=player, week=w):
                    if pick.team.nfl_abbr not in (self.request.GET.getlist('winners[]')):
                        proj_score += pick.pick_num
                proj_dict[player.name.username] = {'proj_score': proj_score}

            print ('update proj: ', proj_dict)
            proj_rank = w.proj_ranks(l, proj_dict)
            print ('update proj ranks: ', proj_rank)

            for player, score in proj_dict.items():
                proj_dict[player].update({'proj_rank': proj_rank[player]})
             

            return Response(json.dumps(proj_dict), 200)
        except Exception as e:
            print ('update proj issue', e)
            return Response(json.dumps({'msg': 'update error'}))




