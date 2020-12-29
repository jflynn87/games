from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView, View, DetailView, UpdateView
import urllib.request
from fb_app.models import Games, Week, Picks, Player, League, Teams, WeekScore, Season, PickPerformance
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
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
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from fb_app import scrape_cbs
from django.core import serializers
from bs4 import BeautifulSoup
import pytz
from django.utils import dateformat





# Create your views here.

class GetSpreads(generics.ListAPIView):


    def get(self, request, **kwargs):

            try:
                #print ('kwargs', request.Request)
                print ('kwargs1', self.kwargs)
                html = urllib.request.urlopen("https://nypost.com/odds/")
                soup = BeautifulSoup(html, 'html.parser')
                nfl_sect = (soup.find("div", {'class':'odds__table-outer--1'}))
                games_dict = []
                
                #week = Week.objects.get(current=True)
                week = Week.objects.get(pk=self.kwargs.get('pk'))
                print ('spreads weeek: ', week)

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

                        if Games.objects.filter(Q(week=week) & Q(home=fav_obj) & Q(away=dog_obj)).exists():
                            game = Games.objects.get(Q(week=week) & Q(home=fav_obj) & Q(away=dog_obj))
                            game.fav=fav_obj
                            game.dog=dog_obj
                            game.spread=spread
                            game.save()
                            games_dict.append((game.eid, game.fav.nfl_abbr, str(game.fav.get_record()), game.dog.nfl_abbr.lower(), str(game.dog.get_record()), spread))

                        elif Games.objects.filter(Q(week=week) & Q(home=dog_obj) & Q(away=fav_obj)).exists():
                            game = Games.objects.get(Q(week=week) & Q(home=dog_obj) & Q(away=fav_obj))
                            game.fav=fav_obj
                            game.dog=dog_obj
                            game.spread=spread
                            game.save()
                            games_dict.append((game.eid, game.fav.nfl_abbr.lower(), str(fav_obj.get_record()), game.dog.nfl_abbr, str(dog_obj.get_record()), spread))
                        else:
                            print ('game not found:', fav, dog)
                        
                    except Exception as e:
                        print ('spread look up error', e, game, fav, dog)
                        #return Response({'msg': e}, 404)
                #print (games_dict)
                data = json.dumps(games_dict)
                return Response(data, 200)
            except Exception as ex:
                print ('get spreads error: ', ex)
                return Response ({'msgs':ex}, 500)


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
        #week = Week.objects.get(current=True)
#        if self.kwargs.get('pk') != None:
#            print ('kwargs driving week')
#            week= Week.objects.get(pk=self.kwargs.get('pk'))
#        else:
#            print ('getting current week games')
#            week = Week.objects.get(current=True)
        week = self.get_week()
        player=Player.objects.get(name=self.request.user)
        #not adjusting game cnt as expect postponed only after picks done
        PickFormSet = modelformset_factory(Picks, form=CreatePicksForm, max_num=(week.game_cnt))
        NoPickFormSet = modelformset_factory(Picks, form=CreatePicksForm, extra=(week.game_cnt))

#        try:
#            print ('skipping preads')
#            #get_spreads()
#        except Exception:
#            print ('no spreads available')
        #games=Games.objects.filter(week=week).order_by("eid")
        games=Games.objects.filter(week=week).order_by("game_time")
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
            #'week': Week.objects.filter(season_model__current=True, week__gte=week.week),
            'games_list': games,
            'form': form,
            'teams': team_dict
            })
        else:
            context.update({
            'week': week,
            #'week': Week.objects.filter(season_model__current=True, week__gte=week.week),
            'games_list': games,
            'form': form,
            'teams': team_dict
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
         if request.POST.get('favs') == 'favs':
            sorted_spreads = sorted(week.get_spreads().items(), key=lambda x: x[1][2], reverse=True)
            #print ('sspreads', sorted_spreads)
            #list of tuples returned by sort, use tuple to find fav
            for g in sorted_spreads:
                pick_list.append(g[1][0])
            print ('picking favs', pick_list)
         else:
            PickFormSet = modelformset_factory(Picks, form=CreatePicksForm, max_num=(week.game_cnt))
            formset = PickFormSet(request.POST, form_kwargs={'week': week})

            if formset.is_valid():
                #print ('valid')
                
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



class AllTime(TemplateView):
    template_name="fb_app/all_time.html"

def ajax_get_games(request, week):
    #print ('in getting gamesS')
    if request.is_ajax():
       # print (request)
        games = Games.objects.filter(week__week='3')
        data = json.dumps(games)
        return HttpResponse(data, content_type="application/json")
    else:
        print ('not ajax')
        raise Http404


class UpdateScores(APIView):
    
    def get(self, num):
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
           if games == None:
               games = scrape_cbs.ScrapeCBS(week).get_data()
           d = {'player-data': week.get_scores(league)}
           display = {**d, **games}
           data = json.dumps(display)
        else:
            data = json.dumps({'msg': 'week not started'})
        
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
        print (self.kwargs)
        week = Week.objects.get(pk=self.kwargs.get('pk'))
    
        base_data = self.get_base_data()

        user = base_data[0]
        player = base_data[1]
        league = base_data[2]

        if week.picks_complete(league) or league.league == 'Football Fools':
            print ('picks complete')
        else:
            if week.started():
                for player in Player.objects.filter(league=league):
                    if Picks.objects.filter(player=player, week=week, player__active=True).count() < 1:
                        player.submit_default_picks(week)
        
        if league.ties_lose:
            #print ('ties lose')
            game_cnt = Games.objects.filter(week=week).exclude(postponed=True).count()
        else:
            game_cnt = week.game_cnt              


        print ('game count: ', game_cnt)
        if week.started():
        
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
            'game_cnt': game_cnt
            })

            print ('*******finished context: ', datetime.datetime.now() - start)
            
            return context
        else:
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
            
            context.update ({'players': picks_submitted,
                        #'picks': pick_dict,
                        'week': week,
                        'pending': picks_pending,
                        'league': league, 
                        
                        #'games': Games.objects.filter(week=week).order_by('eid'),
                             })
            return context


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



