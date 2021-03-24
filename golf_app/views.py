from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, TemplateView, ListView, DetailView, CreateView, UpdateView, FormView
#from extra_views import ModelFormSetView
from golf_app.models import Field, Tournament, Picks, Group, TotalScore, ScoreDetails, \
           mpScores, BonusDetails, PickMethod, PGAWebScores, ScoreDict, UserProfile, \
           Season
from golf_app.forms import  CreateManualScoresForm, FieldForm, FieldFormSet
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateResponseMixin
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
import datetime
from golf_app import populateField, calc_score, optimal_picks,\
     manual_score, scrape_scores_picks, scrape_cbs_golf, scrape_masters, withdraw, scrape_espn, \
     populateMPField, mp_calc_scores
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
from django.core.mail import send_mail
import time
from django.core import serializers
from golf_app import golf_serializers


class FieldListView(LoginRequiredMixin,TemplateView):
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
        print ('started', tournament.started())

        if tournament.started() and tournament.late_picks is False:
            print ('picks too late', user, datetime.datetime.now())
            print (timezone.now())
            return HttpResponse ("Sorry it is too late to submit picks.")
        
        if Picks.objects.filter(playerName__tournament=tournament, user=user).count()>0:
            Picks.objects.filter(playerName__tournament=tournament, user=user).delete()
            ScoreDetails.objects.filter(pick__playerName__tournament=tournament, user=user).delete()

        if request.POST.get('random') == 'random':
            picks = tournament.create_picks(user, 'random')    
            print ('random picks submitted', user, datetime.datetime.now(), picks)
        else:
            form = request.POST
            if tournament.last_group_multi_pick():
                #hard coding to 6, should i change to dynamic?
                last_group = form.getlist('multi-group-6')
            pick_list = []
            
            for k, v in form.items():
                if k != 'csrfmiddlewaretoken' and k!= 'userid' \
                   and k != 'multi-group-6':
                    pick_list.append(Field.objects.get(pk=v))
                elif k == 'multi-group-6':
                    for pick in last_group:
                        pick_list.append(Field.objects.get(pk=pick))

            tournament.save_picks(pick_list, user, 'self')

            print ('user submitting picks', datetime.datetime.now(), request.user, pick_list)
        
        if UserProfile.objects.filter(user=user).exists():
            profile = UserProfile.objects.get(user=user)
            if profile.email_picks:
                email_picks(tournament, user)

        return redirect('golf_app:picks_list')


def email_picks(tournament, user):

    mail_picks = "\r"
    for pick in Picks.objects.filter(playerName__tournament=tournament, user=user):
        mail_picks = mail_picks + 'Group: ' + str(pick.playerName.group.number) + ' Golfer: ' + pick.playerName.playerName + "\r"

    mail_sub = "Golf Game Picks Submittted: " + tournament.name 
    mail_t = "Tournament: " + tournament.name + "\r"
    

    mail_url = "Website to make changes or picks: " + "http://jflynn87.pythonanywhere.com/golf_app/field/"
    mail_content = mail_t + "\r" + "\r" +mail_picks + "\r"+ mail_url
    mail_recipients = [user.email]
    send_mail(mail_sub, mail_content, 'jflynn87g@gmail.com', mail_recipients)  #add fail silently
    
    return

# commented 8/30/2020 use model.py - delete after some testing
# def save_picks(user, tournament, pick_list):
#     '''takes user obj, tournament obj and pick list and saves picks as well as sets up score detail and Bonus
#     details for the tournament'''

#     for picks in pick_list:
#         pick = Picks()
#         pick.user = user
#         pick.playerName = Field.objects.get(playerName=picks, tournament=tournament)
#         pick.save()
#         sd = ScoreDetails()
#         sd.user = user
#         sd.pick = pick
#         sd.save()

#     bd, created = BonusDetails.objects.get_or_create(tournament = tournament, \
#     user = user, winner_bonus = 0, cut_bonus = 0)
#     bd.save()

#     return


