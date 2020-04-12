from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, TemplateView, ListView, DetailView, CreateView, UpdateView, FormView
from golf_app.models import Field, Tournament, Picks, Group, TotalScore, ScoreDetails, \
           mpScores, BonusDetails, PickMethod, PGAWebScores
from golf_app.forms import  CreateManualScoresForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateResponseMixin
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
import datetime
from golf_app import populateField, calc_score, optimal_picks,\
     manual_score, scrape_scores
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Min, Q, Count, Sum, Max
import scipy.stats as ss
from django.http import JsonResponse
import json
import random
from django.db import transaction
import urllib.request
from selenium.webdriver import Chrome
import csv
from rest_framework.views import APIView
from rest_framework.response import Response



class FieldListView(LoginRequiredMixin,ListView):
    login_url = 'login'
    template_name = 'golf_app/field_list.html'
    model = Field
    #redirect_field_name = 'next'

    def get_context_data(self,**kwargs):
        context = super(FieldListView, self).get_context_data(**kwargs)
        tournament = Tournament.objects.get(current=True)
        print (tournament.started())
        #check for withdrawls and create msg if there is any
        try:
            score_file = calc_score.getRanks({'pk': tournament.pk})
            wd_list = []
            print ('score file', score_file[0])
            if score_file[0] == "score lookup fail":
                wd_list = []
                error_message = ''
            else:
                for golfer in Field.objects.filter(tournament=tournament):
                    if golfer.playerName not in score_file[0]:
                        print ('debug')
                        wd_list.append(golfer.playerName)
                        #print ('wd list', wd_list)
                if len(wd_list) > 0:
                    error_message = 'The following golfers have withdrawn:' + str(wd_list)
                    for wd in wd_list:
                        Field.objects.filter(tournament=tournament, playerName=wd).update(withdrawn=True)
                else:
                    error_message = None
        except Exception as e:
            print ('score file lookup issue', e)
            error_message = None

        context.update({
        'field_list': Field.objects.filter(tournament=Tournament.objects.get(current=True)),
        'tournament': tournament,
        'error_message': error_message
        })
        return context

    @transaction.atomic
    def post(self, request):
        tournament = Tournament.objects.get(current=True)
        group = Group.objects.filter(tournament=tournament)
        user = User.objects.get(username=request.user)
        print ('user', user)

        random_picks = []
        picks_list = []
        print ('started', tournament.started())
        if tournament.started() and tournament.late_picks is False:
            print ('picks too late', user, datetime.datetime.now())
            print (timezone.now())
            return HttpResponse ("Sorry it is too late to submit picks.")

        if request.POST.get('random') == 'random':
            for g in group:
                random_picks.append(random.choice(Field.objects.filter(tournament=tournament, group=g, withdrawn=False)))
            print ('random picks', random_picks)
        else:
            form = request.POST
            picks = []
            for key, pick in form.items():
                if key not in  ('csrfmiddlewaretoken', 'userid'):
                    picks_list.append(pick)
            print (picks_list)

        if Picks.objects.filter(playerName__tournament__current=True, user=user).count()>0:
            Picks.objects.filter(playerName__tournament__current=True, user=user).delete()

        if request.POST.get('random'):
            save_picks(user, tournament, random_picks)
            pm = PickMethod()
            pm.user = user
            pm.tournament = tournament
            pm.method = '2'
            pm.save()
        else:
            print (len(form), len(group))
            if (len(form)-2) == len(group):
                pick_list = []
                for k, v in form.items():
                   if k != 'csrfmiddlewaretoken' and k!= 'userid':
                       pick_list.append(Field.objects.get(pk=v))
                save_picks(user, tournament, pick_list)
                pm = PickMethod()
                pm.user = user
                pm.tournament = tournament
                pm.method = '1'
                pm.save()
            else:
                group_list = []
                for key, value in form.items():
                    if key not in ('userid', 'csrfmiddlewaretoken'):
                        group_list.append(key.split('-')[0])
                missing_group = []
                for num in group:
                    if str(num.number) not in group_list:
                        missing_group.append(num.number)
                print (request.user, 'picks missing group', missing_group)

                print (datetime.datetime.now(), request.user, form)
                return render (request, 'golf_app/field_list.html',
                    {'field_list': Field.objects.filter(tournament=tournament),
                     #'picks_list': Picks.objects.filter(playerName__tournament__current=True, user=form['userid']),
                     'form':form,
                     'picks': picks,
                     'tournament': Tournament.objects.get(current=True),
                     'error_message':  "Missing Picks for the following groups: " + str(missing_group),
                         })

        print ('submitting picks', datetime.datetime.now(), request.user, picks_list, 'random:', random_picks)
        return redirect('golf_app:picks_list')