class UpdateProj(APIView):
    
    def get(self, num):
        try:
            #print (self.request.GET.getlist('winners[]'))

            w = Week.objects.get(week=self.request.GET.get('week'), season_model__current=True)
            l = League.objects.get(league=self.request.GET.get('league'))
            proj_dict = {}

            for player in Player.objects.filter(league=l, active=True):
                proj_score = 0
                for pick in Picks.objects.filter(player=player, week=w):
                    if  Games.objects.filter(Q(home=pick.team) | Q(away=pick.team), week=w, postponed=False).exists():
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
                    'loser': pick.is_loser()}})
            except Exception as e:
                data[pick.pick_num] = {str(pick.player.name.username): 
                    {'team': pick.team.nfl_abbr, 
                    'loser': pick.is_loser()}}
                
        return Response(json.dumps(data), 200)


class FBLeaderboard(APIView):
    def get(self, request):

        try:
            data = {}
            player = Player.objects.get(name=request.user)
            
            #league = League.objects.get(league=player.league)
            ranks = player.league.season_ranks()
            
            for p in Player.objects.filter(league=player.league):
                
                data[p.name.username] = {'score': p.season_total(),
                                            'rank': ranks[p.name.username],
                                            'behind': p.season_points_behind()
                                        }
            #sorted_data = {k: v for k, v in sorted(data.items(), key=lambda item: item[1][1])}
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


class GetTeamResults(APIView):
    def get(self, request, nfl_abbr):
        print (request.GET, 'nfl: ', nfl_abbr)
        try:
            data = {}
            player = Player.objects.get(name=request.user)
            stats = PickPerformance.objects.get(season__current=True, league=player.league)

            return JsonResponse({'response': stats.team_results(nfl_abbr)}, status=200)
            #print (sorted_data)
        except Exception as e:
            print ('GetTeamsResul error: ', e)
            
            return JsonResponse({'response': {'error': str(e)}}, status=400)


class AllTeamResults(APIView):
    def get(self, request, player_key):
        try:
            player = Player.objects.get(name__pk=player_key)
            stats = PickPerformance.objects.get(season__current=True, league=player.league)
            player_stats = json.loads(stats.data)[player.name.username]

            league_data = stats.all_team_results()
            player_data = [{k: {'wrong': d['wrong'], 'right': d['right'], 'win_percent': "{:.0%}".format(round(int(d['right'])/(int(d['right'])+int(d['wrong'])),2))} for k, d in player_stats.items()}]
            print (type(player_data), len(player_data), player_data)
            sorted_player_data = {k: v for k, v in sorted(player_data[0].items(), key=lambda item: item[1]['win_percent'])}
            print (sorted_player_data)
            data = {
                'player_data': sorted_player_data,
                'league_data': league_data
            }
            return JsonResponse({'response': data}, status=200)
        except Exception as e:
            print ('AllTeamsResults error: ', e)
            
            return JsonResponse({'respoonse': {'error': str(e)}}, status=400)





# class GetGames(APIView):
    
#     def post(self, request):
#         try:
#             print ('get games', request.data)
#             games = {}
#             week = Week.objects.get(week=request.data['week_key'], season_model__current=True)

#             for game in Games.objects.filter(week=week).order_by('game_time'):
                
                
#                 est = pytz.timezone('US/Eastern')
#                 kick_off = game.game_time.astimezone(est)
#                 dow = kick_off.strftime('%a')
#                 kick_off_display = str(dow) + ', ' + dateformat.TimeFormat(kick_off).P() 

#                 games[game.eid] = {#'time': datetime.datetime.strftime(game.game_time, "%m/%d/%Y, %H"),
#                                    'time': kick_off_display,
#                                    'home': game.home.nfl_abbr,
#                                    'home_record': game.home.get_record(),
#                                    'away': game.away.nfl_abbr.lower(),
#                                    'away_record': game.away.get_record(),
#                                    'spread': game.spread
#                     }

#             print ('getWeeks', games)
#             return Response(json.dumps(games), 200)
#             #return Response(json.dumps(score_dict), 200)

#         except Exception as e:
#             print ('get games api issue: ', e)
#             return Response(json.dumps({'msg': e}), 200)


# def format_time(time):
#         """
#         Copied from django code repoitory, utils/dateformat.py
#         Time, in 12-hour hours, minutes and 'a.m.'/'p.m.', with minutes left off
#         if they're zero and the strings 'midnight' and 'noon' if appropriate.
#         Examples: '1 a.m.', '1:30 p.m.', 'midnight', 'noon', '12:30 p.m.'
#         Proprietary extension.
#         """
#         if time.minute == 0 and time.hour == 0:
#             return _('midnight')
#         if time.minute == 0 and time.hour == 12:
#             return _('noon')
#         return '%s %s' % (time.f(), time.a())