class ScoreGetPicks(APIView):
    
    def get(self, request, pk, username):
        try: 
            t = Tournament.objects.get(pk=pk)
            user = User.objects.get(username=username)
            scores = manual_score.Score(None, t, 'json')
            picks = scores.get_picks_by_user(user)
            
            return JsonResponse(picks, status=200)
        except Exception as e:
            print ('Get Picks API exception', e)
            return Response(json.dumps({'status': str(e)}), 500)
            

class GetPicks(APIView):
    
    def get(self, num):
        try: 
            pick_list = []
            for pick in Picks.objects.filter(user__username=self.request.user, playerName__tournament__current=True):
                pick_list.append(pick.playerName.pk)
            print ('getting picks API response', self.request.user, json.dumps(pick_list))
            return Response(json.dumps(pick_list), 200)
        except Exception as e:
            print ('Get Picks API exception', e)
            return Response(json.dumps({'status': str(e)}), 500)
            


class PicksListView(LoginRequiredMixin,ListView):
    login_url = 'login'
    redirect_field_name = 'golf_app/pick_list.html'
    model = Picks

    def get_context_data(self,**kwargs):
        context = super(PicksListView, self).get_context_data(**kwargs)
        context.update({
        'tournament': Tournament.objects.get(current=True),
        'picks_list': Picks.objects.filter(playerName__tournament__current=True,user=self.request.user),
        })
        return context


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
                for winner in tournament.winner():
                    score_list.append(winner.user)
                    
                    if tournament.major:
                        winner_dict[winner.user] = winner_dict.get(winner.user) + 50/tournament.num_of_winners()
                    else:
                        winner_dict[winner.user] = winner_dict.get(winner.user) + 30/tournament.num_of_winners()

            display_dict[tournament] = score_list

        total_score_list = []
        total_second_half_score_list = []
        for score in total_scores.values():
            total_score_list.append(score)
        #added for Mark
        for s in second_half_scores.values():
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
            if Tournament.objects.filter(current=True).exists():
                t = Tournament.objects.get(current=True)
            else:
                t = None
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
        if url_number == '470':  #Match Play special logic
            populateMPField.create_groups(url_number)
            return HttpResponseRedirect(reverse('golf_app:field'))
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
        sd = ScoreDict.objects.get(tournament=t)
        info = get_info(t)

        if t.complete:
            display_data = json.loads(sd.pick_data)
                
            return Response(({'picks': display_data.get('display_data').get('picks'),
                            'totals': display_data.get('display_data').get('totals'),
                            'leaders': display_data.get('display_data').get('leaders'),
                            'cut_line': display_data.get('display_data').get('cut_line'),
                            'optimal': display_data.get('display_data').get('optimal'), 
                            'scores': display_data.get('display_data').get('scores'),
                            'season_totals': display_data.get('display_data').get('season_totals'),
                            'info': json.dumps(info),
                            't_data': serializers.serialize("json", [t])
            }), 200)


        if t.current and not t.complete:
            print ('scraping')
            if t.pga_tournament_num == '470':
                return HttpResponse('Wrong link, use MP link')
            else:
                score_dict = scrape_espn.ScrapeESPN().get_data()
        else:
            print ('not scraping')
            try:
                score_dict = sd.pick_data()
            except Exception as e:
                score_dict = {}
                #score_dict = get_score_dict(t)
                print ('error using old score dict method', t, e)
            
        
        scores = manual_score.Score(score_dict, t, 'json')
        # change so this isn't executed when complete, add function to get total scores without updating
        #print (len(score_dict))
        if len(score_dict) == 0:
            print ('score_dict empty')
            return Response(({}), 200)
        
        if t.current and len(score_dict) != 0:
            optimal_picks = {}
            for g in Group.objects.filter(tournament=t):
                opt = scores.optimal_picks(g.number)
                optimal_picks[str(g.number)] = {
                                                'golfer': opt[0],
                                                'rank': opt[1],
                                                'cuts': opt[2],
                                                'total_golfers': g.playerCnt
                } 

            scores.update_scores(optimal_picks)
        
        ts = scores.total_scores()
        picks_ret = datetime.datetime.now()
        d = {'msg': 'no data'}
        print ('get picks duration:: ', datetime.datetime.now()- picks_ret)

        leaders = scores.get_leader()
        totals = Season.objects.get(season=t.season).get_total_points()
        t_data = serializers.serialize("json", [t, ])
        display_dict = {}
        display_dict['display_data'] = {'picks': d,
                          'totals': ts,
                          'leaders': leaders,
                          'cut_line': score_dict.get('info').get('cut_line'),
                          'optimal': json.dumps(optimal_picks),
                          'scores': json.dumps(score_dict),
                          'season_totals': totals,
                          't_data': t_data,
                          'round_status': score_dict.get('info').get('round_status')}
 
        sd.pick_data = json.dumps(display_dict)
        sd.data = score_dict 
        sd.save()

        #t.saved_cut_num = score_dict.get('info').get('cut_num')
        t.saved_round = score_dict.get('info').get('round')
        t.save()

        return Response(({'picks': d,
                          'totals': ts,
                          'leaders': leaders,
                          'cut_line': score_dict.get('info').get('cut_line'),
                          'optimal': json.dumps(optimal_picks),
                          'scores': json.dumps(score_dict),
                          'season_totals': totals,
                          'info': json.dumps(info),
                          't_data': t_data,
                          'round_status': score_dict.get('info').get('round_status')
         }), 200)