def save_picks(user, tournament, pick_list):
    '''takes user obj, tournament obj and pick list and saves picks as well as sets up score detail and Bonus
    details for the tournament'''

    for picks in pick_list:
        pick = Picks()
        pick.user = user
        pick.playerName = Field.objects.get(playerName=picks, tournament=tournament)
        pick.save()
        sd = ScoreDetails()
        sd.user = user
        sd.pick = pick
        sd.save()

    bd, created = BonusDetails.objects.get_or_create(tournament = tournament, \
    user = user, winner_bonus = 0, cut_bonus = 0)
    bd.save()

    return


def get_picks(request):
    if request.is_ajax():
        print (request.user)
        pick_list = []
        for pick in Picks.objects.filter(user__username=request.user, playerName__tournament__current=True):
            pick_list.append(pick.playerName.pk)
        data = json.dumps(pick_list)
        return HttpResponse(data, content_type="application/json")
    else:
        print ('not ajax')
        raise Http404


class PicksListView(LoginRequiredMixin,ListView):
    login_url = 'login'
    redirect_field_name = 'golf_app/pick_list.html'
    model = Picks

    def get_context_data(self,**kwargs):
        context = super(PicksListView, self).get_context_data(**kwargs)
        context.update({
        #'field_list': Field.group,
        'tournament': Tournament.objects.get(current=True),
        'picks_list': Picks.objects.filter(playerName__tournament__current=True,user=self.request.user),
        })
        return context


class ScoreListView(DetailView):
    template_name = 'golf_app/scores.html'
    model=TotalScore

    def dispatch(self, request, *args, **kwargs):
        print ('in SLV dispatch')
        if kwargs.get('pk') == None:
            tournament = Tournament.objects.get(current=True)
            self.kwargs['pk'] = str(tournament.pk)
        return super(ScoreListView, self).dispatch(request, *args, **kwargs)
    
    
    def get_context_data(self, **kwargs):
        context = super(ScoreListView, self).get_context_data(**kwargs)
        tournament = Tournament.objects.get(pk=self.kwargs.get('pk'))
        
        if not tournament.started():
           user_dict = {}
           for user in Picks.objects.filter(playerName__tournament=tournament).values('user__username').annotate(Count('playerName')):
               user_dict[user.get('user__username')]=user.get('playerName__count')
               if tournament.pga_tournament_num == '470': #special logic for match player
                  scores = (None, None, None, None,None)
               #else:  scores=calc_score.calc_score(self.kwargs, request)
           self.template_name = 'golf_app/pre_start.html'

           context.update({'user_dict': user_dict,
                           'tournament': tournament,
                          # 'lookup_errors': scores[4],
                                                    })

           return context
        ## from here all logic should only happen if tournament has started

        if not tournament.picks_complete():
               tournament.missing_picks()

        if tournament.manual_score_file:
           score_dict = {}
           file = str(tournament.name) + ' score.csv'
           with open(file, encoding="utf8") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    try:
                        name = row[3].split('(')[0].split(',')[0]
                        #print (name, len(name), name[len(name)-1])
                        if name != '':
                           if name[-1] == ' ':
                              score_dict[name[:-1]] = {'total': row[0], 'status': row[5], 'score': row[4], 'r1': row[7], 'r2': row[8], 'r3': row[9], 'r4': row[10]}
                           else:
                              score_dict[name] = {'total': row[0], 'status': row[5], 'score': row[4], 'r1': row[7], 'r2': row[8], 'r3': row[9], 'r4': row[10]}
                        else:
                            print ('round.csv file == psace', row)
                    except Exception as e:
                        print ('round.csv file read failed', row, e)

                picks = manual_score.Score(score_dict, tournament)
                picks.update_scores()
                picks.total_scores()
                context.update({'scores':TotalScore.objects.filter(tournament=tournament).order_by('score'),
                                'detail_list':picks.get_picks_by_user(),
                                'leader_list':picks.get_leader(),
                                'cut_data':None,
                                'lookup_errors': None,
                                'tournament': tournament,
                                'thru_list': [],
    #                                     'optimal_picks': summary_data[0],
    #                                     'best_score': summary_data[1],
    #                                     'cuts': {'1': 'data', '2': 'data'}
                                         })

                return context

        else:
            try:
                json_url = tournament.score_json_url
                with urllib.request.urlopen(json_url) as field_json_url:
                     data = json.loads(field_json_url.read().decode())
                print ('found pga JSON!')
            except Exception as e:
                print ('cant open pga score file', e)
                #run batch to update pgawebscore table
                score_dict = {}
                #for s in PGAWebScores.objects.filter(tournament=tournament):
                #    score_dict[s.golfer.playerName] = \
                #    {'total': s.total, 'status': s.status, 'score': s.score, 'r1': s.r1, 'r2': s.r2, 'r3': s.r3, 'r4': s.r4}

                picks = manual_score.Score(score_dict, tournament)
                picks.update_scores()
                picks.total_scores()
                context.update({'scores':TotalScore.objects.filter(tournament=tournament).order_by('score'),
                                'detail_list':picks.get_picks_by_user(),
                                'leader_list':picks.get_leader(),
                                'cut_data':None,
                                'lookup_errors': None,
                                'tournament': tournament,
                                'thru_list': [],
    #                                     'optimal_picks': summary_data[0],
    #                                     'best_score': summary_data[1],
    #                                     'cuts': {'1': 'data', '2': 'data'}
                                         })

                return context        


