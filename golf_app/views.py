from django.db.models.query_utils import RegisterLookupMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, TemplateView, ListView, DetailView, CreateView, UpdateView, FormView
#from extra_views import ModelFormSetView
from golf_app.models import Field, Tournament, Picks, Group, TotalScore, ScoreDetails, \
           mpScores, BonusDetails, PickMethod, PGAWebScores, ScoreDict, UserProfile, \
           Season, AccessLog, Golfer, AuctionPick
from golf_app.forms import  CreateManualScoresForm, FieldForm, FieldFormSet, AuctionPicksFormSet
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
     populateMPField, mp_calc_scores, golf_serializers, utils
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
from rest_framework.generics import ListAPIView
from django.core.mail import send_mail
import time
from django.core import serializers
#from golf_app import golf_serializers
from collections import OrderedDict


class FieldListView(LoginRequiredMixin,TemplateView):
    login_url = 'login'
    template_name = 'golf_app/field_list.html'
    model = Field
    #redirect_field_name = 'next'

    def get_context_data(self,**kwargs):
        context = super(FieldListView, self).get_context_data(**kwargs)
        tournament = Tournament.objects.get(current=True)
        # print (tournament.started())
        # #check for withdrawls and create msg if there is any
        # try:
        #     score_file = calc_score.getRanks({'pk': tournament.pk})
        #     wd_list = []
        #     print ('score file', score_file[0])
        #     if score_file[0] == "score lookup fail":
        #         wd_list = []
        #         error_message = ''
        #     else:
        #         for golfer in Field.objects.filter(tournament=tournament):
        #             if golfer.playerName not in score_file[0]:
        #                 print ('debug')
        #                 wd_list.append(golfer.playerName)
        #                 #print ('wd list', wd_list)
        #         if len(wd_list) > 0:
        #             error_message = 'The following golfers have withdrawn:' + str(wd_list)
        #             for wd in wd_list:
        #                 Field.objects.filter(tournament=tournament, playerName=wd).update(withdrawn=True)
        #         else:
        #             error_message = None
        # except Exception as e:
        #     print ('score file lookup issue', e)
        #     error_message = None

        context.update({
        'field_list': Field.objects.filter(tournament=Tournament.objects.get(current=True)),
        'tournament': tournament,
        #'error_message': error_message
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

class NewFieldListView(LoginRequiredMixin,TemplateView):
    login_url = 'login'
    template_name = 'golf_app/field_list_a.html'
    model = Field
    #redirect_field_name = 'next'

    def get_context_data(self,**kwargs):
        context = super(NewFieldListView, self).get_context_data(**kwargs)
        tournament = Tournament.objects.get(current=True)
        # print (tournament.started())
        # #check for withdrawls and create msg if there is any
        # try:
        #     score_file = calc_score.getRanks({'pk': tournament.pk})
        #     wd_list = []
        #     print ('score file', score_file[0])
        #     if score_file[0] == "score lookup fail":
        #         wd_list = []
        #         error_message = ''
        #     else:
        #         for golfer in Field.objects.filter(tournament=tournament):
        #             if golfer.playerName not in score_file[0]:
        #                 print ('debug')
        #                 wd_list.append(golfer.playerName)
        #                 #print ('wd list', wd_list)
        #         if len(wd_list) > 0:
        #             error_message = 'The following golfers have withdrawn:' + str(wd_list)
        #             for wd in wd_list:
        #                 Field.objects.filter(tournament=tournament, playerName=wd).update(withdrawn=True)
        #         else:
        #             error_message = None
        # except Exception as e:
        #     print ('score file lookup issue', e)
        #     error_message = None

        context.update({
        #'field_list': Field.objects.filter(tournament=Tournament.objects.get(current=True)),
        'tournament': tournament,
        'groups': Group.objects.filter(tournament=tournament)
        #'error_message': error_message
        })
        return context

    @transaction.atomic
    def post(self, request):

        print ('request data ', self.request.POST)  #this is it
        data = json.loads(self.request.body)
        print (data, type(data))
        pick_list = data.get('pick_list')
        print ('pick_list', pick_list)
        tournament = Tournament.objects.get(current=True)
        #groups = Group.objects.filter(tournament=tournament)
        user = User.objects.get(username=request.user)

        if 'random' not in pick_list:
            if len(pick_list) != tournament.total_required_picks():
                print ('total picks match: ', len(pick_list), tournament.total_required_picks())
                msg = 'Something went wrong, wrong number of picks.  Expected: ' + str(tournament.total_required_picks()) + ' received: ' + str(len(pick_list)) + ' Please try again'
                response = {'status': 0, 'message': msg} 
                return HttpResponse(json.dumps(response), content_type='application/json')

            for group in Group.objects.filter(tournament=tournament):
                count = Field.objects.filter(group=group, pk__in=pick_list).count()
                if count == group.num_of_picks():
                    print ('group ok: ', group, ' : count: ', count)
                else:
                    print ('group ERROR: ', group, ' : count: ', count)
                    msg = 'Pick error: Group - ' + str(group.number) + ' expected' + str(group.num_of_picks()) + ' picks.  Actual Picks: ' + str(count)
                    response = {'status': 0, 'message': msg} 
                    return HttpResponse(json.dumps(response), content_type='application/json')

        print ('user', user)
        print ('started', tournament.started())

        if tournament.started() and tournament.late_picks is False:
            print ('picks too late', user, datetime.datetime.now())
            print (timezone.now())
            msg = 'Too late for picks, tournament started'
            response = {'status': 0, 'message': msg} 
            return HttpResponse(json.dumps(response), content_type='application/json')

        
        if Picks.objects.filter(playerName__tournament=tournament, user=user).count()>0:
            Picks.objects.filter(playerName__tournament=tournament, user=user).delete()
            ScoreDetails.objects.filter(pick__playerName__tournament=tournament, user=user).delete()

        if 'random' in pick_list:
            picks = tournament.create_picks(user, 'random')    
            print ('random picks submitted', user, datetime.datetime.now(), picks)
        else:
            field_list = []
            for id in pick_list:
                field_list.append(Field.objects.get(pk=id))                    
            tournament.save_picks(field_list, user, 'self')

        print ('user submitting picks', datetime.datetime.now(), request.user, Picks.objects.filter(playerName__tournament=tournament, user=user))
    
        if UserProfile.objects.filter(user=user).exists():
            profile = UserProfile.objects.get(user=user)
            if profile.email_picks:
                email_picks(tournament, user)

        #return redirect('golf_app:picks_list')
        msg = 'Picks Submitted'
        response = {'status': 1, 'message': msg, 'url': '/golf_app/picks_list'} 
        return HttpResponse(json.dumps(response), content_type='application/json')




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


class ScoreGetPicks(ListAPIView):
    serializer_class = golf_serializers.ScoreDetailsSerializer

    def get_queryset(self, *args, **kwargs):
        start = datetime.datetime.now()
        if self.kwargs.get('username') == 'all':
            t = Tournament.objects.get(pk=self.kwargs.get('pk'))
            #u = User.objects.get(username=self.kwargs.get('username'))
            #queryset = ScoreDetails.objects.filter(pick__playerName__tournament=t, user=u)
            queryset = ScoreDetails.objects.filter(pick__playerName__tournament=t)
        else:
            t = Tournament.objects.get(pk=self.kwargs.get('pk'))
            u = User.objects.get(username=self.kwargs.get('username'))
            queryset = ScoreDetails.objects.filter(pick__playerName__tournament=t, user=u)

        print ('return serialized piks: ', datetime.datetime.now() - start)
        return queryset
           

class GetPicks(APIView):
    
    def get(self, num):
        start = datetime.datetime.now()
        try: 
            pick_list = []
            for pick in Picks.objects.filter(user__username=self.request.user, playerName__tournament__current=True):
                pick_list.append(pick.playerName.pk)
            print ('getting picks API response', self.request.user, json.dumps(pick_list), datetime.datetime.now() - start)

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
        utils.save_access_log(self.request, 'total scores')
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
        'season': Season.objects.get(current=True),

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
        #if url_number == '470':  #Match Play special logic
        #    populateMPField.create_groups(url_number)
        #    return HttpResponseRedirect(reverse('golf_app:field'))
        try:
            if Tournament.objects.filter(pga_tournament_num=str(url_number), season__current=True).exists():
                error_msg = ("tournament already exists" + str(url_number))
                return render(request, 'golf_app/setup.html', {'error_msg': error_msg})
            else:
                print ('creating field A')
                populateField.create_groups(url_number)
                return HttpResponseRedirect(reverse('golf_app:new_field_list'))
        except ObjectDoesNotExist:
            print ('obj does not exist exept - creating field')
            populateField.create_groups(url_number)
            return HttpResponseRedirect(reverse('golf_app:new_field_list'))
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
            elif t.pga_tournament_num == '018':
                score_dict = scrape_cbs_golf.ScrapeCBS().get_data()
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
        # try:            
        #     if not score_dict.get('info').get('dict_status') == 'updated':
        #         print ('no change in scores, returning from DB')
        #         display_data = json.loads(sd.pick_data)
        #         return Response(({'picks': display_data.get('display_data').get('picks'),
        #                         'totals': display_data.get('display_data').get('totals'),
        #                         'leaders': display_data.get('display_data').get('leaders'),
        #                         'cut_line': display_data.get('display_data').get('cut_line'),
        #                         'optimal': display_data.get('display_data').get('optimal'), 
        #                         'scores': display_data.get('display_data').get('scores'),
        #                         'season_totals': display_data.get('display_data').get('season_totals'),
        #                         'info': json.dumps(info),
        #                         't_data': serializers.serialize("json", [t])
        #         }), 200)
        # except Exception as e:
        #     print ('cant restore from display dict, recalc scores')

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
                          'scores': json.dumps(OrderedDict(score_dict)),
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
                          'scores': json.dumps(OrderedDict(score_dict)),
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

        try:
            display_data = json.loads(sd.pick_data)

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
        if self.request.user.is_authenticated:
            utils.save_access_log(self.request, 'current week scores')

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
            t = Tournament.objects.get(pk=key)

            if t.set_notstarted:
               t_status['status'] = 'Overrode to not started'
               t_status['started'] = False
               t_status['late_picks'] = t.late_picks
                #return Response(json.dumps({'status': 'Overrode to not started'}), 200)
            elif t.started():
                #score_dict = scrape_espn.ScrapeESPN().get_data()
                #score = manual_score.Score(score_dict, t)
                t_status['status'] = 'Started - refresh to see picks'
                t_status['started'] = True
                t_status['late_picks'] = t.late_picks
            else:
                 t_status['status'] = 'Not Started'
                 t_status['started'] = False
                 t_status['late_picks'] = t.late_picks

            # if not t.started():
            #     #score_dict = scrape_espn.ScrapeESPN().get_data()
            #     status = scrape_espn.ScrapeESPN().status_check()
            #     if status == "Tournament Field":
            #         t_status['status'] = 'Not Started'
            #     #print ('score dict started check: ', score_dict.get('info'))
            #     else:
            #         score_dict = scrape_espn.ScrapeESPN().get_data()
            #         score = manual_score.Score(score_dict, t)
            #         t_status['status'] = 'Started - refresh to see picks'
                #round = t.get_round()
                    #t_round = score_dict.get('info').get('round')

   
                #if t_round != None and t_round != 'Tournament Field' and t_round > 0:
                #if t_round != None and (t_round != 1 and score_dict.get('round_status') != "Not Started"):
                #    print ('started updating scores')
                #    score.update_scores() 
                #if t.started():
                #    t_status['status'] = 'Started - refresh to see picks'
                #else:
                #    t_status['status'] = 'Not Started'
                #t_status['status'] = tourn.started()
                #print ('responding', t_status)
            return Response(json.dumps(t_status), 200)
        except Exception as e:
            print ('error', e)
            return Response(json.dumps({'status': str(e)}), 500)

    # def get(self, t_pk):
       
    #     try:
    #         t = Tournament.objects.get(pk=self.request.GET.get('t_pk'))
    #         if not t.started():
    #             pga_web = scrape_scores.ScrapeScores(t)
    #             score_dict = pga_web.scrape()
    #         print (t.started())
    #         return Response(t.started, 200)
    #     except Exception as e:
    #         return Response(e, 500)

            
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
            #info_dict['started'] = t.started()

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
            print (data)
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
        return JsonResponse(scrape_espn.ScrapeESPN().get_data(), status=200)
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
        print ('PROIR RESULT api DATA: ', request.data)
        try:
            #g_num = group.split('-')[2]
            t= Tournament.objects.get(pk=request.data.get('tournament_key'))
            
            if request.data.get('group') == 'all':
                data= golf_serializers.NewFieldSerializer(Field.objects.filter(tournament=t), many=True).data
            elif len(request.data.get('golfer_list')) == 0:
                data= golf_serializers.NewFieldSerializer(Field.objects.filter(tournament=t, group__number=request.data.get('group')), many=True).data
            else:
                data = golf_serializers.NewFieldSerializer(Field.objects.filter(tournament=t, golfer__espn_number__in=request.data.get('golfer_list')), many=True).data
            #data = serializers.serialize("json", Field.objects.filter(tournament=t, golfer__espn_number__in=request.data.get('golfer_list')), use_natural_foreign_keys=True)
            #print(data)
        except Exception as e:
            print ('prior result api error: ', e) 
            data = json.dumps({'msg': str(e)})
                
        #return JsonResponse(data, status=200)
        print ('prior result duration: ', datetime.datetime.now() - start)
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
        print ('MP API ')
        #t_key = request.data.get('tournament')
        pk =self.request.GET.get('tournament')
        t = Tournament.objects.get(pk=pk)
        #score_dict = scrape_espn.ScrapeESPN().get_mp_data()
        if t.complete:
            sd = ScoreDict.objects.get(tournament=t)
            score_dict = sd.data
        elif t.saved_round == 1:
            print ('MP round 1 scraping group sect')
            score_dict = scrape_scores_picks.ScrapeScores(t, 'https://www.pgatour.com/competition/2021/wgc-dell-technologies-match-play/group-stage.html').mp_brackets()
        else:
            print ('MP round 2 scraping group sect')
            score_dict = scrape_scores_picks.ScrapeScores(t, 'https://www.pgatour.com/competition/2021/wgc-dell-technologies-match-play/leaderboard.html').mp_final_16()
        print (score_dict)
        scores = mp_calc_scores.espn_calc(score_dict)
        ts = mp_calc_scores.total_scores()
        info = get_info(t)
        totals = Season.objects.get(season=t.season).get_total_points()
        print ('calc scores complete MP')
        ScoreDict.objects.filter(tournament=t).update(data=score_dict)

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


class MPRecordsAPI(APIView):
    
    def get(self, request, pk):
        try:
           data = {}
           #pk = request.GET.get('pk')
           t = Tournament.objects.get(pk=pk)
           #t = Tournament.objects.get(season__current=True, pga_tournament_num='470')
           data = scrape_scores_picks.ScrapeScores(t, 'https://www.pgatour.com/competition/' + str(t.season.season) + '/wgc-dell-technologies-match-play/group-stage.html').mp_brackets()
           return JsonResponse(data, status=200)
        except Exception as e:
            print ('Get group API failed: ', e)
            return JsonResponse({'key': 'error'}, status=401)


class TrendDataAPI(APIView):
    
    def get(self, request, season_pk, num_of_t):
        print (season_pk, num_of_t)
        try:
            labels = []
            #data = []
            diff_dict= {}
            
            season = Season.objects.get(pk=season_pk)

            for user in season.get_users():
                u = User.objects.get(pk=user.get('user'))
                diff_dict[u.username] = []

            if num_of_t == "all":
                t_qs = Tournament.objects.filter(season__pk=season.pk).order_by('pk')
            else:
                t_qs = reversed(Tournament.objects.filter(season__pk=season.pk).order_by('-pk')[:int(num_of_t)])

            for t in t_qs:
                labels.append(t.name[0:8])
                totals = json.loads(t.season.get_total_points(t))
                
                for user, stats in totals.items():
                    #print (user, stats)
                    l = diff_dict[user]
                    l.append(stats['diff'])
                    diff_dict[user] = l

            #diff_dict['min_scale'] = min([min(v) for v in diff_dict.values()])

            return JsonResponse(data={'labels': labels, 'data': diff_dict, 'min_scale': min([min(v) for v in diff_dict.values()])}, status=200)
        except Exception as e:
            print ('Trend Data API failed: ', e)
            return JsonResponse({'key': 'Trend data error'}, status=401)

        
class SeasonStats(APIView):
    def post(self, request):
        start = datetime.datetime.now()
        try:
            data = {}
            #print ('DATA ', request.data)
            t= Tournament.objects.get(pk=request.data.get('tournament_key'))
            for espn_num in request.data.get('golfer_list'):
                g = Golfer.objects.get(espn_number=espn_num)
                data.update({g.espn_number: g.summary_stats(t.season)})
            print ('season stats api duration: ', datetime.datetime. now() - start)
            return JsonResponse(data, status=200)
        except Exception as e:
            print ('season stats exception: ', e)
            return JsonResponse({'msg': e})


class GetGolferLinks(APIView):
    def get(self, request, pk):
        start = datetime.datetime.now()
        
        try:
            data = {}
            #print ('DATA ', request.data)
            g = Golfer.objects.get(pk=pk)
            data.update({'pga_link': g.golfer_link(),
                        'espn_link': g.espn_link()})
            
            return JsonResponse(data, status=200)
        except Exception as e:
            print ('get golfer link exception: ', e)
            return JsonResponse({'msg': e})


class AuctionPickCreateView(LoginRequiredMixin,TemplateView):
     login_url = 'login'
     template_name = 'golf_app/auctionpick_form.html'
     

     def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
             't': Tournament.objects.get(current=True),
         })

        return context

     @transaction.atomic
     def post(self, request):

        data = json.loads(self.request.body)
        print (data, type(data))
        pick_list = data.get('pick_list')
        print ('pick_list', pick_list)
        tournament = Tournament.objects.get(current=True)
        #groups = Group.objects.filter(tournament=tournament)
        user = User.objects.get(username=request.user)

        if 'random' not in pick_list:
            if len(pick_list) != tournament.total_required_picks():
                print ('total picks match: ', len(pick_list), tournament.total_required_picks())
                msg = 'Something went wrong, wrong number of picks.  Expected: ' + str(tournament.total_required_picks()) + ' received: ' + str(len(pick_list)) + ' Please try again'
                response = {'status': 0, 'message': msg} 
                return HttpResponse(json.dumps(response), content_type='application/json')

            for group in Group.objects.filter(tournament=tournament):
                count = Field.objects.filter(group=group, pk__in=pick_list).count()
                if count == group.num_of_picks():
                    print ('group ok: ', group, ' : count: ', count)
                else:
                    print ('group ERROR: ', group, ' : count: ', count)
                    msg = 'Pick error: Group - ' + str(group.number) + ' expected' + str(group.num_of_picks()) + ' picks.  Actual Picks: ' + str(count)
                    response = {'status': 0, 'message': msg} 
                    return HttpResponse(json.dumps(response), content_type='application/json')

        print ('user', user)
        print ('started', tournament.started())

        if tournament.started() and tournament.late_picks is False:
            print ('picks too late', user, datetime.datetime.now())
            print (timezone.now())
            msg = 'Too late for picks, tournament started'
            response = {'status': 0, 'message': msg} 
            return HttpResponse(json.dumps(response), content_type='application/json')

        
        if Picks.objects.filter(playerName__tournament=tournament, user=user).count()>0:
            Picks.objects.filter(playerName__tournament=tournament, user=user).delete()
            ScoreDetails.objects.filter(pick__playerName__tournament=tournament, user=user).delete()

        if 'random' in pick_list:
            picks = tournament.create_picks(user, 'random')    
            print ('random picks submitted', user, datetime.datetime.now(), picks)
        else:
            field_list = []
            for id in pick_list:
                field_list.append(Field.objects.get(pk=id))                    
            tournament.save_picks(field_list, user, 'self')

        print ('user submitting picks', datetime.datetime.now(), request.user, Picks.objects.filter(playerName__tournament=tournament, user=user))
    
        if UserProfile.objects.filter(user=user).exists():
            profile = UserProfile.objects.get(user=user)
            if profile.email_picks:
                email_picks(tournament, user)

        #return redirect('golf_app:picks_list')
        msg = 'Picks Submitted'
        response = {'status': 1, 'message': msg, 'url': '/golf_app/picks_list'} 
        return HttpResponse(json.dumps(response), content_type='application/json')