class GetDBScores(APIView):
    
    def get(self, num):
        
        print ('GetScores API VIEW', self.request.GET.get('tournament'))
        t = Tournament.objects.get(pk=self.request.GET.get('tournament'))
        sd, created = ScoreDict.objects.get_or_create(tournament=t)
        if created:
            sd.pick_data = {}
            sd.data = {}
            sd.save()
        info = get_info(t)
        t_data = serializers.serialize("json", [t, ])
        #print ('T DATA: ', type(t_data), t_data)


        try:
            display_data = json.loads(sd.pick_data)
            print ('display_data len: ', len(display_data))

            if len(display_data) > 0:    
                return Response(({'picks': display_data.get('display_data').get('picks'),
                                'totals': display_data.get('display_data').get('totals'),
                                'leaders': display_data.get('display_data').get('leaders'),
                                'cut_line': display_data.get('display_data').get('cut_line'),
                                'optimal': display_data.get('display_data').get('optimal'), 
                                'scores': display_data.get('display_data').get('scores'),
                                'season_totals': display_data.get('display_data').get('season_totals'),
                                'info': json.dumps(info),
                                't_data': display_data.get('display_data').get('t_data'),
                                'round_status': display_data.get('display_data').get('round_status')
                }), 200)
            else:
                print ('switch to get scores')
                print (self.request.GET)
                GetScores(self.request.GET, num)
        except Exception as e:
            print ('old logic', e)
            return (redirect('golf_app:get_scores'), num)
            #GetScores().get(self.request)
            #return Response({}, 200)

class NewScoresView(LoginRequiredMixin,ListView):
    login_url = 'login'
    template_name = 'golf_app/scores.html'
    queryset = Picks.objects.filter(playerName__tournament__current=True) 

    def get_context_data(self, **kwargs):
        context = super(NewScoresView, self).get_context_data(**kwargs)
        start = datetime.datetime.now()
        if self.kwargs.get('pk') != None:
            print (self.kwargs)
            tournament = Tournament.objects.get(pk=self.kwargs.get('pk'))
        else:
            tournament = Tournament.objects.get(current=True)
        
        if not tournament.started():
           user_dict = {}
           for user in Picks.objects.filter(playerName__tournament=tournament).values('user__username').annotate(Count('playerName')):
               user_dict[user.get('user__username')]=user.get('playerName__count')
               #if tournament.pga_tournament_num == '470': #special logic for match player
               #   scores = (None, None, None, None,None)
               #else:  scores=calc_score.calc_score(self.kwargs, request)
           self.template_name = 'golf_app/pre_start.html'

           context.update({'user_dict': user_dict,
                           'tournament': tournament,
                          # 'lookup_errors': scores[4],
                                                    })

           return context
        ## from here all logic should only happen if tournament has started
        if not tournament.picks_complete():
               print ('picks not complete')
               tournament.missing_picks()

        #score_dict = scrape_espn.ScrapeESPN().get_data()

        context.update({'scores':TotalScore.objects.filter(tournament=tournament).order_by('score'),
                        'detail_list':None,
                        'leader_list':None,
                        'cut_data':None,
                        'lookup_errors': None,
                        'tournament': tournament,
                        'thru_list': [],
                        'groups': Group.objects.filter(tournament=tournament),
                        #'score_dict': score_dict,
                                    })
        print ('scores context duration', datetime.datetime.now() -start)
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


