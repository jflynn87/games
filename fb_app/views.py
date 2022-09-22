from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView, View, DetailView, UpdateView, CreateView
import urllib.request
from fb_app.models import Games, Week, Picks, Player, League, Teams, WeekScore, Season, PickPerformance, \
     PlayoffPicks, PlayoffScores, PlayoffStats, PickMethod, AccessLog, SeasonPicks
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, HttpRequest
from django.urls import reverse, reverse_lazy
#from fb_app.forms import UserForm, CreatePicksForm#, PickFormSet, NoPickFormSet
from fb_app.forms import CreatePicksForm, CreatePlayoffsForm, CreateSeasonPicksForm, SeasonPicksFormSet
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
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from fb_app import scrape_cbs, scrape_cbs_playoff, playoff_stats, espn_data
from django.core import serializers
from bs4 import BeautifulSoup
import pytz
from django.utils import dateformat
from math import ceil
from django.core.mail import send_mail



# Create your views here.

class GetSpreads(generics.ListAPIView):


    def get(self, request, **kwargs):
            try:
                #print ('kwargs', request.Request)
                print ('kwargs1', self.kwargs)
                html = urllib.request.urlopen("https://www.sportsline.com/nfl/odds/")
                soup = BeautifulSoup(html, 'html.parser')
                nfl_sect = (soup.find("div", {'class':'table-container'}))
                games_dict = []
                
                week = Week.objects.get(pk=self.kwargs.get('pk'))
                print ('spreads weeek: ', week)
                try:
                    for row in nfl_sect.find_all('tbody'):
                        away_data = row.find('tr', {'class': 'away-team'})
                        away_team = away_data.find('div', {'class': 'team'}).text
                        away_line = away_data.find_all('td')[2].find('span', {'class': 'primary'}).text
                        away_line_1 = away_data.find_all('td')[2].find('span', {'class': 'secondary'}).text
                        home_data = row.find('tr', {'class': 'home-team'})
                        print (home_data.text)
                        home_team = home_data.find('div', {'class': 'team'}).text
                        home_line = home_data.find_all('td')[2].find('span', {'class': 'primary'}).text
                        home_line_1 = home_data.find_all('td')[2].find('span', {'class': 'secondary'}).text

                        if home_line[0] == '-':
                            fav_obj = Teams.objects.get(long_name__iexact=home_team)
                            dog_obj = Teams.objects.get(long_name__iexact=away_team)
                            spread = home_line + ' ' + home_line_1
                        else:
                            fav_obj = Teams.objects.get(long_name__iexact=away_team)
                            dog_obj = Teams.objects.get(long_name__iexact=home_team)
                            spread = away_line + ' ' + away_line_1

                        home_obj = Teams.objects.get(long_name__iexact=home_team)
                        away_obj = Teams.objects.get(long_name__iexact=away_team)


                        if Games.objects.filter(week=week, home=home_obj, away=away_obj).exists():
                            game = Games.objects.get(week=week, home=home_obj, away=away_obj)
                            game.fav = fav_obj
                            game.dog = dog_obj
                            game.spread = spread
                            game.save()
                            if game.fav == game.home:
                                games_dict.append((game.eid, game.fav.nfl_abbr, str(game.fav.get_record()), game.dog.nfl_abbr.lower(), str(game.dog.get_record()), spread))
                            else:
                                games_dict.append((game.eid, game.fav.nfl_abbr.lower(), str(fav_obj.get_record()), game.dog.nfl_abbr, str(dog_obj.get_record()), spread))
                        else:
                            print ('game not found:', home_team, away_team)
                            
                except Exception as e:
                            print ('spread look up error', e, game, home_team, away_team)
            except Exception as f:
                    print ('NY Post error', f)
                    games_dict = {}
            data = json.dumps(games_dict)
            return Response(data, 200)
            #except Exception as ex:
            #    print ('get spreads error: ', ex)
            #    return Response ({'msgs':ex}, 500)



# class GetSpreads(generics.ListAPIView):


#     def get(self, request, **kwargs):

#             try:
#                 #print ('kwargs', request.Request)
#                 print ('kwargs1', self.kwargs)
#                 html = urllib.request.urlopen("https://nypost.com/odds/")
#                 soup = BeautifulSoup(html, 'html.parser')
#                 nfl_sect = (soup.find("div", {'class':'odds__table-outer--1'}))
#                 games_dict = []
                
#                 #week = Week.objects.get(current=True)
#                 week = Week.objects.get(pk=self.kwargs.get('pk'))
#                 print ('spreads weeek: ', week)
#                 try:
#                     for row in nfl_sect.find_all('tr')[1:]:
#                         try:
#                             col = row.find_all('td')
#                             teams = col[0].text.split()
#                             line = col[5].text.split()
#                             if line[0][0] == '-':
#                                 fav = teams[0]
#                                 dog = teams[1]
#                                 spread = line[0]
#                                 #print ('o/a', line[1])
#                             else:
#                                 fav = teams[1]
#                                 dog = teams[0]
#                                 spread = line [1]
#                                 #print ('o/a', line[0])
#                             if fav == "Team":
#                                 fav = "Football Team"
#                             elif dog == "Team":
#                                 dog = "Football Team"
#                             fav_obj = Teams.objects.get(long_name__iexact=fav)
#                             dog_obj = Teams.objects.get(long_name__iexact=dog)

#                             if Games.objects.filter(Q(week=week) & Q(home=fav_obj) & Q(away=dog_obj)).exists():
#                                 game = Games.objects.get(Q(week=week) & Q(home=fav_obj) & Q(away=dog_obj))
#                                 game.fav=fav_obj
#                                 game.dog=dog_obj
#                                 game.spread=spread
#                                 game.save()
#                                 games_dict.append((game.eid, game.fav.nfl_abbr, str(game.fav.get_record()), game.dog.nfl_abbr.lower(), str(game.dog.get_record()), spread))

#                             elif Games.objects.filter(Q(week=week) & Q(home=dog_obj) & Q(away=fav_obj)).exists():
#                                 game = Games.objects.get(Q(week=week) & Q(home=dog_obj) & Q(away=fav_obj))
#                                 game.fav=fav_obj
#                                 game.dog=dog_obj
#                                 game.spread=spread
#                                 game.save()
#                                 games_dict.append((game.eid, game.fav.nfl_abbr.lower(), str(fav_obj.get_record()), game.dog.nfl_abbr, str(dog_obj.get_record()), spread))
#                             else:
#                                 print ('game not found:', fav, dog)
                            
#                         except Exception as e:
#                             print ('spread look up error', e, game, fav, dog)
#                 except Exception as f:
#                     print ('NY Post error', f)
#                     games_dict = {}
#                 data = json.dumps(games_dict)
#                 return Response(data, 200)
#             except Exception as ex:
#                 print ('get spreads error: ', ex)
#                 return Response ({'msgs':ex}, 500)