@transaction.atomic
def create_picks(tournament, user):
    '''takes tournament and user objects and generates random picks.  check for duplication with general pick submit class'''

    for group in Group.objects.filter(tournament=tournament):
        pick = Picks()
        random_picks = random.choice(Field.objects.filter(tournament=tournament, group=group, withdrawn=False))
        pick.playerName = Field.objects.get(playerName=random_picks.playerName, tournament=tournament)
        pick.user = user
        pick.save()

    pm = PickMethod()
    pm.user = user
    pm.tournament = tournament
    pm.method = '3'
    pm.save()

    return



class SeasonTotalView(ListView):
    template_name="golf_app/season_total.html"
    model=Tournament

    def get_context_data(self, **kwargs):
        display_dict = {}
        user_list = []
        winner_dict = {}
        winner_list = []
        total_scores = {}
        second_half_scores = {}
        mark_date = datetime.datetime.strptime('2019-3-20', '%Y-%m-%d')

        for user in TotalScore.objects.values('user_id').distinct().order_by('user_id'):
            user_key = user.get('user_id')
            user_list.append(User.objects.get(pk=user_key))
            winner_dict[User.objects.get(pk=user_key)]=0
            total_scores[User.objects.get(pk=user_key)]=0
            #added second half for Mark
            second_half_scores[User.objects.get(pk=user_key)]=0

        for user in TotalScore.objects.values('user').distinct().order_by('user_id'):
            winner_dict[(User.objects.get(pk=user.get('user')))]=0

        for tournament in Tournament.objects.filter(season__current=True).order_by('-start_date'):
            score_list = []
            #second_half_score_list = []  #added for Mark
            for score in TotalScore.objects.filter(tournament=tournament).order_by('user_id'):
                score_list.append(score)
                total_score = total_scores.get(score.user)
                total_scores[score.user] = total_score + score.score
                #add second half for Mark
                if tournament.start_date > mark_date.date():
                    #second_half_score_list.append(score)
                    second_half_score = second_half_scores.get(score.user)
                    second_half_scores[score.user] = second_half_score + score.score

            if tournament.complete:
                print ('add new logic')
                
                for winner in tournament.winner():
                    score_list.append(winner.user)
                    
                    if tournament.major:
                        winner_dict[winner.user] = winner_dict.get(winner.user) + 50/tournament.num_of_winners()
                    else:
                        winner_dict[winner.user] = winner_dict.get(winner.user) + 30/tournament.num_of_winners()

                # winner = TotalScore.objects.filter(tournament=tournament).order_by('score').values('score')
                # winning_score = winner[0].get('score')
                # #winning_score = winner[0].score
                # num_of_winners = winner.filter(score=winning_score, tournament=tournament).count()
                # win_user_list = []
                # if num_of_winners == 1:
                #     winner_data = ([TotalScore.objects.get(tournament=tournament, score=winning_score)], num_of_winners)
                #     win_user_list.append(User.objects.get(pk=winner_data[0][0].user.pk))
                #     score_list.append(User.objects.get(pk=winner_data[0][0].user.pk))
                #     winner_data = (win_user_list, num_of_winners)
                #     winner_list.append(winner_data)
                # elif num_of_winners > 1:
                #     winner_data = ([TotalScore.objects.filter(tournament=tournament, score=winning_score)], num_of_winners)
                #     #win_user_list = []
                #     for user in winner_data[0]:
                #         print ('this', user)
                #         for name in user:
                #         #score_list.append(User.objects.get(pk=name.user.pk))
                #             win_user_list.append(User.objects.get(pk=name.user.pk))
                #             winner_data = (win_user_list, num_of_winners)
                #             score_list.append(User.objects.get(pk=name.user.pk))
                #         winner_list.append(winner_data)

                # else:
                #      print ('something wrong with winner lookup', 'num of winners: ', len(winner))

            display_dict[tournament] = score_list

        

        #print (winner_list)
        # for winner in winner_list:
        #     for data in winner[0]:
        #         prize = winner_dict.get(data)
        #         if tournament.major:
        #             prize = prize + (50/winner[1])
        #         else:
        #             prize = prize + (30/winner[1])
        #         winner_dict[data] = prize

        total_score_list = []
        total_second_half_score_list = []
        for score in total_scores.values():
            #print ('fh', total_score_list)
            total_score_list.append(score)
        #added for Mark
        for s in second_half_scores.values():
            #print ('sh', second_half_score_list)
            total_second_half_score_list.append(s)

        ranks = ss.rankdata(total_score_list, method='min')
        rank_list = []
        for rank in ranks:
            rank_list.append(rank)

        second_half_ranks = ss.rankdata(total_second_half_score_list, method='min')
        second_half_rank_list = []
        for rank in second_half_ranks:
            second_half_rank_list.append(rank)



        print ()
        print ('display_dict', display_dict)
        print ()
        print ('winner dict', winner_dict)
        print ('second half totals', total_second_half_score_list)
        print ('full season totals',total_score_list)

        context = super(SeasonTotalView, self).get_context_data(**kwargs)
        context.update({
        'display_dict':  display_dict,
        'user_list': user_list,
        'rank_list': rank_list,
        'totals_list': total_score_list,
        'second_half_list': total_second_half_score_list,
        'prize_list': winner_dict,
        'second_half_rank_list': second_half_rank_list,

        })
        return context