class CheckStarted(APIView):

    def post(self, request):

        try:
            t_status  = {}
            key = request.data['key']
            print ('post', key)

            t = Tournament.objects.get(pk=key)

            if t.set_notstarted:
               return Response(json.dumps({'status': 'Overrode to not started'}), 200)


            if not t.started():
                #pga_web = scrape_scores_picks.ScrapeScores(t)
                #score_dict = pga_web.scrape()
                score_dict = scrape_espn.ScrapeESPN().get_data()
                print ('score dict started check: ', score_dict.get('info'))
                score = manual_score.Score(score_dict, t)
                #round = t.get_round()
                t_round = score_dict.get('info').get('round')
   
                #if t_round != None and t_round != 'Tournament Field' and t_round > 0:
                if t_round != None and (t_round != 1 and score_dict.get('round_status') != "Not Started"):
                    print ('started updating scores')
                    score.update_scores() 
                if t.started():
                    t_status['status'] = 'Started - refresh to see picks'
                else:
                    t_status['status'] = 'Not Started'
                #t_status['status'] = tourn.started()
                print ('responding', t_status)
            return Response(json.dumps(t_status), 200)
        except Exception as e:
            print ('error', e)
            return Response(json.dumps({'status': str(e)}), 500)

    def get(self, t_pk):
        print ('1', t_pk.GET)
        

        
        try:
            t = Tournament.objects.get(pk=self.request.GET.get('t_pk'))
            if not t.started():
                pga_web = scrape_scores.ScrapeScores(t)
                score_dict = pga_web.scrape()
            print (t.started())
            return Response(t.started, 200)
        except Exception as e:
            return Response(e, 500)

            
# class PriorResult(APIView):
#     def get(self, num):
#         print ('start prior result')
#         try:
#             results_list = []
#             current_t = Tournament.objects.get(current=True)
#             season = int(current_t.season.season)
#             t = Tournament.objects.get(name=current_t.name, season__season=(season-1))
#             print (t)
#             for score in ScoreDetails.objects.filter(pick__playerName__tournament=t).order_by('score').values('pick__playerName__playerName', 'score').distinct():
#                 print (score)
#                 results_list.append({'golfer': score.get('pick__playerName__playerName'), 'score': score.get('score')})

#             return Response(json.dumps(results_list), 200)
#         except Exception as e:
#             print ('exception', e)
#             return Response(e, 500)

class OptimalPicks(APIView):
    pass
    # def get(self, num):
        
    #     try:
    #         result_dict = {}
    #         t = Tournament.objects.get(pk=self.request.GET.get('tournament'))
            
    #         for g in Group.objects.filter(tournament=t):
    #             result_dict[g.number] = g.best_picks()

    #         print ('optimal_picks', result_dict)
    #         return Response(json.dumps(result_dict), 200)
    #     except Exception as e:
    #         print ('exception', e)
    #         return Response(json.dumps({e}), 500)


class GetInfo(APIView):

    def get(self, num):
        print (self.request.GET)
        try:
            info_dict = {}
            t = Tournament.objects.get(pk=self.request.GET.get('tournament'))
            total_picks = 0

            for g in Group.objects.filter(tournament=t):
                info_dict[g.number] = g.num_of_picks()
                total_picks += g.num_of_picks()
            info_dict['total'] = total_picks

            #info_dict['complete'] = t.complete

            print ('info dict class', info_dict)
            return Response(json.dumps(info_dict), 200)
        except Exception as e:
            print ('exception', e)
            return Response(json.dumps({e}), 500)