class GameListView(LoginRequiredMixin,ListView):
    login_url = 'login'
    model=Games
    
    def get_week(self):
        if self.kwargs.get('pk') != None:
            print ('kwargs driving week')
            return Week.objects.get(pk=self.kwargs.get('pk'))
        else:
            print ('getting current week games')
            return Week.objects.get(current=True)


    def get_context_data(self, **kwargs):
        context = super(GameListView, self).get_context_data(**kwargs)
        print ('game list view', self.kwargs)
        week = self.get_week()
        week_started = week.started()

        player=Player.objects.get(name=self.request.user)
        #not adjusting game cnt as expect postponed only after picks done
        PickFormSet = modelformset_factory(Picks, form=CreatePicksForm, max_num=(week.game_cnt))
        NoPickFormSet = modelformset_factory(Picks, form=CreatePicksForm, extra=(week.game_cnt))
        games=Games.objects.filter(week=week).order_by("game_time")

        if week_started and not Picks.objects.filter(player=player, week=week).exists():
            p = player.submit_default_picks(week)

        if Picks.objects.filter(player=player, week=week).exists():
            form = PickFormSet(queryset=Picks.objects.filter(week=week, player=player), form_kwargs={'week': week})
        else:
            form = NoPickFormSet(queryset=Picks.objects.none(), form_kwargs={'week': week})

        team_dict = {}
        for team in Teams.objects.all():
            team_dict[team.id] = team.nfl_abbr

        if Picks.objects.filter(week=week, player=player).count() > 0:
            context.update({
            'week': week,
            'games_list': games,
            'form': form,
            'teams': team_dict,
            'week_started': week_started
            })
        else:
            context.update({
            'week': week,
            'games_list': games,
            'form': form,
            'teams': team_dict,
            'week_started': week_started
            })

        return context

    def get_success_url(self):
        return redirect('fb_app:picks_list')


    def post(self, request, **kwargs):

         print ('submitting picks', request.user.username, request.POST, kwargs)
             
         #week = Week.objects.get(current=True)
         week = self.get_week()
         print ('week started', week.started())
         player = Player.objects.get(name=request.user)
         print (player, week, "Making picks", datetime.datetime.now())
         team_dict = {}
         for team in Teams.objects.all():
             team_dict[team.id] = team.nfl_abbr

         pick_list = []
         pm = PickMethod()
         pm.week = week
         pm.player = player

         if request.POST.get('favs') == 'favs':
            sorted_spreads = sorted(week.get_spreads().items(), key=lambda x: x[1][2], reverse=True)
            #print ('sspreads', sorted_spreads)
            #list of tuples returned by sort, use tuple to find fav
            for g in sorted_spreads:
                pick_list.append(g[1][0])

            pm.method = '2'
            print ('picking favs', pick_list)
         else:
            PickFormSet = modelformset_factory(Picks, form=CreatePicksForm, max_num=(week.game_cnt))
            formset = PickFormSet(request.POST, form_kwargs={'week': week})

            if formset.is_valid():
                #print ('valid')
                if PickMethod.objects.filter(week=week, player=player, method=3).exists():
                    pm.method = '4'
                else:
                    pm.method = '1'    
                for form in formset:
                    cd = form.cleaned_data
                    team = cd.get('team')
                    pick_list.append(team)
            
            else:
                print ('pick formset errors: ', formset.errors)
                return render (request, 'fb_app/games_list.html', {
                'form': formset,
                'message': formset.errors,
                'games_list': Games.objects.filter(week=week),
                'teams': team_dict,
                'week': week,

                })
         pm.save()
         i = 0
         picks_chk = []
         while i < len(pick_list):
             picks_chk.append(str(Teams.objects.get(nfl_abbr=pick_list[i])))
             i +=1
         #print (picks_chk)
         picks_check = validate(picks_chk, week)

         if picks_check[0]:
            print ('pick valid' + str(picks_check[0]))
         else:

            error = picks_check[1]
            return render (request, 'fb_app/games_list.html', {
            'form': formset,
            'message': error,
            'games_list': Games.objects.filter(week=week),
            'teams': team_dict,
            'week': week,
            
              })

         if Picks.objects.filter(week=week, player=player).count() >0:
            Picks.objects.filter(week=week, player=player).delete()
            print (datetime.datetime.now(), request.user, 'updating picks')


         i = 0  #first item in list is pick 16
         pick_num = 16
         while i < week.game_cnt:

             team = picks_chk[i]
             picks = Picks()
             picks.pick_num = pick_num
             picks.team = Teams.objects.get(nfl_abbr__iexact=team)
             picks.player = player
             picks.week = week
             picks.save()
             i +=1
             pick_num -=1

         try:
            if player.email_picks:
                email_picks(request.user)
         except Exception as e:
            print ('email picks error', e)

         
         print (datetime.datetime.now(), request.user, 'saved picks')
         return redirect('fb_app:picks_list', pk=week.pk)


class PicksListView(LoginRequiredMixin,ListView):
    login_url = 'login'
    redirect_field_name = 'fb_app/pick_list.html'
    model = Picks

    def get_week(self):
        if self.kwargs.get('pk') != None:
            print ('kwargs driving week')
            return Week.objects.get(pk=self.kwargs.get('pk'))
        else:
            print ('getting current week games')
            return Week.objects.get(current=True)


    def get_queryset(self):
        #return Picks.objects.filter(player__name__username=self.request.user, week__current=True).order_by('-pick_num')
        week = self.get_week()
        return Picks.objects.filter(player__name__username=self.request.user, week=week).order_by('-pick_num')

    def get_context_data(self,**kwargs):
        context = super(PicksListView, self).get_context_data(**kwargs)
        context.update({
        'week': self.get_week(),
        })
        return context



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
                        winning_score = WeekScore.objects.filter(player__league=league, player__active=True, week=score_week).aggregate(Min('score'))
                        winners = WeekScore.objects.filter(score=winning_score.get('score__min'), week=score_week, player__league=league, player__active=True)
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



class AllTime(TemplateView):
    template_name="fb_app/all_time.html"

# def ajax_get_games(request, week):
#     #print ('in getting gamesS')
#     if request.is_ajax():
#        # print (request)
#         games = Games.objects.filter(week__week='3')
#         data = json.dumps(games)
#         return HttpResponse(data, content_type="application/json")
#     else:
#         print ('not ajax')
#         raise Http404


class GetGamesAPI(APIView):

    def get(self, request, week_num):
        start = datetime.datetime.now()
        #print ('*** update scores: ', self.request.GET)
        print ('XXXXXX', week_num, type(week_num))
        try:
            week = Week.objects.get(week=week_num, season_model=Season.objects.get(current=True))
            games = serializers.serialize('json', Games.objects.filter(week=week), use_natural_foreign_keys=True)
        except Exception as e:
            print ('fb app Get Games API error: ', e)
            games = {'error': str(e)}
        
        #print ('Update Score duration: ', datetime.datetime.now() - start)
        return Response(games, 200)



class UpdateScores(APIView):
    
    def get(self, num):
        start = datetime.datetime.now()
        #print ('*** update scores: ', self.request.GET)
        week = Week.objects.get(week=self.request.GET.get('week'), \
            season_model=Season.objects.get(season=self.request.GET.get('season')))
        
        league = League.objects.get(league=self.request.GET.get('league'))
        
        #try:
        #    player = Player.objects.get(name=User.objects.get(pk=self.request.user.pk))
        #except Exception as e:
        #    player = Player.objects.get(name=User.objects.get(username='milt'))
        
        if week.started():
           games = week.update_games()
           
           #if games == None:
               #games = scrape_cbs.ScrapeCBS(week).get_data()
           #    games = {'games': espn_data.ESPNData().get_data()}
           #    print ('games after espn inside none ', games)
           d = {'player-data': week.get_scores(league)}
           display = {**d, **games}
           data = json.dumps(display)
        else:
            data = json.dumps({'msg': 'week not started'})
        
        print ('Update Score duration: ', datetime.datetime.now() - start)
        return Response(data, 200)

    def post(self, num):
        #print ('in post', self.request.POST)

        data = json.dumps({'testing': 'does this work?'})

        return Response(data, 200)
        