def setup(request):

    if request.method == "GET":
        if request.user.is_superuser:
            t = Tournament.objects.get(current=True)
            json_url = 'https://statdata.pgatour.com/r/current/message.json'
            #print (json_url)

            with urllib.request.urlopen(json_url) as field_json_url:
                data = json.loads(field_json_url.read().decode())

            return render(request, 'golf_app/setup.html', {'status': data,
                                                            'tournament': t})
        else:
           return HttpResponse('Not Authorized')
    if request.method == "POST":
        url_number = request.POST.get('tournament_number')
        print (url_number, type(url_number))
        try:
            if Tournament.objects.filter(pga_tournament_num=str(url_number), season__current=True).exists():
                error_msg = ("tournament already exists" + str(url_number))
                return render(request, 'golf_app/setup.html', {'error_msg': error_msg})
            else:
                print ('creating field A')
                populateField.create_groups(url_number)
                return HttpResponseRedirect(reverse('golf_app:field'))
        except ObjectDoesNotExist:
            print ('creating field')
            populateField.create_groups(url_number)
            return HttpResponseRedirect(reverse('golf_app:field'))
        except Exception as e:
            print ('error', e)
            error_msg = (e)
            return render(request, 'golf_app/setup.html', {'error_msg': error_msg})

class AboutView(TemplateView):
    template_name='golf_app/about.html'

class AllTime(TemplateView):
    template_name='golf_app/all_time.html'