def get_info(t):
    try:
        info_dict = {}
        t = Tournament.objects.get(pk=t.pk)
        total_picks = 0

        for g in Group.objects.filter(tournament=t):
            info_dict[g.number] = g.num_of_picks()
            total_picks += g.num_of_picks()
        info_dict['total'] = total_picks

        info_dict['complete'] = t.complete
        print ('info dict function', info_dict)
        return info_dict
    except Exception as e:
        print ('exception', e)
        return Response({'error': e})



class CBSScores(APIView):

    ## not started, add code

    def get(self, num):
        #print (self.request.GET)

        try:
            
            #info_dict = {}
            t = Tournament.objects.get(pk=self.request.GET.get('tournament'))

            if t.complete:
                return Response(({}), 200)

            sd = ScoreDict.objects.get(tournament=t)
            info = get_info(t)
            if not t.current:
                return (json.dumps({'error': 'only for current tournament'}), 500)

            score_dict = scrape_cbs_golf.ScrapeCBS().get_data()

        
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
                optimal = t.optimal_picks()
                totals = Season.objects.get(season=t.season).get_total_points()

                display_dict = {}
                display_dict['display_data'] = {'picks': d,
                                'totals': ts,
                                'leaders': leaders,
                                'cut_line': t.cut_score,
                                'optimal': optimal,
                                'scores': json.dumps(score_dict),
                                'season_totals': totals,}

                sd.cbs_data = json.dumps(display_dict)
                sd.save()

                return Response(({'picks': d,
                                'totals': ts,
                                'leaders': leaders,
                                'cut_line': t.cut_score,
                                'optimal': optimal,
                                'scores': json.dumps(score_dict),
                                'season_totals': totals,
                                'info': json.dumps(info),
                }), 200)

        except Exception as e:
            print ('exception', e)
            return Response(json.dumps({'error': e}), 500)


class GetFieldCSV(APIView):

    def get(self, num):
        print ('get field csv', self.request.GET)
        try:
            t = Tournament.objects.get(pk=self.request.GET.get('tournament'))
            data = serializers.serialize('json', Field.objects.filter(tournament=t),  use_natural_foreign_keys=True)
            #data = golf_serializers.FieldSerializer(Field.objects.filter(tournament=t), many=True).data
            #return JsonResponse(data, 200)
            return Response(data, 200)
        except Exception as e:
            print ('exception', e)
            return Response(json.dumps({e}), 500)


class GetGroupNum(APIView):

    def get(self, request):
        print ('get group num', self.request.GET.get('group_pk'))
        try:
            #t = Tournament.objects.get(pk=self.request.GET.get('tournament'))
            #data = serializers.serialize('json', Field.objects.filter(tournament=t))
            group = Group.objects.get(pk=self.request.GET.get('group_pk'))

            return Response(json.dumps({'group_num': group.number}), 200)
            # return Response(json.dumps(data), 200)
        except Exception as e:
            print ('exception', e)
            return Response(json.dumps({e}), 500)

    def post(self, request):
        print ('get group num', request.data)
        try:
            group_dict = {}
            t = Tournament.objects.get(pk=request.data.get('tournament_key'))
            #data = serializers.serialize('json', Group.objects.filter(tournament=t))
            for g in Group.objects.filter(tournament=t):
                group_dict[g.pk] = g.number


            #return Response(json.dumps({'group_num': group.number}), 200)
            print (group_dict)
            return Response(json.dumps([group_dict]), 200)
        except Exception as e:
            print ('exception', e)
            return Response(json.dumps({e}), 500)

class GolfLeaderboard(APIView):
    def get(self, request):

        try:
            data = {}
            season = Season.objects.get(current=True)

            data = dict(json.loads(season.get_total_points()))
                        
            sorted_data = sorted(data.items(), key=lambda x: x[1]['total'])
            print (sorted_data)
        except Exception as e:
            print ('error: ', e)
            sorted_data['error'] = {'msg': str(e)}
                
        return Response(json.dumps(sorted_data), 200)

class Withdraw(APIView):
    def get(self, request):

        try:
            
            wds = withdraw.WDCheck().check_wd()
            print ('wds', wds['wd_list'])
            wd_picks = withdraw.WDCheck().check_wd_picks()
            wds.update({'wd_picks': wd_picks})
            print (wds)

        except Exception as e:
            print ('error: ', e)
            wds = {'msg': str(e)}
                
        return JsonResponse(wds, status=200)