class NewScoresView(TemplateView):
    template_name="fb_app/new_scores.html"
    model = Week


    def dispatch(self, request, *args, **kwargs):
        print ('kwargs', kwargs)
        start = datetime.datetime.now()

        if kwargs.get('pk')  == None:
            week = Week.objects.get(current=True)
            if (request.user.is_anonymous or kwargs.get('league') == 'ff') and \
            Picks.objects.filter(week__pk=week.pk, player__league__league="Football Fools").count() < 20:
                last_week_n = week.week -1
                last_week = Week.objects.get(season_model__current=True, week=last_week_n)
                self.kwargs['pk'] = str(last_week.pk)
            else:
                self.kwargs['pk']= str(week.pk)
        print ('finsihed new score dispatch: ', datetime.datetime.now() - start)
        return super(NewScoresView, self).dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        start = datetime.datetime.now()
        context = super(NewScoresView, self).get_context_data(**kwargs)
        access = save_access_log(self.request, 'scores_view')
        print (self.kwargs)
        week = Week.objects.get(pk=self.kwargs.get('pk'))
        week_started = week.started()
    
        base_data = self.get_base_data(week, week_started)

        user = base_data[0]
        player = base_data[1]
        league = base_data[2]
        view = base_data[3]

        if week.picks_complete(league) or league.league == 'Football Fools':
            print ('picks complete')
        else:
            if week_started:
                for player in Player.objects.filter(league=league, active=True):
                    if Picks.objects.filter(player=player, week=week).count() < 1:
                        player.submit_default_picks(week)
        
        if league.ties_lose:
            #print ('ties lose')
            game_cnt = Games.objects.filter(week=week).exclude(postponed=True).count()
        else:
            game_cnt = week.game_cnt              

        if week.week != 1 and view != 'scores_view':
            prior_week = Week.objects.get(week=week.week-1, season_model__current=True)
            prior_week_scores = WeekScore.objects.filter(player__league=league, week=prior_week, week__season_model__current=True).order_by('score')
        else:
            prior_week = Week.objects.exclude(current=True).last()
            prior_week_scores = None
            
        if PickMethod.objects.filter(week=week, method='3').exists():
            espn = espn_data.ESPNData()
            if espn.regular_week() and len(espn.first_game_of_week()) == 1:
                thurs_game = Games.objects.get(eid=espn.first_game_of_week()[0])
                late_users = list(PickMethod.objects.filter(week=week, method='3').values_list('player', flat=True))
                if Picks.objects.filter(team=thurs_game.winner, player__in=late_users).exists():
                    Picks.objects.filter(team=thurs_game.winner, player__in=late_users).update(team=thurs_game.loser)

        print ('game count: ', game_cnt)
        #if week.started():
        if view == 'scores_view':
            context.update({
            'players': None,
            'picks': None,
            'week': week,
            'pending': None,
            'games': None,
            'scores': None,
            'projected_ranks': None,
            'projected_scores': None,
            'ranks': None,
            'totals': None,
            'season_ranks': None,
            'league': league,
            'game_cnt': game_cnt, 
            'week_started': week_started, 
            'view': view
            })

            print ('*******finished context: ', datetime.datetime.now() - start)
            
            return context
        elif view == 'pre_start':
            print ('week not started')
            player_list = []
            picks_pending = []
            picks_submitted = []
            for player in Player.objects.filter(league=league, active=True):
                player_list.append(player.name.username)
                if player.picks_submitted(week):
                    picks_submitted.append(player.name.username)
                else:
                    picks_pending.append(player.name.username)
            
            #prior_week_scores = WeekScore.objects.filter(player__league=league, week__week=week.week - 1, week__season_model__current=True).order_by('score')

            context.update ({'players': picks_submitted,
                        #'picks': pick_dict,
                        'week': week,
                        'pending': picks_pending,
                        'league': league, 
                        'scores': prior_week_scores,
                        #'prior_week': Week.objects.get(week=week.week-1, season_model__current=True),
                        'prior_week': prior_week,
                        'week_started': week_started,
                        'view': view
                        
                        #'games': Games.objects.filter(week=week).order_by('eid'),
                             })
            return context

        elif view == 'no_picks':
            print ('no picks view: ', self.request.user)
            player_list = []
            picks_pending = []
            picks_submitted = []
            for player in Player.objects.filter(league=league, active=True):
                player_list.append(player.name.username)
                if player.picks_submitted(week):
                    picks_submitted.append(player.name.username)
                else:
                    picks_pending.append(player.name.username)
            
            #prior_week_scores = WeekScore.objects.filter(player__league=league, week__week=week.week - 1, week__season_model__current=True).order_by('score')

            context.update ({'players': picks_submitted,
                        #'picks': pick_dict,
                        'week': week,
                        'pending': picks_pending,
                        'league': league, 
                        'scores': prior_week_scores,
                        #'prior_week': Week.objects.get(week=week.week-1, season_model__current=True),
                        'prior_week': prior_week,
                        'week_started': week_started,
                        'view': view
                        
                        #'games': Games.objects.filter(week=week).order_by('eid'),
                             })
        else:
            print ('score view unknown: ', base_data)
            raise HTTP404

        return context


    def get_base_data(self, week, week_started):
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

        if week_started and league.league == 'Football Fools':
            view = 'scores_view'
        elif not week_started and league.league == 'Football_Fools':
            view = 'pre_start'
        elif not week_started:
            view = 'pre_start'
        elif week_started and not week.regular_week:
            view = 'scores_view'
        elif week_started and week.regular_week and PickMethod.objects.filter(player=player, week=week).exclude(method=3).exists():
            view = 'scores_view'
        elif week_started and week.regular_week and PickMethod.objects.filter(player=player, week=week, method=4).exists():
            view = 'scores_view'
        else:
            view = 'no_picks'


        return (user, player, league, view)



class UpdateProj(APIView):
    
    def get(self, num):
        try:
            print (self.request.GET.getlist('winners[]'))

            w = Week.objects.get(week=self.request.GET.get('week'), season_model__current=True)
            l = League.objects.get(league=self.request.GET.get('league'))
            proj_dict = {}

            for player in Player.objects.filter(league=l, active=True):
                proj_score = 0
                for pick in Picks.objects.filter(player=player, week=w):
                    if Games.objects.filter(Q(home=pick.team) | Q(away=pick.team), week=w, postponed=False, tie=True).exists() and l.ties.lose:
                        proj_score += pick.pick_num
                    elif Games.objects.filter(Q(home=pick.team) | Q(away=pick.team), week=w, postponed=False).exists():
                        if pick.team.nfl_abbr not in (self.request.GET.getlist('winners[]')):
                            proj_score += pick.pick_num
                proj_dict[player.name.username] = {'proj_score': proj_score}

            #print ('update proj: ', proj_dict)
            proj_rank = w.proj_ranks(l, proj_dict)
            #print ('update proj ranks: ', proj_rank)

            for player, score in proj_dict.items():
                proj_dict[player].update({'proj_rank': proj_rank[player]})
             

            return Response(json.dumps(proj_dict), 200)
        except Exception as e:
            print ('update proj issue', e)
            return Response(json.dumps({'msg': 'update error'}))


        for player in Player.objects.filter(league=league, active=True):
            score_dict[player.name.username] = {}
        
        print ('before building pick dict:', datetime.datetime.now() - start)


class GetPicks(APIView):
    
    def get(self, num):
        try:
            print ('get picks', self.request.GET)
            score_dict = {}
            league = League.objects.get(league=self.request.GET.get('league'))
            week = Week.objects.get(week=self.request.GET.get('week'), season_model__current=True)
            for player in Player.objects.filter(league=league, active=True):
                score_dict[player.name.username] = {}
        

            for pick in Picks.objects.filter(player__league=league, week=week, player__active=True).order_by('player__name__username').order_by('pick_num'):
                if pick.is_loser():
                    status = 'loser' 
                else:
                    status = 'reg'
                try:
                    score_dict[pick.player.name.username]['picks'].update({pick.pick_num: {'team': pick.team.nfl_abbr, 'status': status}})
                except Exception as e:
                    score_dict[pick.player.name.username]['picks'] = {pick.pick_num: {'team': pick.team.nfl_abbr, 'status': status}}

            return Response(json.dumps(score_dict), 200)

        except Exception as e:
            print ('get picks api issue: ', e)
            return Response(json.dumps({'msg': e}), 200)