class GetScores(APIView):
    
    def get(self, num):
        
        print ('GetScores API VIEW', self.request.GET.get('tournament'))
        t = Tournament.objects.get(pk=self.request.GET.get('tournament'))

        if t.current:
            print ('scraping')
            pga_web = scrape_scores.ScrapeScores(t)
            score_dict = pga_web.scrape()
        else:
            print ('not scraping')
            score_dict = get_score_dict(t)
        
        scores = manual_score.Score(score_dict, t, 'json')
        # change so this isn't executed when complete, add function to get total scores without updating
        #print (len(score_dict))
        if len(score_dict) == 0:
            print ('score_dict empty')
            return Response(({}), 200)


        
        if t.current and len(score_dict) != 0:
           scores.update_scores()
        
        ts = scores.total_scores()
        d = scores.get_picks_by_user() 
        leaders = scores.get_leader()
        optimal = scores.optimal_picks()
        print (d, ts)
        return Response(({'picks': d,
                          'totals': ts,
                          'leaders': leaders,
                          'cut_line': t.cut_score,
                          'optimal': optimal
         }), 200)

class GetDBScores(APIView):
    
    def get(self, num):
        
        print ('GetScores API VIEW', self.request.GET.get('tournament'))
        t = Tournament.objects.get(pk=self.request.GET.get('tournament'))

        #pga_web = scrape_scores.ScrapeScores(t)
        score_dict = get_score_dict(t)
        
        scores = manual_score.Score(score_dict, t, 'json')
        #scores.update_scores()
        ts = scores.total_scores()
        d = scores.get_picks_by_user() 
        leaders = scores.get_leader()
        print ('db leaders', leaders)
        return Response(({'picks': d,
                          'totals': ts,
                          'leaders': leaders,
                          'cut_line': t.cut_score
         }), 200)



class NewScoresView(LoginRequiredMixin,ListView):
    login_url = 'login'
    template_name = 'golf_app/scores.html'
    #form=CreateManualScoresForm
    #golfers = manual_score.Score('016').get_picked_golfers()
    queryset = Picks.objects.filter(playerName__tournament__current=True) 

    def get_context_data(self, **kwargs):
        context = super(NewScoresView, self).get_context_data(**kwargs)
        if self.kwargs.get('pk') != None:
            print (self.kwargs)
            tournament = Tournament.objects.get(pk=self.kwargs.get('pk'))
        else:
            tournament = Tournament.objects.get(current=True)
        
        if not tournament.started():
           user_dict = {}
           for user in Picks.objects.filter(playerName__tournament=tournament).values('user__username').annotate(Count('playerName')):
               user_dict[user.get('user__username')]=user.get('playerName__count')
               if tournament.pga_tournament_num == '470': #special logic for match player
                  scores = (None, None, None, None,None)
               #else:  scores=calc_score.calc_score(self.kwargs, request)
           self.template_name = 'golf_app/pre_start.html'

           context.update({'user_dict': user_dict,
                           'tournament': tournament,
                          # 'lookup_errors': scores[4],
                                                    })

           return context
        ## from here all logic should only happen if tournament has started

        if not tournament.picks_complete():
               tournament.missing_picks()

        try:
            json_url = tournament.score_json_url
            with urllib.request.urlopen(json_url) as field_json_url:
                    data = json.loads(field_json_url.read().decode())
            print ('pga json availablE!')
        except Exception as e:
            print ('cant open pga score file', e)

            context.update({'scores':TotalScore.objects.filter(tournament=tournament).order_by('score'),
                            'detail_list':None,
                            'leader_list':None,
                            'cut_data':None,
                            'lookup_errors': None,
                            'tournament': tournament,
                            'thru_list': [],
                                        })

            return context        


#from golf_app import manual_score
class ManualScoresView(LoginRequiredMixin,ListView):
    login_url = 'login'
    template_name = 'golf_app/scores.html'
    #form=CreateManualScoresForm
    #golfers = manual_score.Score('016').get_picked_golfers()
    queryset = Picks.objects.filter(playerName__tournament__current=True) 

def get_score_dict(tournament):
    '''takes a tournament obj and returns a dict of the picks with scores'''
    score_dict = {}
    for s in ScoreDetails.objects.filter(pick__playerName__tournament=tournament):
        score_dict[s.pick.playerName.playerName] = \
        {'rank': s.score, 'change': None, 'thru': s.thru, 'total_score': s.toPar, 'round_score': s.today_score}
    #print ('get_score_dict', score_dict)
    return score_dict