class AuctionScores(APIView):
    def get(self, request):
        totals = {}
        try:
            start = datetime.datetime.now()
            score_dict = scrape_espn.ScrapeESPN().get_data()
            
            t = Tournament.objects.get(current=True)
            for u in User.objects.filter(username__in=['john', 'jcarl62', 'ryosuke']):
                totals[u.username] = {'total': 0}
            for i, pick in enumerate(AuctionPick.objects.filter(playerName__tournament=t)):
                sd = [v for v in score_dict.values() if v.get('pga_num') == pick.playerName.golfer.espn_number]
                print (pick, sd[0].get('rank'))
                
                if int(utils.formatRank(sd[0].get('rank'))) > score_dict.get('info').get('cut_num') or sd[0].get('rank') in t.not_playing_list():
                    total = totals[pick.user.username].get('total') + int(score_dict.get('info').get('cut_num'))
                    rank = rank = (score_dict.get('info').get('cut_num'))
                else:
                    total = totals[pick.user.username].get('total') + int(utils.formatRank(sd[0].get('rank')))
                    rank = utils.formatRank(sd[0].get('rank'))
                
                totals[pick.user.username].update({pick.playerName.playerName: 
                                                   {'rank': rank,
                                                   'score': sd[0].get('total_score')}
                                                    #'total': total
                                                    })
                totals[pick.user.username].update({'total': total})

        except Exception as e:
            totals['msg'] = {'error': e}

        print (totals)
        return JsonResponse(totals, status=200)


class GetGolfers(APIView):
    def get(self, request):
        start = datetime.datetime.now()
        
        try:
            golfers = golf_serializers.GolferSerializer(Golfer.objects.all(), many=True)
            
            #print ('DATA ', request.data)
            
            return Response(golfers.data, status=200)
        except Exception as e:
            print ('get golfers data exception: ', e)
            return JsonResponse({'msg': e})