class ValidateESPN(APIView):
    def get(self, request):
        issues = {}
        issues['field_missing'] = {}
        try:
            t = Tournament.objects.get(current=True)
            for f in Field.objects.filter(tournament=t, golfer__espn_number__isnull=True):
                issues['field_missing'].update({'golfer': f.playerName,
                                            'espn_num': f.golfer.espn_number})
            
            print ('missing espn nums', issues)

        except Exception as e:
            print ('chekc espn num api error: ', e)
            issues['field_mising'].update({'msg': str(e)})
                
        return JsonResponse(issues, status=200)


class ScoresByPlayerView(LoginRequiredMixin,TemplateView):
    login_url = 'login'
    template_name = 'golf_app/scores.html'
    #queryset = Picks.objects.filter(playerName__tournament__current=True) 

    def get_context_data(self, **kwargs):
        context = super(ScoresByPlayerView, self).get_context_data(**kwargs)
        start = datetime.datetime.now()
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
               print ('picks not complete')
               tournament.missing_picks()

        #score_dict = scrape_espn.ScrapeESPN().get_data()

        context.update({'scores':TotalScore.objects.filter(tournament=tournament).order_by('score'),
                        'detail_list':None,
                        'leader_list':None,
                        'cut_data':None,
                        'lookup_errors': None,
                        'tournament': tournament,
                        'thru_list': [],
                        'groups': Group.objects.filter(tournament=tournament), 
                        #'score_dict': score_dict,
                                    })
        print ('scores context duration', datetime.datetime.now() -start)
        return context        


class ESPNScoreDict(APIView):
    def get(self, request, pk):
        try:
            data = {}
            data['users'] = {}
            user_list = []
            t = Tournament.objects.get(pk=pk)
            #t = Tournament.objects.get(current=True)
            users = t.season.get_users()
            for user in users:
                data['users'].update({
                                     user.get('user'): str(User.objects.get(pk=user.get('user')))
                })
                user_list.append(user.get('user'))
            #data['users'] = user_list
            score_dict = scrape_espn.ScrapeESPN().get_data()            
            optimal_picks = {}
            score = manual_score.Score(score_dict, t)
            for g in Group.objects.filter(tournament=t):
                opt = score.optimal_picks(g.number)
                optimal_picks[str(g.number)] = {
                                                'golfer': opt[0],
                                                'rank': opt[1],
                                                'cuts': opt[2],
                                                'total_golfers': g.playerCnt
                } 

            data['optimal_picks'] = optimal_picks
            data['score_dict'] = score_dict
            data['t_data'] = serializers.serialize("json", [t, ])
            data['info'] = get_info(t)
            data['season_totals'] = Season.objects.get(season=t.season).get_total_points()
            data['leaders'] = score.get_leader()
            #print (type(data))
        except Exception as e:
            print ('espn score dict api error: ', e)
            data['msg'] = {'msg': str(e)}
                
        return JsonResponse(data, status=200)


class ScoresByPlayerAPI(APIView):
    def post(self, request):
        try:
            print ('request.POST.data: ', request.data )
            data = {}
            u = User.objects.get(pk=request.data.get('user_pk'))
            t = Tournament.objects.get(pk=request.data.get('tournament_key'))
            score = manual_score.Score(request.data.get('score_dict'), t, 'json')
            update = score.update_scores_player(u, request.data.get('optimal_picks'))
            
            #data['picks'] = score.get_picks_by_user(u)
            data['totals'] = score.player_total_score(u)
            #print ('by player scores: ', data)
            #data = serializers.serialize('json', ScoreDetails.objects.filter(user=u, pick__playerName__tournament=t))

        except Exception as e:
            print ('score by player api error: ', e)
            data = {'msg': str(e)}
                
        #return JsonResponse(data, status=200)
        return JsonResponse(data, status=200)