class UpdateGamesList(APIView):
    
    def get(self, num):
        try:
            #print ('get picks', self.request.GET)
            score_dict = {}
            league = League.objects.get(league=self.request.GET.get('league'))
            week = Week.objects.get(week=self.request.GET.get('week'), season_model__current=True)
            for player in Player.objects.filter(league=league, active=True):
                score_dict[player.name.username] = {}
        

            for pick in Picks.objects.filter(player__league=league, week=week, player__active=True).order_by('player__name__username').order_by('pick_num'):
                if pick.is_loser():
                    status = 'loser' 
                else:
                    status = 'reg'
                try:
                    score_dict[pick.player.name.username]['picks'].update({pick.pick_num: {'team': pick.team.nfl_abbr, 'status': status}})
                except Exception as e:
                    score_dict[pick.player.name.username]['picks'] = {pick.pick_num: {'team': pick.team.nfl_abbr, 'status': status}}

            return Response(json.dumps(score_dict), 200)

        except Exception as e:
            print ('get picks api issue: ', e)
            return Response(json.dumps({'msg': e}), 200)


class GetWeeks(APIView):
    
    def get(self, request):
        try:
            #print ('get weeks', request.GET)

            c_week = Week.objects.get(current=True)

            data = serializers.serialize('json', Week.objects.filter(week__gte=c_week.week, season=c_week.season))
            #print ('getWeeks', data)
            return Response(data, 200)
            #return Response(json.dumps(score_dict), 200)

        except Exception as e:
            print ('get weeks api issue: ', e)
            return Response(json.dumps({'msg': e}), 200)

class SpreadView(TemplateView):
    '''allows seeing games list and spreads without login.  no pick capability'''
    #model = Games
    template_name = 'fb_app/spread_view.html'

    def get_week(self):
        if self.kwargs.get('pk') != None:
            print ('kwargs driving week')
            return Week.objects.get(pk=self.kwargs.get('pk'))
        else:
            print ('getting current week games')
            c_week = Week.objects.get(current=True)
            if c_week.started():
                return Week.objects.get(season_model__current=True, week=c_week.week+1)
            else:
                return Week.objects.get(current=True)

    def get_context_data(self,**kwargs):
        context = super(SpreadView, self).get_context_data(**kwargs)
        context.update({
        'week': self.get_week(),
        'games': Games.objects.filter(week=self.get_week()).order_by('game_time')
        })
        return context


class GetPick(APIView):
    permission_classes = [AllowAny]
    def post(self, request):

        data = {}
        for pick in Picks.objects.filter(week__week=request.data['week'], pick_num=int(request.data['pick_num']), week__season_model__current=True, player__league__league=request.data['league']):
            try:
                data[pick.pick_num].update({str(pick.player.name.username): 
                    {'team': pick.team.nfl_abbr, 
                    'logo': pick.team.pic,
                    'loser': pick.is_loser()}})
            except Exception as e:
                data[pick.pick_num] = {str(pick.player.name.username): 
                    {'team': pick.team.nfl_abbr, 
                    'logo': pick.team.pic, 
                    'loser': pick.is_loser()}}
                
        return Response(json.dumps(data), 200)


class FBLeaderboard(APIView):
    def get(self, request):

        try:
            data = {}
            player = Player.objects.get(name=request.user)
            
            #league = League.objects.get(league=player.league)
            ranks = player.league.season_ranks()

            for p in Player.objects.filter(league=player.league, active=True):
                
                data[p.name.username] = {'score': p.season_total(),
                                            'rank': ranks[p.name.username],
                                            'behind': p.season_points_behind()
                                        }
                if p.season_picks_record():
                    record = p.season_picks_record()
                    data.get(p.name.username).update({'season_wins': [v.get('wins') for k, v in record.items() if k == p.name.username][0], \
                                                     'season_loss': [v.get('loss') for k, v in record.items() if k == p.name.username][0]})
                else:
                    data.get(p.name.username).update({'season_wins': 0, 'season_loss': 0})

            sorted_data = sorted(data.items(), key=lambda x: x[1]['rank'])
            #print (sorted_data)
        except Exception as e:
            print ('error: ', e)
            sorted_data = {}
            sorted_data['error'] = {'msg': str(e)}
                
        return Response(json.dumps(sorted_data), 200)