class PriorResultAPI(APIView):
    def post(self, request):
        start = datetime.datetime.now()
        try:
            #g_num = group.split('-')[2]
            t= Tournament.objects.get(pk=request.data.get('tournament_key'))

            data = golf_serializers.NewFieldSerializer(Field.objects.filter(tournament=t, golfer__espn_number__in=request.data.get('golfer_list')), many=True).data
            #data = serializers.serialize("json", Field.objects.filter(tournament=t, golfer__espn_number__in=request.data.get('golfer_list')), use_natural_foreign_keys=True)
            #print(data)
        except Exception as e:
            print ('prior result api error: ', e) 
            data = json.dumps({'msg': str(e)})
                
        #return JsonResponse(data, status=200)
        print ('prior result duration: ', request.data.get('golfer_list'), datetime.datetime.now() - start)
        return JsonResponse(data, status=200, safe=False)


class RecentFormAPI(APIView):
    def get(self, request, player_num):
        try:
            data = {}
            data[player_num]['prior_result'] = {}
            data[player_num]['recent'] = {}
            
            #result_list = []
            for t in reversed(Tournament.objects.all().order_by('-pk')[1:5]):
                if Field.objects.filter(tournament=t, golfer__espn_number=player_num).exists():
                    f = Field.objects.get(tournament=t, golfer__espn_number=player_num)
                    sd = ScoreDict.objects.get(tournament=t)
                    x = [v.get('rank') for k, v in sd.data.items() if k !='info' and v.get('pga_num') in [f.golfer.espn_number, f.golfer.golfer_pga_num]]
                    data[player_num]['recent'].update({t.name: x[0]})
                else:
                    data[player_num].update({t.name: 'DNP'})
            
            
            #data[player_num] = result_list

        except Exception as e:
            print ('recent form api error: ', e)
            data = {'msg': str(e)}
                
        #return JsonResponse(data, status=200)
        return JsonResponse(data, status=200)

#class UpdateFieldView(FormView):
class UpdateFieldView(LoginRequiredMixin, TemplateView):
    login_url = '/login'
    template_name='golf_app/update_field.html'

    def get_context_data(self, **kwargs):
        context = super(UpdateFieldView, self).get_context_data(**kwargs)
        t = Tournament.objects.get(current=True)
        context.update({
            't': t,
            'field': Field.objects.filter(tournament=t).order_by('group', 'currentWGR'),
            #'form': FieldForm(),
            'formset': FieldFormSet(queryset=Field.objects.filter(tournament=t))

        })
        return context

    def post(self, request):
        #print (request.POST)
        formset = FieldFormSet(request.POST)
        print (formset)
        if not formset.is_valid():
                return HttpResponse({
                    #'t': t,
                    #'field': Field.objects.filter(tournament=t).order_by('group', 'currentWGR'),
                    #'form': FieldForm(),
                    'formset': formset

                })

        for f in formset:
            if f.is_valid():
                if f.has_changed():
                    print('changed', f)
                    f.save() 

        return redirect('golf_app:update_field')
    

class GetGroupAPI(APIView):
    pass
    def get(self, request, pk):
        try:
           data = {}
           field = Field.objects.get(pk=pk)
           data = {'field': field.pk, 'group': field.group.pk}
           return JsonResponse(data, status=200)
        except Exception as e:
            print ('Get group API failed: ', e)
            return JsonResponse({'key': 'error'}, status=401)

            
class MPScoresAPI(APIView):

    def get(self, request):
        #t_key = request.data.get('tournament')
        pk =self.request.GET.get('tournament')
        t = Tournament.objects.get(pk=pk)
        score_dict = scrape_espn.ScrapeESPN().get_mp_data()
        print (score_dict)
        scores = mp_calc_scores.espn_calc(score_dict)
        ts = mp_calc_scores.total_scores()
        info = get_info(t)
        totals = Season.objects.get(season=t.season).get_total_points()
        print ('calc scores complete MP')

        return Response(({'picks':  {'msg': 'no data'},
                                'totals': ts,
                                'leaders':  {'msg': 'no data'},
                                'cut_line':  {'msg': 'no data'},
                                'optimal': None,
                                'scores': json.dumps(score_dict),
                                'season_totals': totals,
                                'info': json.dumps(info),
                                't_data': serializers.serialize("json", [t])
                }), 200)