class Analytics(TemplateView):
    template_name="fb_app/analytics.html"

    def get_context_data(self, **kwargs):
        context = super(Analytics, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            player = Player.objects.get(name=self.request.user)
            context.update(
                {'player_list': Player.objects.filter(league=player.league, active=True)}            
                          )
        else:
            context.update(
                {'player_list': Player.objects.filter(league=League.objects.get(league='Football Fools'), active=True)}
                           )
        return context


class AllTeamResults(APIView):
    def get(self, request, player_key):
        try:
            player = Player.objects.get(name__pk=player_key)
            stats = PickPerformance.objects.get(season__current=True, league=player.league)
            player_stats = json.loads(stats.data)[player.name.username]

            league_data = stats.all_team_results()
            player_data = [{k: {'wrong': d['wrong'], 'right': d['right'],
             'win_percent': "{:.0%}".format(round(int(d['right'])/(int(d['right'])+int(d['wrong'])),2))} for k, d in player_stats.items()}]
            #print (type(player_data), len(player_data), player_data)
            sorted_player_data = {k: v for k, v in sorted(player_data[0].items(), key=lambda item: item[1]['win_percent'])}
            #print (sorted_player_data)
            data = {
                'player_data': sorted_player_data,
                'league_data': league_data
            }
            return JsonResponse({'response': data}, status=200)
        except Exception as e:
            print ('AllTeamsResults error: ', e)
            
            return JsonResponse({'respoonse': {'error': str(e)}}, status=400)


class TeamResults(APIView):
    def get(self, request, player_key, nfl_abbr):
        print (request.GET, 'nfl: ', nfl_abbr, player_key)
        try:
            data = {}
            player = Player.objects.get(name__pk=player_key)
            stats = PickPerformance.objects.get(season__current=True, league=player.league)
            player_stats = stats.team_results(nfl_abbr, player)
            league_stats = stats.team_results(nfl_abbr)
            data = {'response': {'player_stats': player_stats,
                                'league_stats': league_stats,}
                                }


            return JsonResponse(data, status=200)
            #print (sorted_data)
        except Exception as e:
            print ('GetTeamsResul error: ', e)
            
            return JsonResponse({'response': {'error': str(e)}}, status=400)


class CreatePlayoffs(LoginRequiredMixin, CreateView):
    template_name='fb_app/playoff_form.html'
    form_class = CreatePlayoffsForm
    success_url = '/'
    redirect_field_name = '/'
    
    def get_context_data(self, **kwargs):
        context = super(CreatePlayoffs, self).get_context_data(**kwargs)
        #player = Player.objects.get(name=self.request.user)
        game = Games.objects.get(week__current=True, playoff_picks=True)

        context.update(
                {'game': game})
        return context

    def form_valid(self, form):
        playoff_picks = form.save(commit=False)
        playoff_picks.player = Player.objects.get(name=self.request.user)
        playoff_picks.game = Games.objects.get(week__current=True, playoff_picks=True)
        playoff_picks.save()
        return super().form_valid(form)


class UpdatePlayoffs(LoginRequiredMixin, UpdateView):
    template_name='fb_app/playoff_form.html'
    model = PlayoffPicks
    form_class = CreatePlayoffsForm
    success_url = '/'
    redirect_field_name = '/'

    def get_context_data(self, **kwargs):
        context = super(UpdatePlayoffs, self).get_context_data(**kwargs)
        #player = Player.objects.get(name=self.request.user)
        game = Games.objects.get(week__current=True, playoff_picks=True)

        context.update(
                {'game': game})
        return context

    
class PlayoffScores(LoginRequiredMixin, TemplateView):
    template_name = 'fb_app/playoff_score.html'


    def get_context_data(self, **kwargs):
        context = super(PlayoffScores, self).get_context_data(**kwargs)
        #player = Player.objects.get(name=self.request.user)
        game = Games.objects.get(week__current=True, playoff_picks=True)

        context.update(
                {'game': game})
        return context


class UpdatePlayoffScores(APIView):
    def get(self, request):
        
        try:
            #data = {}
            game = Games.objects.get(week__current=True, playoff_picks=True)
            stats, created = PlayoffStats.objects.get_or_create(game=game)
            picks = {}

            if stats.data:
                if stats.data.get('qtr') != "Final":
                    web = scrape_cbs_playoff.ScrapeCBS()
                    updated_stats = calc_qb_ratings(web.get_data())
                    stats.data = updated_stats 
                    stats.save()
                #else:
                #    pass
            else:
                web = scrape_cbs_playoff.ScrapeCBS()
                updated_stats = calc_qb_ratings(web.get_data())
                stats.data = updated_stats 
                stats.save()

            stat_data = playoff_stats.Stats().get_all_stats()

            for p in PlayoffPicks.objects.filter(game=game):
                picks[p.player.name.username]= {
                    'rushing_yards': p.rushing_yards,
                    'passing_yards': p.passing_yards,
                    'total_points_scored': p.total_points_scored,
                    'points_on_fg': p.points_on_fg,
                    'takeaways': p.takeaways,
                    'sacks': p.sacks,
                    'def_special_teams_tds': p.def_special_teams_tds,
                    'home_runner': p.home_runner,
                    'home_receiver': p.home_receiver,
                    'home_passing': p.home_passing,
                    'home_passer_rating': p.home_passer_rating,
                    'away_runner': p.away_runner,
                    'away_receiver': p.away_receiver,
                    'away_passing': p.away_passing,
                    'away_passer_rating': p.away_passer_rating,
                    'winning_team': p.winning_team.nfl_abbr

                }

            #print ('pre calc XXXX', stat_data)
            #print ('pre calc stats', stat_data)
            scores = calc_scores(picks, stat_data, game)
            #sorted_picks = sorted(k, x in picks.items(), key=lambda k, x: scores.get(x).get('player_total'), reverse=True)
            #sorted_pair_list = sorted(dic.items(), key=lambda x: dict_key.get(x[0]))
            #print (sorted_picks)
            data = {'response':
                    {'picks': picks,
                     'stats': stat_data,
                     'scores': scores
                    }}

            #print(data)
            return JsonResponse(data, status=200)
            #print (sorted_data)
        except Exception as e:
            print ('UpdatePlayoffScores error: ', e)
            r = HttpRequest.method="GET"
            #scores = views.UpdatePlayoffScores().get(r)
            started = PlayoffGameStarted().get(r)
            print ('started check', started)
            
            if json.loads(started._container[0])['response']['game_started']:
                for p in PlayoffPicks.objects.filter(game=game):
                    picks[p.player.name.username]= {
                        'rushing_yards': p.rushing_yards,
                        'passing_yards': p.passing_yards,
                        'total_points_scored': p.total_points_scored,
                        'points_on_fg': p.points_on_fg,
                        'takeaways': p.takeaways,
                        'sacks': p.sacks,
                        'def_special_teams_tds': p.def_special_teams_tds,
                        'home_runner': p.home_runner,
                        'home_receiver': p.home_receiver,
                        'home_passing': p.home_passing,
                        'home_passer_rating': p.home_passer_rating,
                        'away_runner': p.away_runner,
                        'away_receiver': p.away_receiver,
                        'away_passing': p.away_passing,
                        'away_passer_rating': p.away_passer_rating,
                        'winning_team': p.winning_team.nfl_abbr

                    }
                    print ('formatting data ', p.winning_team.nfl_abbr)
                data = {'response':
                    {'picks': picks,
                     'stats': None,
                     'scores': None
                    }}
                
                JsonResponse(data, status=200)
            else:
                print ('not started')

            return JsonResponse({'response': {'error': str(e)}}, status=400)

class PlayoffGameStarted(APIView):
    '''takes a request and returns json'''
    def get(self, request):
        #make game a parameter, for now assume it is just the current week game
        game = Games.objects.get(playoff_picks=True, week__current=True)
        try:
            if game.qtr in ['pregame', None]:
                stats, created = PlayoffStats.objects.get_or_create(game=game)
                

                #if created or stats.data.get('qtr') == 'pregame' or stats.data.get('qtr') == None:
                print (len(stats.data))
                if stats.data == None or len(stats.data) == 0 or stats.data.get('qtr') == 'pregame' or stats.data.get('qtr') == None:
                    print ('started checking web scrape created is: ', created)
                    web = scrape_cbs_playoff.ScrapeCBS().get_data()
                    stats.data = web
                    stats.save()

                    #if created:
                    if  web['qtr'] in ['pregame', None]:
                        print ('NOT started during create sect based on not being pregame')
                        return JsonResponse({'response': {'game_started': False}})
                    else:
                        print ('started during create sect based on not being pregame')
                        return JsonResponse({'response': {'game_started': True}})
                elif stats.data.get('qtr') != 'pregame' and stats.data.get('qtr') != None:
                    print ('started based on stats data qtr not pregame/none')
                    return JsonResponse({'response': {'game_started': True}})
                else:
                    print ('playoff started check in else but shouldnt get here')
                    return JsonResponse({'response': {'game_started': False}})
            else:
                print ('game started based on game DB not = pregame')
                return JsonResponse({'response': {'game_started': True}})

        except Exception as e:
            print ('not finding game started', e)
            return JsonResponse({'response': {'game_started': False}})



class TeamOffStatsView(APIView):
    '''takes a request and returns json'''
    def get(self, request, nfl_abbr):
        start = datetime.datetime.now()
        print (nfl_abbr)
        team = Teams.objects.get(nfl_abbr=nfl_abbr)
        stats_dict = {}
        html = urllib.request.urlopen("https://www.cbssports.com/nfl/stats/team/team/total/nfl/regular/")

        soup = BeautifulSoup(html, 'html.parser')

        teams = soup.find('div', {'id': 'TableBase'})
        stats = teams.find_all('tr', {'class': 'TableBase-bodyTr'})

        for data in stats:
            row = data.find_all('td')
            team = row[0].a['href'].split('/')[3]
            #if team == 'LAR':
            #    team = "LA"
            gp = row[1].text.strip()
            yards = row[2].text.strip()
            yards_per_game = row[3].text .strip()
            pass_yards = row[4].text.strip()
            pass_yards_per_game = row[5].text.strip()
            rush_yards = row[6].text.strip()
            rush_yards_per_game = row[7].text.strip()
            points = row[8].text.strip()
            points_per_game = row[9].text.strip()

            stats_dict[team] = {
                                    'gp': gp, 
                                    'yards': yards,
                                    'yards_per_game': yards_per_game,
                                    'pass_yards': pass_yards,
                                    'pass_yards_per_game': pass_yards_per_game,
                                    'rush_yards': rush_yards,
                                    'rush_yards_per_game': rush_yards_per_game,
                                    'points': points,
                                    'points_per_game': points_per_game,
                            
            }

        return JsonResponse(stats_dict, status=200)

class TeamDefStatsView(APIView):
    '''takes a request and returns json'''
    def get(self, request, nfl_abbr):
        start = datetime.datetime.now()
        print (nfl_abbr)
        team = Teams.objects.get(nfl_abbr=nfl_abbr)
        stats_dict = {}

        html = urllib.request.urlopen("https://www.cbssports.com/nfl/stats/team/team/defense/nfl/regular/")  # defense
        soup = BeautifulSoup(html, 'html.parser')

        teams = soup.find('div', {'id': 'TableBase'})
        stats = teams.find_all('tr', {'class': 'TableBase-bodyTr'})

        for data in stats:
            row = data.find_all('td')
            team = row[0].a['href'].split('/')[3]
            #if team == 'LAR':
            #    team = "LA"
            stats_dict[team] = {
                                    'solo tackles': row[2].text.strip(),
                                    'assisted tackles': row[3].text.strip(),
                                    'combined_tackles': row[4].text.strip(),
                                    'ints': row[5].text.strip(),
                                    'int_yards': row[6].text.strip(),
                                    'int_td': row[7].text.strip(),
                                    'fumble_forced': row[8].text.strip(),
                                    'fumble_recovered': row[9].text.strip(),
                                    'fumble_td': row[10].text.strip(),
                                    'sacks': row[11].text.strip(),
                                    'passed_defensed': row[12].text.strip(),
            }

        return JsonResponse(stats_dict, status=200)


class TeamOppStatsView(APIView):
    '''takes a request and returns json'''
    def get(self, request, nfl_abbr):
        start = datetime.datetime.now()
        print (nfl_abbr)
        team = Teams.objects.get(nfl_abbr=nfl_abbr)
        stats_dict = {}
        html = urllib.request.urlopen("https://www.cbssports.com/nfl/stats/team/opponent/total/nfl/regular/")

        soup = BeautifulSoup(html, 'html.parser')

        teams = soup.find('div', {'id': 'TableBase'})
        stats = teams.find_all('tr', {'class': 'TableBase-bodyTr'})

        for data in stats:
            row = data.find_all('td')
            team = row[0].a['href'].split('/')[3]
            #if team == 'LAR':
            #    team = "LA"
            # gp = row[1].text.strip()
            # yards = row[2].text.strip()
            # yards_per_game = row[3].text .strip()
            # pass_yards = row[4].text.strip()
            # pass_yards_per_game = row[5].text.strip()
            # rush_yards = row[6].text.strip()
            # rush_yards_per_game = row[7].text.strip()
            # points = row[8].text.strip()
            #points_ = row[9].text.strip()
            print (team, row[9].text.strip())
            stats_dict[team] = {
                                    'points_against': row[9].text.strip(), 
            }

        return JsonResponse(stats_dict, status=200)




## helper functions

def calc_scores(picks, stats, game):
    '''takes 2 dicts and returns a dict of scores'''

    score_dict = {}
    for user in picks.keys():
        score_dict[user] = {}
 
    total_points_diff = min(abs(v['total_points_scored'] - stats['total_points']) for v in picks.values())
    total_points_winners = [k for k, v in picks.items() if abs(v['total_points_scored'] - stats['total_points']) == total_points_diff]
    total_points_losers = [k for k, v in picks.items() if abs(v['total_points_scored'] - stats['total_points']) != total_points_diff]
    for winner in total_points_winners:
        score_dict[winner].update({'total_points_scored': round(1/len(total_points_winners), 2)})
    for loser in total_points_losers:
        score_dict[loser].update({'total_points_scored': 0})
    
    fg_points_diff = min(abs(v['points_on_fg'] - stats['points_on_fg']) for v in picks.values())
    fg_points_winners = [k for k, v in picks.items() if abs(v['points_on_fg'] - stats['points_on_fg']) == fg_points_diff]
    fg_points_losers = [k for k, v in picks.items() if abs(v['points_on_fg'] - stats['points_on_fg']) != fg_points_diff]
    for winner in fg_points_winners:
        score_dict[winner].update({'points_on_fg': round(1/len(fg_points_winners), 2)})
    for loser in fg_points_losers:
        score_dict[loser].update({'points_on_fg': 0})

    takeaways_diff = min(abs(v['takeaways'] - stats['takeaways']) for v in picks.values())
    takeaways_winners = [k for k, v in picks.items() if abs(v['takeaways'] - stats['takeaways']) == takeaways_diff]
    takeaways_losers = [k for k, v in picks.items() if abs(v['takeaways'] - stats['takeaways']) != takeaways_diff]
    for winner in takeaways_winners:
        score_dict[winner].update({'takeaways': round(1/len(takeaways_winners), 2)})
    for loser in takeaways_losers:
        score_dict[loser].update({'takeaways': 0})

    sacks_diff = min(abs(v['sacks'] - stats['sacks']) for v in picks.values())
    sacks_winners = [k for k, v in picks.items() if abs(v['sacks'] - stats['sacks']) == sacks_diff]
    sacks_losers = [k for k, v in picks.items() if abs(v['sacks'] - stats['sacks']) != sacks_diff]
    for winner in sacks_winners:
        score_dict[winner].update({'sacks': round(1/len(sacks_winners), 2)})
    for loser in sacks_losers:
        score_dict[loser].update({'sacks': 0})


    d_td_diff = min(abs(v['def_special_teams_tds'] - stats['def_special_teams_tds']) for v in picks.values())
    d_td_winners = [k for k, v in picks.items() if abs(v['def_special_teams_tds'] - stats['def_special_teams_tds']) == d_td_diff]
    d_td_losers = [k for k, v in picks.items() if abs(v['def_special_teams_tds'] - stats['def_special_teams_tds']) != d_td_diff]
    for winner in d_td_winners:
        score_dict[winner].update({'def_special_teams_tds': round(1/len(d_td_winners), 2)})
    for loser in d_td_losers:
        score_dict[loser].update({'def_special_teams_tds': 0})


    home_runner_diff = min(abs(v['home_runner'] - stats['home_runner']) for v in picks.values())
    home_runner_winners = [k for k, v in picks.items() if abs(v['home_runner'] - stats['home_runner']) == home_runner_diff]
    home_runner_losers = [k for k, v in picks.items() if abs(v['home_runner'] - stats['home_runner']) != home_runner_diff]
    for winner in home_runner_winners:
        score_dict[winner].update({'home_runner': round(1/len(home_runner_winners), 2)})
    for loser in home_runner_losers:
        score_dict[loser].update({'home_runner': 0})


    home_receiver_diff = min(abs(v['home_receiver'] - stats['home_receiver']) for v in picks.values())
    home_receiver_winners = [k for k, v in picks.items() if abs(v['home_receiver'] - stats['home_receiver']) == home_receiver_diff]
    home_receiver_losers = [k for k, v in picks.items() if abs(v['home_receiver'] - stats['home_receiver']) != home_receiver_diff]
    for winner in home_receiver_winners:
        score_dict[winner].update({'home_receiver': round(1/len(home_runner_winners), 2)})
    for loser in home_receiver_losers:
        score_dict[loser].update({'home_receiver': 0})


    home_passer_rating_diff = min(abs(v['home_passer_rating'] - stats['home_passer_rating']) for v in picks.values())
    home_passer_rating_winners = [k for k, v in picks.items() if abs(v['home_passer_rating'] - stats['home_passer_rating']) == home_passer_rating_diff]
    home_passer_rating_losers = [k for k, v in picks.items() if abs(v['home_passer_rating'] - stats['home_passer_rating']) != home_passer_rating_diff]
    for winner in home_passer_rating_winners:
        score_dict[winner].update({'home_passer_rating': round(1/len(home_passer_rating_winners), 2)})
    for loser in home_passer_rating_losers:
        score_dict[loser].update({'home_passer_rating': 0})

    away_runner_diff = min(abs(v['away_runner'] - stats['away_runner']) for v in picks.values())
    away_runner_winners = [k for k, v in picks.items() if abs(v['away_runner'] - stats['away_runner']) == away_runner_diff]
    away_runner_losers = [k for k, v in picks.items() if abs(v['away_runner'] - stats['away_runner']) != away_runner_diff]
    for winner in away_runner_winners:
        score_dict[winner].update({'away_runner': round(1/len(away_runner_winners), 2)})
    for loser in away_runner_losers:
        score_dict[loser].update({'away_runner': 0})


    away_receiver_diff = min(abs(v['away_receiver'] - stats['away_receiver']) for v in picks.values())
    away_receiver_winners = [k for k, v in picks.items() if abs(v['away_receiver'] - stats['away_receiver']) == away_receiver_diff]
    away_receiver_losers = [k for k, v in picks.items() if abs(v['away_receiver'] - stats['away_receiver']) != away_receiver_diff]
    for winner in away_receiver_winners:
        score_dict[winner].update({'away_receiver': round(1/len(away_receiver_winners), 2)})
    for loser in away_receiver_losers:
        score_dict[loser].update({'away_receiver': 0})


    away_passer_rating_diff = min(abs(v['away_passer_rating'] - stats['away_passer_rating']) for v in picks.values())
    away_passer_rating_winners = [k for k, v in picks.items() if abs(v['away_passer_rating'] - stats['away_passer_rating']) == away_passer_rating_diff]
    away_passer_rating_losers = [k for k, v in picks.items() if abs(v['away_passer_rating'] - stats['away_passer_rating']) != away_passer_rating_diff]
    for winner in away_passer_rating_winners:
        score_dict[winner].update({'away_passer_rating': round(1/len(away_passer_rating_winners), 2)})
    for loser in away_passer_rating_losers:
        score_dict[loser].update({'away_passer_rating': 0})

    winning_team =  stats['winning_team']
    print ('checking winner', stats['winning_team'])
    if winning_team == 'no winner':
        for player, p in picks.items():
            score_dict[player].update({'winning_team': 0})
            total = round(sum(score_dict[player].values()),2)
            score_dict[player].update({'player_total': total})

    else:
        winning_team_obj = Teams.objects.get(nfl_abbr=winning_team)
        
        for player, p in picks.items():
            print ('WTWETWT', p['winning_team'], winning_team)
            print (winning_team_obj.dog)
            if p['winning_team'] == winning_team and winning_team == game.dog.nfl_abbr:
                score_dict[player].update({'winning_team': 2})
            elif p['winning_team'] == winning_team and winning_team == game.fav.nfl_abbr:
                score_dict[player].update({'winning_team': 1})
            else:
                score_dict[player].update({'winning_team': 0})

            total = round(sum(score_dict[player].values()),2)
            score_dict[player].update({'player_total': total})
    
    sorted_score_dict = sorted(score_dict.items(), key=lambda v:v[1]['player_total'], reverse=True)
    print (score_dict)
    print (dict(sorted_score_dict))
    
    return dict(sorted_score_dict)
    



def calc_qb_ratings(stats):
    '''takes a dict, updates it and returns the updated dict'''
    #home_passing = stats['home']['passing']
    print ('calc qb start')
    #home_atts = max(qb['cp/att'].split('/')[1] for qb in stats['home']['passing'].values())
    #print (home_atts)
    #home_qb = [k for k,v in stats['home']['passing'].items() if v['cp/att'].split('/')[1]== home_atts]
    #d = {home_qb[0]: stats['home']['passing'].get(home_qb[0])}
    #print ('d', d)
    #print (home_qb)
    
    
    #return max(int(f['yards']) for f in self.stats.data['away']['receiving'].values())
    #print ('home qb', home_qb)

    for team, data in stats.items():
        if team in ['home', 'away']:
            for k, v in data['passing'].items():
                print (k, v)
            #max_atts = max(qb['cp/att'].split('/')[1] for qb in stats[team]['passing'].values())
            #qb = [k for k,v in stats[team]['passing'].items() if v['cp/att'].split('/')[1]== max_atts]  #getting the data for the QB with most attempts
            #if len(qb) > 1:
            #    print ('passer rating calc issue, multiple with same # of attempts')
            #k = qb[0]
            #v = stats[team]['passing'].get(k)
                comp = int(v['cp/att'].split('/')[0])
                att = int(v['cp/att'].split('/')[1])
                if att != 0:
                    rating_a = ((comp/att) - .3) * 5
                    rating_b = ((int(v['yards'])/att) -3) *.25
                    rating_c = (int(v['tds'])/att) *20
                    rating_d = 2.375 - ((int(v['ints'])/att) *25)

                    multiplier = 10 ** 1
                    final_rating = ceil((((rating_a + rating_b + rating_c + rating_d) / 6) * 100) * multiplier) / multiplier

                    print (k, final_rating)
                    stats[team]['passing'][k].update({'rating': final_rating})

                else:
                    stats[team]['passing'][k].update({'rating': 0})
            
    #print (stats)
    return (stats)


class PlayoffLogic(TemplateView):
    template_name='fb_app/playoff_about.html'


class GetGameStatusAPI(APIView):
    
    def get(self, request, week_key):
        try:
            week = Week.objects.get(pk=week_key)
            week_started = week.started()
            espn = espn_data.ESPNData()            
            d = {}

            if week_started and not week.regular_week:
                all_started = True
            elif week_started and PickMethod.objects.filter(week=week, player__name=self.request.user, method__in=['1', '2', '4']).exists():
                all_started = True
            else:
                all_started = False
            d['all_started'] = all_started
            
            for g in Games.objects.filter(week=week):
                if not week_started or week.late_picks:
                    s = False
                elif all_started:
                    s = True
                else:
                    s = espn.started(g.eid)
                d[g.home.pk] = {'started': s, 'abbr': g.home.nfl_abbr}
                d[g.away.pk] = {'started': s, 'abbr': g.away.nfl_abbr}
                
            return Response(json.dumps(d), 200)

        except Exception as e:
            print ('get picks api issue: ', e)
            return Response(json.dumps({'msg': str(e)}), 500)


def save_access_log(request, screen):
    '''takes a request and a string saves an object and returns nothing'''
    try:
        if request.user.is_authenticated:
            log, created = AccessLog.objects.get_or_create(week=Week.objects.get(current=True), user=request.user, page=screen, device_type=request.user_agent)
            log.views += 1
            log.save()
    except Exception as e:
        print ('save access log issue: ', e)
    return


class Setup(LoginRequiredMixin, TemplateView):
    template_name = 'fb_app/setup.html'

    def get_context_data(self, **kwargs):
        context = super(Setup, self).get_context_data(**kwargs)
        #player = Player.objects.get(name=self.request.user)
        weeks = Week.objects.filter(season_model__current=True)

        context.update(
                {'weeks': weeks})
        return context

    def post(self, request, **kwargs):
        from fb_app import load_espn_sched
        print (request.POST)
        espn = {}
        nfl_season_type=request.POST.get('nfl_season_type')
        if request.POST.get('payload') and request.POST.get('current'):
            error = 'Enter a max week or select checkbox for current week'
        elif request.POST.get('payload'):
            espn = load_espn_sched.load_sched(payload=request.POST.get('payload'), nfl_season_type=nfl_season_type)
            error = "PAYLOaD"
            
        elif request.POST.get('current'):
            error = 'CURRENT '
            espn = load_espn_sched.load_sched(nfl_season_type=nfl_season_type)
        else:
            error = 'Unknown input'
        weeks = Week.objects.filter(season_model__current=True)

        print ('setup summary: ', espn)
        return render (request, 'fb_app/setup.html', {
            'form': request.POST,
            'error': error,
            'weeks': weeks,
        }
        )


class RollWeekAPI(APIView):
    
    def get(self, request):
        print ('Rolling Week API')
        start = datetime.datetime.now()
        try:    
            d = {}
            week = Week.objects.get(current=True)

            if week.games_complete():
                if Week.objects.filter(season_model__current=True, week=week.week + 1).exists():
                    week.current = False
                    new_current = Week.objects.get(season_model__current=True, week=week.week + 1)
                    new_current.current = True
                    week.save()
                    new_current.save()
                    d.update({'success': {'current_week': new_current.week, 'current': new_current.current}})
                else:
                    d.update({'no_next_week':  {'current_week': week.week, 'current': week.current}})

            else:
                d.update({'games_not_complete':  {'current_week': week.week, 'current': week.current}})

        except Exception as e:
            print ('get picks api issue: ', e)
            d.update({'error': {'msg': str(e)}})
        
        d['duration'] = str(datetime.datetime.now() - start)
        return Response(json.dumps(d), 200)


class PickAllGames(LoginRequiredMixin, TemplateView):
    template_name = 'fb_app/all_games_form.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        start = datetime.datetime.now()
        context = super(PickAllGames, self).get_context_data(**kwargs)
        player = Player.objects.get(name=self.request.user)
        season = Season.objects.get(current=True)
        
        if SeasonPicks.objects.filter(player=player, season=season).exists():
            games = SeasonPicks.objects.filter(player=player, season=season)
            mode = 'update'
        else:
            games = Games.objects.filter(week__season_model=season)
            mode = 'new'
        
        print ('MODE: ', mode)
        print ('GAMES len : ', len(games))
        context.update(
                {'games': games,
                'mode': mode,
                'season': season,
                'last_season': Season.objects.get(season=str(int(season.season)-1)),
                'player': player,
                })

        print ('ALL PICKS DUR: ', datetime.datetime.now() - start)
        return context

    def post(self, request, **kwargs):
        print (request.POST)
        start = datetime.datetime.now()        
        season = Season.objects.get(current=True)
        player = Player.objects.get(name=self.request.user)

        if SeasonPicks.objects.filter(player=player, season=season).exists():
            SeasonPicks.objects.filter(player=player, season=season).delete()

        if request.POST.get('favs'):
            last_season = Season.objects.get(season=str(int(season.season)-1))
            stats = {}
            for team in Teams.objects.all():
                stats[team] = team.get_record(last_season)

            print (player, ' : ', 'picking favs')
            for g in Games.objects.filter(week__season=season):
                p = SeasonPicks()
                p.player = player
                p.season = season
                p.game = g
                if stats.get(g.home)[0] > stats.get(g.away)[0]:
                    p.pick = g.home
                elif stats.get(g.away)[0] > stats.get(g.home)[0]:
                    p.pick = g.away
                else:
                    p.pick = g.home
                p.save()
        else:
            for k,v in request.POST.items():
                if k != 'csrfmiddlewaretoken':
                    if SeasonPicks.objects.filter(player=player, season=season, game=Games.objects.get(pk=k)).exists():
                        p = SeasonPicks.objects.get(player=player, season=season, game=Games.objects.get(pk=k))
                    else:
                        p = SeasonPicks()
                        p.game = Games.objects.get(pk=k)
                        p.season = season
                        p.player = player
                    
                    p.pick = Teams.objects.get(pk=v)
                    p.save()
        
        #mode = 'update'
        #error = 'Picks Submitted'
        print ('season picks submitted: ', player, 'Dur: ', datetime.datetime.now() - start)
        return redirect('/fb_app/all_games_confirm')
        # return render (request, self.template_name, {
        #     #'form': request.POST,
        #     'games': SeasonPicks.objects.filter(player=player, season=season),
        #     'error': error,
        #     'season': season,
           
        # }
        #)


class PickAllGamesConfirm(LoginRequiredMixin, TemplateView):
    template_name= 'fb_app/all_games_confirm.html'
    login_url = '/login'
    
    def get_context_data(self, **kwargs):
        start = datetime.datetime.now()
        context = super(PickAllGamesConfirm, self).get_context_data(**kwargs)
        player = Player.objects.get(name=self.request.user)
        
        sp = player.season_picks_summary()

        context.update(
                {'sp': sp,
                'season': Season.objects.get(current=True)
                })

        print ('ALL PICKS DUR: ', datetime.datetime.now() - start)
        return context


class GetRecordsAPI(APIView):
    
    def get(self, request):

        start = datetime.datetime.now()
        try:    
            d = {}
            c_season = Season.objects.get(current=True)
            season = Season.objects.get(season=str(int(c_season.season)-1))

            for t in Teams.objects.all():
                d[t.pk] = {'record': t.get_record(season),
                            'nfl_abbr': t.nfl_abbr,
                            'team_pk': t.pk}

        except Exception as e:
            print ('get records api issue: ', e)
            d.update({'error': {'msg': str(e)}})
        
        #d['duration'] = str(datetime.datetime.now() - start)
        return Response(json.dumps(d), 200)


def email_picks(user):
    '''takes a list of email addresses, returns nothing'''
    from django.template.loader import get_template



    from django.conf import settings
    from django.template.loader import render_to_string
    from django.template import Template, Context

    start = datetime.datetime.now()
    #req = HttpRequest()
    u = {'user': user}
    context = PicksEmail().get_context_data(**u)
    
    dir = settings.BASE_DIR + '/fb_app/templates/fb_app/'
    #msg_plain = render_to_string(dir + 'email.txt', {'appt': appt})
    msg = render_to_string(dir + 'email_picks.html', context)
    #msg = EmailMessage(msg_html)
    
    t = Template(dir + 'email_picks.html')
    c = Context(context)
    #html =  t.render(c)
    req = HttpRequest()
    #print (render(req, dir + 'fedex_summary.html', context, content_type='application/xhtml+xml').__dict__)    
    print ('sending FB picks email', user)
    
    #print(msg)
    send_mail("Weekly Football Picks ",
    from_email = "jflynn87g.gmail.com",
    #recipient_list = ['jflynn87@hotmail.com','jrc7825@gmail.com', 'ryosuke.aoki0406@gmail.com'],
    #recipient_list = ['jflynn87@hotmail.com',],
    recipient_list = [user.email, ],
    message = msg,
    html_message=msg
     )

    return



class PicksEmail(TemplateView):
    template_name = 'fb_app/email_picks.html'

    def get_context_data(self, **kwargs):
        start = datetime.datetime.now()
        context = super(PicksEmail, self).get_context_data(**kwargs)
        week = Week.objects.get(season_model__current=True, current=True)
        print ('kwargs ', kwargs, kwargs.get('user'), type(kwargs), kwargs.keys())
        if kwargs:
            user = kwargs.get('user')
        else:
            user = self.request.user
        
        print (user, type(user))
        picks = {}

        for p in Picks.objects.filter(player__name=user, week=week).order_by('-pick_num'):
            picks[p.pick_num] = {'pick': p,
                                'game': Games.objects.get(Q(week=week), (Q(home=p.team) | (Q(away= p.team)))) 
                                }

        context.update({
                    'picks': picks,
                    'week': week,
                    'user': user
        })

        return context
    

class AllGamesScore(LoginRequiredMixin, TemplateView):
    template_name= 'fb_app/all_games_score.html'
    login_url = 'login'
    
    def get_context_data(self, **kwargs):
        start = datetime.datetime.now()
        context = super(AllGamesScore, self).get_context_data(**kwargs)
        d = {}
        for p in Player.objects.filter(league__league='Golfers'):
            if SeasonPicks.objects.filter(player=p, season__current=True).exists():
                d.update(p.season_picks_record())

        context.update(
                {'record': d,
                'season': Season.objects.get(current=True)
                })

        print ('SP PICKS SCORE DUR: ', datetime.datetime.now() - start)
        return context


class SPDetailsAPI(APIView):
     def get(self, request, player):

        start = datetime.datetime.now()
        try:  
            d = {}
            d[player] = {}
            p = Player.objects.get(name__username=player)
            for week in Week.objects.filter(season_model__current=True):
                d.get(player).update({'week' + str(week.week): p.season_picks_week_wins(week)}) 
                print (d)
        except Exception as e:
            print ('SPDetailsAPI error: ', e)

        return Response(json.dumps(d), 200)