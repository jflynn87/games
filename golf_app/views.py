from venv import create
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from golf_app.models import CountryPicks, Field, Tournament, Picks, Group, TotalScore, ScoreDetails, \
           mpScores, BonusDetails, PickMethod, PGAWebScores, ScoreDict, UserProfile, \
           Season, AccessLog, Golfer, AuctionPick, CountryPicks, FedExField, FedExSeason, FedExPicks
from golf_app.forms import  CreateManualScoresForm, FieldForm, FieldFormSet, AuctionPicksFormSet
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpRequest, HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
import datetime
from golf_app import populateField, manual_score, withdraw, scrape_espn, \
     mp_calc_scores, golf_serializers, utils, olympic_sd, espn_api, \
     ryder_cup_scores, espn_ryder_cup, bonus_details, espn_schedule, scrape_scores_picks, \
     scrape_cbs_golf 

from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Min, Q, Count, Sum, Max
import scipy.stats as ss
from django.http import JsonResponse
import json
import random
from django.db import transaction
import urllib.request
import csv
from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from django.core.mail import send_mail
from django.core import serializers
from collections import OrderedDict
import numpy as np


class FieldListView1(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'golf_app/field_list_1.html'

    def get_context_data(self, **kwargs):
        context = super(FieldListView1, self).get_context_data(**kwargs)
        start = datetime.datetime.now()
        utils.save_access_log(self.request, 'new_picks')
        try:
            tournament = Tournament.objects.get(current=True)
        except Exception:
            tournament = None

        # espn = espn_api.ESPNData(update_sd=False)

        # started_golfers = []
        # lock_groups = []
        # if not espn.started() or tournament.late_picks:
        #     t_started = False
        # else:
        #     t_started = espn.started()
        #     started_golfers = espn.started_golfers_list()
        #     for g in Group.objects.filter(tournament=tournament):
        #         if g.lock_group(espn, self.request.user):
        #             lock_groups.append(g.number) 

        # picks = Picks.objects.filter(playerName__tournament=tournament, user=self.request.user).values_list('playerName__pk', flat=True)
        # field = serializers.serialize('json', Field.objects.filter(tournament=tournament))
        # espn_nums = Field.objects.filter(tournament=tournament).values_list('golfer__espn_number', flat=True)
        # golfers = serializers.serialize('json', Golfer.objects.filter(espn_number__in=espn_nums))        

        context.update({
            'tournament': tournament,
            'fedex_season': FedExSeason.objects.get(season=tournament.season)
            #'t_started': t_started,
            #'picks': picks,
            #'started_golfers': started_golfers,
            #'field': Field.objects.filter(tournament=tournament, group__number=1),
            #'field': field,
            #'golfers': golfers,
            #'info':  json.dumps(get_info(tournament)),
            #'lock_groups': lock_groups,
            #'groups': Group.objects.filter(tournament=tournament),
            
        })

        print ('new field 1 context dur: ', datetime.datetime.now() - start)
        return context


class NewFieldListView(LoginRequiredMixin,TemplateView):
    login_url = 'login'
    template_name = 'golf_app/field_list_a.html'
    model = Field
    #redirect_field_name = 'next'

    def get_context_data(self,**kwargs):
        context = super(NewFieldListView, self).get_context_data(**kwargs)
        utils.save_access_log(self.request, 'picks')
        try:
            tournament = Tournament.objects.get(current=True)
        except Exception:
            t = Tournament.objects.all().order_by('-pk').first()
            if t.pga_tournament_num == '999':
                tournament=Tournament.objects.get(season__current=True, pga_tournament_num='999')
            else: tournament = None

        context.update({
        #'field_list': Field.objects.filter(tournament=Tournament.objects.get(current=True)),
        'tournament': tournament,
        'groups': Group.objects.filter(tournament=tournament)
        #'error_message': error_message
        })
        return context

    @transaction.atomic
    def post(self, request):
        start = datetime.datetime.now()
        data = json.loads(self.request.body)
        print ('start of picks submit: ', request.user, data)
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

        if tournament.started() and not tournament.late_picks:
            espn = espn_api.ESPNData()
            msg = 'Golfer already palying: '
            error = False
            for p in pick_list:
                if not Picks.objects.filter(playerName__pk=p).exists():  #only check new picks, front end should prevent new picks so just a saftey net
                    f = Field.objects.get(pk=p)
                    if espn.player_started(f.golfer.espn_number):
                        print ('picked started golfer: ', self.request.user, f)
                        msg = msg + ' ' + f.playerName 
                        error = True
            if error:
                response = {'status': 0, 'message': msg} 
                return HttpResponse(json.dumps(response), content_type='application/json')
            
        
        print ('user', user)
        print ('started', tournament.started())

        # if tournament.started() and tournament.late_picks is False:
        #     print ('picks too late', user, datetime.datetime.now())
        #     print (timezone.now())
        #     msg = 'Too late for picks, tournament started'
        #     response = {'status': 0, 'message': msg} 
        #     return HttpResponse(json.dumps(response), content_type='application/json')

        
        if Picks.objects.filter(playerName__tournament=tournament, user=user).count()>0:
            Picks.objects.filter(playerName__tournament=tournament, user=user).delete()
            ScoreDetails.objects.filter(pick__playerName__tournament=tournament, user=user).delete()

        if CountryPicks.objects.filter(user=user, tournament=tournament).count() > 0:
            CountryPicks.objects.filter(user=user, tournament=tournament).delete()

        if 'random' in pick_list:
            picks = tournament.create_picks(user, 'random')    
            print ('random picks submitted', user, datetime.datetime.now(), picks)
        else:
            field_list = []
            for id in pick_list:
                field_list.append(Field.objects.get(pk=id))                    
            tournament.save_picks(field_list, user, 'self')
        
        if tournament.pga_tournament_num == '999':
            for mens_pick in  data.get('men_countries'):
                cp = CountryPicks()
                cp.user = user
                cp.tournament = tournament
                cp.country = mens_pick
                cp.gender = "men"
                cp.save()

            for womens_pick in  data.get('women_countries'):
                cp = CountryPicks()
                cp.user = user
                cp.tournament = tournament
                cp.country = womens_pick
                cp.gender = 'women'
                cp.save()

        if tournament.pga_tournament_num == '468':  #Ryder Cup
            cp = CountryPicks()
            cp.user = user
            cp.tournament = tournament
            cp.country = data.get('ryder_cup')[0]
            cp.ryder_cup_score = data.get('ryder_cup')[1]
            cp.gender = 'men'
            cp.save()
            

        print ('user submitting picks', datetime.datetime.now(), request.user, Picks.objects.filter(playerName__tournament=tournament, user=user))
        print ('submit picks duration: ',  datetime.datetime.now() - start)
    
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


def fedex_email_picks(user):
    try:
        mail_picks = "\r"
        for pick in FedExPicks.objects.filter(pick__season__season__current=True, user=user):
            mail_picks = mail_picks + 'Group: ' + str(pick.pick.golfer.golfer_name) + "\r"

        mail_sub = "Golf Game FEDEX Picks Submittted: " + user.username
        mail_t = "Old FedEx Picks: " + user.username + "\r"
        

        mail_url = "Website to make changes or picks: " + "http://jflynn87.pythonanywhere.com"
        mail_content = mail_t + "\r" + "\r" +mail_picks + "\r"+ mail_url
        # change address to user if they want it
        mail_recipients = ["jflynn87@hotmail.com"]
        send_mail(mail_sub, mail_content, 'jflynn87g@gmail.com', mail_recipients)  #add fail silently
    except Exception as e:
        print ('FEDEX Email picks error', e)
    
    return




class ScoreGetPicks(ListAPIView):
    serializer_class = golf_serializers.ScoreDetailsSerializer

    def get_queryset(self, *args, **kwargs):
        start = datetime.datetime.now()
        t = Tournament.objects.get(pk=self.kwargs.get('pk'))
        if self.kwargs.get('username') == 'all':
            #t = Tournament.objects.get(pk=self.kwargs.get('pk'))
            #u = User.objects.get(username=self.kwargs.get('username'))
            #queryset = ScoreDetails.objects.filter(pick__playerName__tournament=t, user=u)
            queryset = ScoreDetails.objects.filter(pick__playerName__tournament=t)
        elif self.kwargs.get('username') == 'only':
            self.serializer_class = golf_serializers.SDOnlySerializer
            queryset = ScoreDetails.objects.filter(pick__playerName__tournament=t)
        else:
            #t = Tournament.objects.get(pk=self.kwargs.get('pk'))
            u = User.objects.get(username=self.kwargs.get('username'))
            queryset = ScoreDetails.objects.filter(pick__playerName__tournament=t, user=u)

        print ('return serialized piks: ', datetime.datetime.now() - start)
        return queryset
           
class GetPicks(APIView):
    
    def get(self, num):
        start = datetime.datetime.now()
        t = Tournament.objects.get(current=True)
        try: 
            #picks = golf_serializers.PicksSerializer(Picks.objects.filter(user__username=self.request.user, playerName__tournament=t).exclude(playerName__withdrawn=True), many=True).data
            picks = serializers.serialize('json', Picks.objects.filter(user__username=self.request.user, playerName__tournament=t).exclude(playerName__withdrawn=True))
            print ('get picks duration: ', datetime.datetime.now() - start)            
            #return Response(json.dumps(picks), 200)
            return Response(picks, 200)
            #return Response(json.dumps(pick_list), 200)
        except Exception as e:
            print ('Get Picks API exception', e)
            return Response(json.dumps({'status': str(e)}), 500)
            


class PicksListView(LoginRequiredMixin,ListView):
    login_url = 'login'
    redirect_field_name = 'golf_app/pick_list.html'
    model = Picks

    def get_context_data(self,**kwargs):
        context = super(PicksListView, self).get_context_data(**kwargs)
        t = Tournament.objects.get(current=True)
        if t.pga_tournament_num == '999':  
            countries = CountryPicks.objects.filter(user=self.request.user, tournament=t)
        elif t.pga_tournament_num == '468':
            countries = CountryPicks.objects.filter(user=self.request.user, tournament=t)
        else:
            countries = None
        context.update({
        'tournament': Tournament.objects.get(current=True),
        'picks_list': Picks.objects.filter(playerName__tournament__current=True,user=self.request.user),
        'country_list': countries
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
            second_half_score_list = []  #added for Mark
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
                        winner_dict[winner.user] = winner_dict.get(winner.user) + 100/tournament.num_of_winners()
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
        #'totals_list': 
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

            pga_t_num = data.get('tid')
            
            try:
                espn_data = espn_schedule.ESPNSchedule()
                espn_sched = espn_data.get_event_list()

                espn_curr_event = espn_data.current_event()[0]
                espn_t_num = espn_curr_event.get('link').split('=')[1]
            except Exception as e:
                print ('setup current event exception', e)
                espn_curr_event = []
                espn_t_num = ''
                espn_data = {}
                espn_sched = {}

            

            return render(request, 'golf_app/setup.html', {'status': data,
                                                            'tournament': t,
                                                            'espn_sched': espn_sched,
                                                            'curr_event': espn_curr_event,
                                                            'espn_t_num': espn_t_num,
                                                            'pga_t_num': pga_t_num,
                                                            'first_golfer': Golfer.objects.first(),
                                                            'last_golfer': Golfer.objects.last()})
        else:
           return HttpResponse('Not Authorized')
    #moving this to separate API functinos to break apart 
    if request.method == "POST":
        url_number = request.POST.get('tournament_number')
        espn_num = request.POST.get('espn_t_num')
        print (url_number, type(url_number))
        print ('espn_t_num: ', espn_num)
        #if url_number == '470':  #Match Play special logic
        #    populateMPField.create_groups(url_number)
        #    return HttpResponseRedirect(reverse('golf_app:field'))
        try:
            if Tournament.objects.filter(pga_tournament_num=str(url_number), season__current=True).exists():
                error_msg = ("tournament already exists" + str(url_number))
                return render(request, 'golf_app/setup.html', {'error_msg': error_msg})
            else:
                print ('creating field A')
                populateField.create_groups(url_number, espn_num)
                return HttpResponseRedirect(reverse('golf_app:new_field_list'))
        except ObjectDoesNotExist:
            print ('obj does not exist exept - creating field')
            populateField.create_groups(url_number, espn_num)
            return HttpResponseRedirect(reverse('golf_app:new_field_list'))
        except Exception as e:
            print ('error', e)
            error_msg = (e)
            return render(request, 'golf_app/setup.html', {'error_msg': error_msg})


class AboutView(TemplateView):
    template_name='golf_app/about.html'


class GetScores(APIView):
   
    def get(self, request, tournament):
        
        #print ('GetScores API VIEW', self.request.GET.get('tournament'))
        #t = Tournament.objects.get(pk=self.request.GET.get('tournament'))
        if tournament:
            t = Tournament.objects.get(pk=tournament)
        else:
            t = Tournament.objects.get(current=True)

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


        if (t.current and not t.complete) or t.pga_tournament_num == '999':
            print ('scraping')
            if t.pga_tournament_num == '470': 
                return HttpResponse('Wrong link, use MP link')
            elif t.pga_tournament_num == '018':
                score_dict = scrape_cbs_golf.ScrapeCBS().get_data()
            elif t.pga_tournament_num == '999':
                score_dict = olympic_sd.OlympicScores().get_sd()
                print ('Olympic score dict: ', score_dict)
            else:
                score_dict = scrape_espn.ScrapeESPN(setup=True).get_data()
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
        print ('XXXXXX', score_dict.get('info'), t.started())
        if len(score_dict) == 0: 
            #(score_dict.get('info').get('round') == 1 and score_dict.get('info').get('round_status') == 'Not Started'):
            print ('score_dict empty', score_dict.get('info'))
            for sd in ScoreDetails.objects.filter(pick__playerName__tournament=t):
                sd.sod_position = ' '
                sd.save()
            return Response(({}), 200)
        
        if (t.current and len(score_dict) != 0) or t.pga_tournament_num == '999':
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
        totals = Season.objects.get(season=int(t.season.season)).get_total_points()
        print ("TOTALS ", totals)
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
            if sd.pick_data:
                display_data = json.loads(sd.pick_data)
            else:
                display_data = ''

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
                print ('no db scores returnng empty dicts')
                # return Response(({'picks': ' ',
                #                 'totals': ' ',
                #                 'leaders': ' ', 
                #                 'cut_line': ' ',
                #                 'optimal': ' ', 
                #                 'scores': ' ',
                #                 'season_totals': ' ',
                #                 'info': json.dumps(info),
                #                 't_data': ' ',
                #                 'round_status': ' '
                # }), 200)
                return Response({})
                
               
        except Exception as e:
            print ('old logic', e)
            return (redirect('golf_app:get_scores'), num)
            #GetScores().get(self.request)
            #return Response({}, 200)

class NewScoresView(LoginRequiredMixin,TemplateView):  #changed from ListView 1/5/2022
    login_url = 'login'
    template_name = 'golf_app/scores.html'
    #queryset = Picks.objects.filter(playerName__tournament__current=True) 

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
           for user in tournament.season.get_users('obj'):
               count = Picks.objects.filter(playerName__tournament=tournament, user=user).aggregate(Count('playerName'))
               print ('count: ', count)
               user_dict[user.username]=count.get('playerName__count')

           self.template_name = 'golf_app/pre_start.html'

           context.update({'user_dict': user_dict,
                           'tournament': tournament,
                          # 'lookup_errors': scores[4],
                                                    })

           return context
        ## from here all logic should only happen if tournament has started
        if not tournament.complete and not tournament.picks_complete():
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


class OlympicScoresView(LoginRequiredMixin,ListView):
    login_url = 'login'
    template_name = 'golf_app/olympic_scores.html'
    queryset = Picks.objects.filter(playerName__tournament__pga_tournament_num='999', playerName__tournament__season__current=True) 

    def get_context_data(self, **kwargs):
        context = super(OlympicScoresView, self).get_context_data(**kwargs)
        start = datetime.datetime.now()
        if self.request.user.is_authenticated:
            utils.save_access_log(self.request, 'olympic current week scores')

#        if self.kwargs.get('pk') != None:
#            print (self.kwargs)
#            tournament = Tournament.objects.get(pk=self.kwargs.get('pk'))
#        else:
        tournament = Tournament.objects.get(pga_tournament_num='999', season__current=True)
        
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
        # comment out in hopes all submit
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

    def get(self, request, pk):
        #print ('PK :: ', pk)
        #print (self.request.GET)
        try:
            info_dict = {}
            #t = Tournament.objects.get(pk=self.request.GET.get('tournament'))
            t = Tournament.objects.get(pk=pk)
            total_picks = 0

            for g in Group.objects.filter(tournament=t):
                info_dict[g.number] = g.num_of_picks()
                total_picks += g.num_of_picks()
            info_dict['total'] = total_picks
            #info_dict['started'] = t.started()

            #info_dict['complete'] = t.complete

            #print ('info dict class', info_dict)
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

        #info_dict['complete'] = t.complete
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
            print ('WD Check error: ', e)
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
        # try:
        #     data = {}
        #     data['users'] = {}
        #     user_list = []
        #     t = Tournament.objects.get(pk=pk)
        #     #t = Tournament.objects.get(current=True)
        #     users = t.season.get_users()
        #     for user in users:
        #         data['users'].update({
        #                              user.get('user'): str(User.objects.get(pk=user.get('user')))
        #         })
        #         user_list.append(user.get('user'))
        #     #data['users'] = user_list
        #     score_dict = scrape_espn.ScrapeESPN().get_data()            
        #     optimal_picks = {}
        #     score = manual_score.Score(score_dict, t)
        #     for g in Group.objects.filter(tournament=t):
        #         opt = score.optimal_picks(g.number)
        #         optimal_picks[str(g.number)] = {
        #                                         'golfer': opt[0],
        #                                         'rank': opt[1],
        #                                         'cuts': opt[2],
        #                                         'total_golfers': g.playerCnt
        #         } 

        #     data['optimal_picks'] = optimal_picks
        #     data['score_dict'] = score_dict
        #     data['t_data'] = serializers.serialize("json", [t, ])
        #     data['info'] = get_info(t)
        #     data['season_totals'] = Season.objects.get(season=t.season).get_total_points()
        #     data['leaders'] = score.get_leader()
        #     #print (type(data))
        # except Exception as e:
        #     print ('espn score dict api error: ', e)
        #     data['msg'] = {'msg': str(e)}
                
        # return JsonResponse(data, status=200)


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
    def get(self, request):
        start = datetime.datetime.now()
        #context = {'espn_data': espn_data, 'user': self.request.user}
        try:
            t= Tournament.objects.get(current=True)
            data= golf_serializers.PreStartFieldSerializer(Field.objects.filter(tournament=t), many=True).data
        except Exception as e:
            print ('prior res get API error; ', e)
            data = json.dumps({'msg': str(e)})

        print ('prior result GET duration: ', datetime.datetime.now() - start)
        return JsonResponse(data, status=200, safe=False)

    
    def post(self, request):
        start = datetime.datetime.now()
        print ('PROIR RESULT api DATA: ', request.data)
        try:
            #g_num = group.split('-')[2]
            t= Tournament.objects.get(pk=request.data.get('tournament_key'), season__current=True)
            if not t.started() or request.data.get('no_api'):  #skip golfer started data/checks
                if request.data.get('group') == 'all':
                    data= golf_serializers.PreStartFieldSerializer(Field.objects.filter(tournament=t), many=True).data
                elif len(request.data.get('golfer_list')) == 0:
                    data= golf_serializers.PreStartFieldSerializer(Field.objects.filter(tournament=t, group__number=request.data.get('group')), many=True).data
                else:
                    data = golf_serializers.PreStartFieldSerializer(Field.objects.filter(tournament=t, golfer__espn_number__in=request.data.get('golfer_list')), many=True).data
            else:
                espn_data = espn_api.ESPNData()
                context = {'espn_data': espn_data, 'user': self.request.user}
                if request.data.get('group') == 'all':
                    data= golf_serializers.NewFieldSerializer(Field.objects.filter(tournament=t), context=context, many=True).data
                elif len(request.data.get('golfer_list')) == 0:
                    data= golf_serializers.NewFieldSerializer(Field.objects.filter(tournament=t, group__number=request.data.get('group')), context=context, many=True).data
                else:
                    data = golf_serializers.NewFieldSerializer(Field.objects.filter(tournament=t, golfer__espn_number__in=request.data.get('golfer_list')), context=context, many=True).data
        except Exception as e:
            print ('prior result api error: ', e) 
            data = json.dumps({'msg': str(e)})
                
        #return JsonResponse(data, status=200)
        print ('prior result duration Group: ', request.data.get('group'), datetime.datetime.now() - start)
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

    def get(self, request, pk):
        print ('MP API ')
        start = datetime.datetime.now()
        t = Tournament.objects.get(pk=pk)
        d = {}

        if t.complete:
            #sd = ScoreDict.objects.get(tournament=t)
            #score_dict = sd.data
            for u in t.season.get_users('obj'):
                total = TotalScore.objects.get(tournament=t, user=u)
                d[u.username] = {'score': total.score,
                                'cuts': 0}

            return JsonResponse(d, status=200, safe=False)
        else:
            espn = espn_api.ESPNData(t=t, force_refresh=True)
            round_data = espn.mp_golfers_per_round()

            TotalScore.objects.filter(tournament=t).update(score=0)

            for pick in Picks.objects.filter(playerName__tournament=t).values('playerName__golfer__espn_number').distinct():
                p = Picks.objects.filter(playerName__tournament=t, playerName__golfer__espn_number=pick.get('playerName__golfer__espn_number')).first()
                score = p.playerName.mp_calc_score(round_data, espn)

                ScoreDetails.objects.filter(pick__playerName__tournament=t, pick__playerName__golfer__espn_number=pick.get('playerName__golfer__espn_number')).update(score=score)
                for sd in ScoreDetails.objects.filter(pick__playerName__tournament=t, pick__playerName__golfer__espn_number=pick.get('playerName__golfer__espn_number')):
                    ts, created = TotalScore.objects.get_or_create(user=sd.user, tournament=t)
                    if created:
                        ts.score = 0
                    else:
                        ts.score = ts.score + score
                    ts.save()

                if espn.tournament_complete():
                    if score == 1:
                        for w in  Picks.objects.filter(playerName__tournament=t, playerName__golfer__espn_number=pick.get('playerName__golfer__espn_number')):
                            if not PickMethod.objects.filter(user=w.user, method=3, tournament=w.playerName.tournament).exists():
                                bd, created = BonusDetails.objects.get_or_create(user=w.user, tournament=w.playerName.tournament, bonus_type='1')
                                bd.bonus_points = 50
                                bd.save()
                                ts = TotalScore.objects.get(user=w.user, tournament=w.playerName.tournament)
                                ts.score = ts.score - 50
                                ts.save()
                    if score == 2:
                        for s in Picks.objects.filter(playerName__tournament=t, playerName__golfer__espn_number=pick.get('playerName__golfer__espn_number')):
                            if not PickMethod.objects.filter(user=s.user, method=3, tournament=s.playerName.tournament).exists():
                                bd, created = BonusDetails.objects.get_or_create(user=s.user, tournament=s.playerName.tournament, bonus_type='4')
                                bd.bonus_points = 25
                                bd.save()
                                ts = TotalScore.objects.get(user=s.user, tournament=s.playerName.tournament)
                                ts.score = ts.score - 25
                                ts.save()

            if espn.tournament_complete():
                t.complete = True
                t.save()
                for u in t.season.get_users('obj'):
                    if ScoreDetails.objects.filter(pick__playerName__tournament=t, pick__user=u, score=1).exists() and \
                        ScoreDetails.objects.filter(pick__playerName__tournament=t, pick__user=u, score=2).exists() and \
                        ScoreDetails.objects.filter(pick__playerName__tournament=t, pick__user=u, score=3).exists():
                        print ('MP Trifecta: ', u)
                        bd, created = BonusDetails.objects.get_or_create(user=w.user, tournament=t, bonus_type='6')
                        bd.bonus_points = 25
                        bd.save()
                        total = TotalScore.objects.get(tournament=t, user=u)
                        total.score = total.score - 25
                        total.save()

                winning_score = TotalScore.objects.filter(tournament=t).aggregate(Min('score'))
                print ('MP winning score: ', winning_score)
                winner = TotalScore.objects.filter(tournament=t, score=winning_score.get('score__min'))
                print ('match play', winner)
                for w in winner:
                    if not PickMethod.objects.filter(tournament=t, user=w.user, method=3).exists():
                        bd, created = BonusDetails.objects.get_or_create(user=w.user, tournament=t, bonus_type='3')
                        bd.bonus_points = 100/t.num_of_winners()
                        bd.save()
                        w.score = w.score - (100/t.num_of_winners())
                        w.save()

        for u in t.season.get_users('obj'):
            cuts = ScoreDetails.objects.filter(pick__user=u, pick__playerName__tournament=t, score=17).count()
            total = TotalScore.objects.get(tournament=t, user=u)
            d[u.username] = {'score': total.score,
                             'cuts': cuts}
        
        print ("MP Scores duration: ", datetime.datetime.now() - start)
        return JsonResponse(d, status=200, safe=False)

class MPRecordsAPI(APIView):
    
    def get(self, request, pk):
        #assumes that this is run after score api so no nee to re-get ESPN API
        try:
            d = {}
            t= Tournament.objects.get(pk=pk)
            sd = ScoreDict.objects.get(tournament=t)
            data = sd.espn_api_data
            espn = espn_api.ESPNData(t=t, data=data)
            records = espn.get_mp_records()
            for p in Picks.objects.filter(playerName__tournament=t):
                #p = Picks.objects.filter(playerName__golfer__espn_number=pick.get('playerName__golfer__espn_number'), playerName__tournament=t).first()
                d[p.pk] = espn.mp_golfer_results(p.playerName.golfer, records)

            return JsonResponse(d, status=200)
        
        #    data = {}
        #    #pk = request.GET.get('pk')
        #    t = Tournament.objects.get(pk=pk)
        #    #t = Tournament.objects.get(season__current=True, pga_tournament_num='470')
        #    data = scrape_scores_picks.ScrapeScores(t, 'https://www.pgatour.com/competition/' + str(t.season.season) + '/wgc-dell-technologies-match-play/group-stage.html').mp_brackets()
        #    print ('pm records: ', data)
        #    return JsonResponse(data, status=200)
        except Exception as e:
            print ('MP records API failed: ', e)
            return JsonResponse({'key': 'error'}, status=401)


class MPRankInGroup(APIView):
    
    def get(self, request, pk):
        #assumes that this is run after score api so no nee to re-get ESPN API
        try:
            d = {}
            t= Tournament.objects.get(pk=pk)
            sd = ScoreDict.objects.get(tournament=t)
            data = sd.espn_api_data
            espn = espn_api.ESPNData(t=t, data=data)
            for p in Picks.objects.filter(playerName__tournament=t):
                #p = Picks.objects.filter(playerName__golfer__espn_number=pick.get('playerName__golfer__espn_number'), playerName__tournament=t).first()
                r = espn.mp_group_rank(p.playerName)
                d[p.pk] = r.get(p.playerName.pk)

            return JsonResponse(d, status=200)
        
        #    data = {}
        #    #pk = request.GET.get('pk')
        #    t = Tournament.objects.get(pk=pk)
        #    #t = Tournament.objects.get(season__current=True, pga_tournament_num='470')
        #    data = scrape_scores_picks.ScrapeScores(t, 'https://www.pgatour.com/competition/' + str(t.season.season) + '/wgc-dell-technologies-match-play/group-stage.html').mp_brackets()
        #    print ('pm records: ', data)
        #    return JsonResponse(data, status=200)
        except Exception as e:
            print ('MP rank API failed: ', e)
            return JsonResponse({'key': 'error'}, status=400)


class TrendDataAPI(APIView):
    
    def get(self, request, season_pk, num_of_t):
        print (season_pk, num_of_t)
        try:
            labels = []
            #data = []
            diff_dict= {}
            
            season = Season.objects.get(pk=season_pk)

            for u in season.get_users('obj'):
                #u = User.objects.get(pk=user.get('user'))
                diff_dict[u.username] = []

            if num_of_t == "all":
                t_qs = Tournament.objects.filter(season__pk=season.pk).order_by('pk')
            else:
                t_qs = reversed(Tournament.objects.filter(season__pk=season.pk).order_by('-pk')[:int(num_of_t)])

            for t in t_qs:
                print (t)
                labels.append(t.name[0:8])
                totals = json.loads(t.season.get_total_points(t))
                print ('past totals')
                for user, stats in totals.items():
                    print (user, stats)
                    l = diff_dict[user]
                    l.append(stats['diff'])
                    diff_dict[user] = l
                    

            #diff_dict['min_scale'] = min([min(v) for v in diff_dict.values()])
            print ('diff_dict')
            return JsonResponse(data={'labels': labels, 'data': diff_dict, 'min_scale': min([min(v) for v in diff_dict.values()])}, status=200)
        except Exception as e:
            print ('Trend Data API failed: ', e)
            return JsonResponse({'key': 'Trend data error'}, status=200)

        
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
            data.update({'pga_link': g.get_pga_player_link(),
                        'espn_link': g.espn_link(),
                        'pic_link': g.pic_link,
                        'flag_link': g.flag_link
                        })
            print (data)
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
            golfers = golf_serializers.GolferSerializer(Golfer.objects.all(), many=True).data
            #golfers = serializers.serialize('json', Golfer.objects.all(), use_natural_foreign_keys=True)
            field = serializers.serialize('json', Field.objects.filter(tournament__current=True),  use_natural_foreign_keys=True)
            
            #data = {'golfers': golfers.data,
            data = {'golfers': golfers,
                    'field': field}

            return JsonResponse(data, status=200)
        except Exception as e:
            print ('get golfers data exception: ', str(e))
            return JsonResponse({'msg': str(e)})


class PicksSummaryData(APIView):
    def get(self, request, pk):
        data = {'total_picks': {},
                'by_player': {}}
        try:
            #t= Tournament.objects.get(pk=request.data.get('tournament_key'))
            t= Tournament.objects.get(pk=pk)
            picks = Picks.objects.filter(playerName__tournament=t).values('playerName__playerName').annotate(count=Count('playerName')).order_by('-count')
            for p in picks:
                data.get('by_player').update({p.get('playerName__playerName'): p.get('count')})
            data.get('total_picks').update(Picks.objects.filter(playerName__tournament=t).aggregate(Count('playerName', distinct=True)))
            #print ('picks API DATA: ', data)
            return JsonResponse(data)
        except Exception as e:
            print ('get pick summary exception: ', e)
            return JsonResponse({'msg': e})
            
class OlympicGolfersByCountry(APIView):
    
    def get(self, request):
        try:
            t = Tournament.objects.get(pga_tournament_num='999', season__current=True)
            d = t.get_country_counts()
            # sex = 'men'
            # d = {'men': {}, 'women': {}}
            # for f in Field.objects.filter(tournament=t):
            #     if f.playerName == "Nelly Korda":  #top ranked in 2021
            #         sex = 'women'
            #     country = f.golfer.flag_link.split('/')[9][0:3].upper()
            #     if country == "NIR":  #for Rory
            #         country = "IRL"
            #     if d.get(sex).get(country):
            #         d.get(sex).update({country: d.get(sex).get(country) +  1})
            #     else:
            #         d.get(sex).update({country: 1})
            return JsonResponse(d)
        except Exception as e:
            print ('get olympic get players by country exception: ', e)
            return JsonResponse({'msg': e})
    

class GetCountryPicks(APIView):
    def get(self,request, pga_t_num, user):
        print ('GETCOUNTRY API request', self.request.user, pga_t_num)
        t = Tournament.objects.get(pga_tournament_num=pga_t_num, season__current=True)
        try:
            if user == 'user':
               #data = serializers.serialize('json', CountryPicks.objects.filter(tournament=t, user=self.request.user),  use_natural_foreign_keys=True)
               data= golf_serializers.CountryPicks(CountryPicks.objects.filter(tournament=t, user=self.request.user), many=True).data
            else:
               #data = serializers.serialize('json', CountryPicks.objects.filter(tournament=t),  use_natural_foreign_keys=True)
               data= golf_serializers.CountryPicks(CountryPicks.objects.filter(tournament=t), many=True).data
        except Exception as e:
            print ('GET country picks exception: ', e)
            data = json.dumps({'msg': e})    
            
        return JsonResponse(data, status=200, safe=False)


class FedExPicksView(LoginRequiredMixin,TemplateView):
     login_url = 'login'
     template_name = 'golf_app/fedex_picks.html'
     

     def get_context_data(self,**kwargs):
        context = super(FedExPicksView, self).get_context_data(**kwargs)
        utils.save_access_log(self.request, 'fedex picks')
        context.update({
         'season': FedExSeason.objects.get(season__current=True),
                        })
        return context

     @transaction.atomic
     def post(self, request):
        if FedExPicks.objects.filter(user=self.request.user, pick__season__season__current=True).exists():
            print ('CHANGING FEDEX Picks', self.request.user)
            print ('old picks: ')
            for p in FedExPicks.objects.filter(user=self.request.user, pick__season__season__current=True):
                print (p, p.pick.golfer.golfer_name)
            fedex_email_picks(self.request.user)
        FedExPicks.objects.filter(user=self.request.user, pick__season__season__current=True).delete()
        data = json.loads(self.request.body)
        print ('pick list', data.get('pick_list'))
        msg = 'FedEx Picks Submitted'
        for p in data.get('pick_list'):
            pick = FedExPicks()
            pick.user = self.request.user
            pick.pick = FedExField.objects.get(season__season__current=True, pk=p)
            pick.save()
            
        response = {'status': 1, 'message': msg, 'url': '/golf_app/fedex_picks_list'} 
        return HttpResponse(json.dumps(response), content_type='application/json')


class FedExFieldAPI(APIView):
    def get(self, request, filter):

        s = FedExSeason.objects.get(season__current=True)

        if filter == 'all':
            users = serializers.serialize(queryset=s.season.get_users('obj'), format='json')
            picks = s.picks_by_golfer()
            data = {'picks': picks,
                    'users': users}
        else:            
            context = {'user': self.request.user}
            try:
                if s.season.season == 2022 and self.request.user.username == "Hiro":
                    t = Tournament.objects.get(season__season='2022', name='Hero World Challenge')
                    top_30 = {k:v for k,v in t.fedex_data.items() if k != 'player_points' and int(v.get('rank')) <= 30}
                    exclude_rank = 50

                    exclude_list = []
                    for k, v in top_30.items():
                        if FedExField.objects.filter(golfer__golfer_name=k, soy_owgr__gte=exclude_rank).exists():
                            f = FedExField.objects.get(golfer__golfer_name=k)
                            exclude_list.append(f.pk)

                    data= golf_serializers.FedExFieldSerializer(FedExField.objects.filter(season=s).exclude(pk__in=exclude_list).order_by('soy_owgr'), context=context, many=True).data
                else:
                    data= golf_serializers.FedExFieldSerializer(FedExField.objects.filter(season=s).order_by('soy_owgr'), context=context, many=True).data
                #data= golf_serializers.FedExFieldSerializer(FedExField.objects.filter(season=s).order_by('soy_owgr'), many=True).data
            except Exception as e:
                print ('FedEx Field API exception: ', e)
                data = json.dumps({'msg': e})    
            
        return JsonResponse(data, status=200, safe=False)


class  SeasonPointsAPI(APIView):
    def get(self, request, season, filter):

        s = Season.objects.get(pk=season)

        if filter == 'all':
            #data = s.player_points()
            data = s.get_total_points()
        else:            
            data = s.player_points(self.request.user)
            
        return JsonResponse(data, status=200, safe=False)


class FedExPicksListView(LoginRequiredMixin,ListView):
    login_url = 'login'
    #redirect_field_name = 'golf_app/fedex_pick_list.html'
    model = FedExPicks
    template_name = 'golf_app/fedex_picks_list.html'

    def get_context_data(self,**kwargs):
        context = super(FedExPicksListView, self).get_context_data(**kwargs)

        context.update({
         'picks_list': FedExPicks.objects.filter(user=self.request.user, pick__season__season__current=True),
                        })
        return context


class FedExPicksAPI(APIView):
    def get(self, request, fedex_season, filter):
        start = datetime.datetime.now()
        f_season = FedExSeason.objects.get(pk=fedex_season)

        d = {}
        print (filter)
        try:
            if filter == 'by_user':
                print ('IN BY USER')
                data = list(FedExPicks.objects.filter(pick__season=f_season, user=self.request.user).values_list('pick__golfer__pk', flat=True))
                d['data'] = data
                print ('FEDEX: ', d)
            else:
                for p in FedExPicks.objects.filter(pick__season=fedex_season):
                    if d.get(p.user.username):
                        d.get(p.user.username).update({p.pick.golfer.espn_number: {'golfer_name': p.pick.golfer.golfer_name,
                                                                                    'score': p.score}})
                    else:
                        d[p.user.username] = {p.pick.golfer.espn_number: {'golfer_name': p.pick.golfer.golfer_name,
                                                                    'score': p.score}}
        except Exception as e:
            print ('FedExPicksAPI error: ', e)
            d['error'] = {'msg': str(e)}
        
        
        print ('duration FEDEXpicks API: ', datetime.datetime.now() - start)
        return JsonResponse(d, status=200, safe=False)







class PriorYearStatsAPI(APIView):

    def get(self, request):
        pass

class RyderCupScoresView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name= 'golf_app/ryder_cup_scores.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        s = Season.objects.get(current=True)
        t = Tournament.objects.get(pga_tournament_num='468', season=s)
        

        context.update({
             't': t,

         })

        return context


class RyderCupScoresAPI(APIView):
    def get(self,request):
        
        s = Season.objects.get(current=True)
        t = Tournament.objects.get(season=s, pga_tournament_num='468')
        if t.complete:
            sd = ScoreDict.objects.get(tournament=t)
            score_dict = espn_ryder_cup.ESPNData(data=sd.data).field()
        else:
            score_dict = espn_ryder_cup.ESPNData().field()

        scores = ryder_cup_scores.Score(score_dict).update_scores()
        totals = ryder_cup_scores.Score(score_dict).total_scores()
        print ('view totals: ', totals)
        
        try:
            data = {}
            data['score_dict'] = score_dict
            data['field'] = {}
            #for f in Field.objects.filter(tournament=t):
            #    data['field'].update({f.golfer.espn_number: f.playerName})

            for u in s.get_users():
                
                user = User.objects.get(pk=u.get('user'))
                print (user, totals.get(user.username))
                cp = CountryPicks.objects.get(tournament=t, user=user)
                picks = Picks.objects.filter(playerName__tournament=t, user=user).order_by('playerName__group__number')
                data[user.username] = {'c_pick': cp.country,
                                       'c_points':  cp.ryder_cup_score}
                for bd in BonusDetails.objects.filter(user=user, tournament=t):
                    if data.get(user.username).get('bonus'):
                        data.get(user.username).get('bonus').update({bd.get_bonus_type_display(): bd.bonus_points})
                    else:
                        data[user.username]['bonus'] = {bd.get_bonus_type_display(): bd.bonus_points}
                for pick in picks:
                    sd = ScoreDetails.objects.get(user=user, pick=pick)
                    score = sd.score
                    data[user.username].update({
                                                'total_score': totals.get(user.username).get('total_score'),
                                                'group_' +  str(pick.playerName.group.number): pick.playerName.playerName,
                                                'flag_' + str(pick.playerName.group.number): pick.playerName.golfer.flag_link,
                                                'pic_' + str(pick.playerName.group.number): pick.playerName.golfer.pic_link,
                                                'score_' + str(pick.playerName.group.number): score,
                    })

        except Exception as e:
            print ('Ryder Cup scrores API exception: ', e)
            data = json.dumps({'msg': e})    
            
        return JsonResponse(data, status=200, safe=False)


class ApiScoresView(LoginRequiredMixin, TemplateView):

    login_url = 'login'
    template_name= 'golf_app/scores_api.html'

    def get_context_data(self, **kwargs):
        context = super(ApiScoresView, self).get_context_data(**kwargs)
        start = datetime.datetime.now()
        if self.request.user.is_authenticated:
            utils.save_access_log(self.request, 'API current week scores')
        print (self.kwargs)
        if self.kwargs.get('pk') != None:
            print (self.kwargs)
            tournament = Tournament.objects.get(pk=self.kwargs.get('pk'))
        else:
            tournament = Tournament.objects.get(current=True)
        
        if not tournament.started():
           user_dict = {}
           for user in tournament.season.get_users('obj'):
               count = Picks.objects.filter(playerName__tournament=tournament, user=user).aggregate(Count('playerName'))
               print ('count: ', count)
               user_dict[user.username]=count.get('playerName__count')

           self.template_name = 'golf_app/pre_start.html'

           context.update({'user_dict': user_dict,
                           'tournament': tournament,
                                                    })

           return context

        ## from here all logic should only happen if tournament has started
        if not tournament.complete and not tournament.picks_complete():
               print ('picks not complete')
               tournament.missing_picks()

        new_lines = []
        picks_c = Picks.objects.filter(playerName__tournament=tournament).count()
        users = Picks.objects.filter(playerName__tournament=tournament).values('user__username').distinct().count()
        
        cells_per_row = picks_c / users
        #print (cells_per_row)

        for i in range(picks_c):
    
            if i % cells_per_row == 1:
                new_lines.append(i)
        #ts = TotalScore.objects.filter(tournament=tournament).order_by('score')    
        #print ('TOTAL SCORES: ', Picks.objects.filter(playerName__tournament=tournament).order_by(ts, 'playerName__group__number'))
        context.update({'t': tournament, 
                        'groups': Group.objects.filter(tournament=tournament),
                        'picks': Picks.objects.filter(playerName__tournament=tournament).order_by('user', 'playerName__group__number'),
                        #'ts': ts,
                        'new_lines': new_lines,
                        
                                    })
        print ('api scores context duration', datetime.datetime.now() -start)
        return context        



class EspnApiScores(APIView):
    @transaction.atomic
    def get(self, request, pk):
        start = datetime.datetime.now()
        d = {}
        try:

            t = Tournament.objects.get(pk=pk)
            if not t.started():
                return JsonResponse({'msg': 'Tournament Not Started'}, status=200, safe=False)

            for u in t.season.get_users('obj'):
                d[u.username] = {'score': 0,
                                'cuts': 0}

            if t.complete:
                data = return_sd_data(t,d)
                print ("Tournament Complete dur: ", datetime.datetime.now() - start)
                return JsonResponse(data, status=200, safe=False)

            espn = espn_api.ESPNData(t=t, force_refresh=True, update_sd=False)

            #if not espn.needs_update():
            #    data = return_sd_data(t,d)
            #    print ('API update not required, returning SD data dur: ', datetime.datetime.now() - start)
            #    return JsonResponse(data, status=200, safe=False)

            start_big = datetime.datetime.now()
            big = espn.group_stats()
            print ('big dur ', datetime.datetime.now() - start_big)

            start_calc_score  = datetime.datetime.now()
            cut_num = espn.cut_num()
            
            BonusDetails.objects.filter(tournament=t, bonus_type='5').update(bonus_points=0)

            for golfer in Picks.objects.filter(playerName__tournament=t).values('playerName__golfer__espn_number').distinct():
                pick = Picks.objects.filter(playerName__tournament=t, playerName__golfer__espn_number=golfer.get('playerName__golfer__espn_number')).first()
                score = pick.playerName.calc_score(api_data=espn)
                #print (pick, score)

                bonus = 0

                bd = bonus_details.BonusDtl(espn_api=espn, espn_scrape_data=None, tournament=t, inquiry=False)  
                bd_big = bd.best_in_group(big, pick)
                if bd_big:
                    print ('BIG: ', pick, bonus)
                    bonus += 10
                if bd.winner(pick):
                    bonus += bd.winner_points(pick)
                if espn.tournament_complete() and espn.playoff():
                    if bd.playoff_loser(pick):
                        bonus += 25

                for p in Picks.objects.filter(playerName__tournament=t, playerName__golfer__espn_number=pick.playerName.golfer.espn_number):
                    if score.get('cut'):
                        d.get(p.user.username).update({'cuts': d.get(p.user.username).get('cuts') + 1})
                    if PickMethod.objects.filter(user=p.user, method__in=[1,2], tournament=t).exists():
                        d.get(p.user.username).update({'score': d.get(p.user.username).get('score') + ((score.get('score') - bonus))})
                    else:
                        d.get(p.user.username).update({'score': (d.get(p.user.username).get('score') + score.get('score'))})

                rank = espn.get_rank(pick.playerName.golfer.espn_number)
                golfer_data = espn.golfer_data(pick.playerName.golfer.espn_number)
                
                if rank in t.not_playing_list():
                    today_score = rank
                    gross_score = cut_num  #should just use the score from model calc_score i think
                else:
                    today_score = ''  #fix this, but does it matter?
                    gross_score = rank
                
                thru = espn.get_thru(pick.playerName.golfer.espn_number)
                
                #if golfer_data:
                if golfer_data.get('statistics') and len(golfer_data.get('statistics')) >0:
                    to_par = golfer_data.get('statistics')[0].get('displayValue')
                    sod_position = golfer_data.get('movement')
                else:
                    to_par = ''
                    sod_position = ''
                
                sd = ScoreDetails.objects.filter(pick__playerName__tournament=t, pick__playerName=pick.playerName).update(  
                                    today_score=today_score,
                                    thru = thru,
                                    gross_score=gross_score,
                                    score=score.get('score'),
                                    toPar = to_par,
                                    sod_position=sod_position
                )


                #print ('score check: ', d.get('jcarl62'), pick, score)
            if bd.no_cut_exists():
                no_cuts = bd.update_cut_bonus()
                for u, b in no_cuts.items():
                    d.get(u.username).update({'score': d.get(u.username).get('score') - b})   

            if espn.tournament_complete():
                t.complete = True
                t.save()
                overall_bd = bonus_details.BonusDtl(espn, t)

                for username in d.keys():
                    u = User.objects.get(username=username)
                    if overall_bd.trifecta(u):
                        d.get(username).update({'score': d.get(username).get('score') - 50})   

                winner_list = overall_bd.weekly_winner(d)
                print ('winners ', winner_list)
                for winner in winner_list:
                    d.get(winner).update({'score': d.get(winner).get('score') - overall_bd.weekly_winner_points()})
            for username in d.keys():
                user = User.objects.get(username=username)
                ts, created = TotalScore.objects.get_or_create(user=user, tournament=t)
                ts.score = d.get(ts.user.username).get('score')
                ts.cut_count = d.get(ts.user.username).get('cuts')
                ts.save()

            d['group_stats'] = {}
            d.get('group_stats').update(big)

            print ('calc score dur: ', datetime.datetime.now() - start_calc_score)
        
        except Exception as e:
            print ('ESPN SCORES API EXCEPTION: ', e)
            d['error'] = {'source': 'EspnApiScores',
                          'msg': str(e)} 
        print (d)    
        print ('update scores full process total time: ', datetime.datetime.now() - start)
        return JsonResponse(d, status=200, safe=False)

def return_sd_data(t,d):
    start = datetime.datetime.now()
    for ts in TotalScore.objects.filter(tournament=t):
        d.get(ts.user.username).update({'score': ts.score, 'cuts': ts.cut_count})
    
    if t.good_api_data():  #espn api data is good from the Amex
        sd = ScoreDict.objects.get(tournament=t)
        espn_data = sd.espn_api_data
        espn = espn_api.ESPNData(t=t, data=espn_data)
        d['group_stats'] = espn.group_stats()
    else:
        sd = ScoreDict.objects.get(tournament=t)
        if not sd.data_valid():
            sd.update_sd_data()

        data =json.loads(sd.pick_data)
        optimal = json.loads(data.get('display_data').get('optimal'))
        d['group_stats'] = {}

        for k, v in optimal.items():
            d.get('group_stats').update({str(k): {'golfers': [],
                        'golfer_espn_nums': [],
                        'cuts': v.get('cuts'),
                        'total_golfers': v.get('total_golfers')}
                        })
            print (v.get('golfer'))
            for num, name in v.get('golfer').items():
                d.get('group_stats').get(str(k)).get('golfer_espn_nums').append(num)
                d.get('group_stats').get(str(k)).get('golfers').append(name)

    print ('return SD data dur: ', datetime.datetime.now() - start)

    return d
    



class AllTimeView(TemplateView):
    template_name='golf_app/all_time.html'

    def get_context_data(self, **kwargs):
        context = super(AllTimeView, self).get_context_data(**kwargs)
        utils.save_access_log(self.request, 'all time')
        context.update({
            'users': Season.objects.get(current=True).get_users('obj'),
            'seasons': Season.objects.all()
        })

        return context
 

class TotalPlayedAPI(APIView):
    def get(self, request, season):
        
        start = datetime.datetime.now()
        d = {}

        if season == 'all':
            s = Season.objects.get(current=True)
        else:
            s = Season.objects.get(pk=season)
        try:
            for u in s.get_users('obj'):
                if season == 'all':
                    d[u.username] = {'played': TotalScore.objects.filter(user=u).exclude(score=999).count()}
                else:
                    d[u.username] = {'played': TotalScore.objects.filter(user=u, tournament__season=s).exclude(score=999).count()}
        except Exception as e:
            print ('total played API error: ', e)
            d['error'] = {'msg': e}
        
        print ('total played API time: ', datetime.datetime.now() - start)

        return JsonResponse(json.dumps(d), status=200, safe=False)


class TWinsAPI(APIView):
    def get(self, request, season):
        
        start = datetime.datetime.now()
        d = {}
        try:
            if season == 'all':
                tournaments = Tournament.objects.all()
            else:
                tournaments = Tournament.objects.filter(season__pk=season)
            
            for t in tournaments:
                for ts in t.winner():
                    try: 
                       d.get(ts.user.username).update({'weekly_winner': d.get(ts.user.username).get('weekly_winner') + 1,
                         })
                    except Exception as a:
                         d[ts.user.username] = {'weekly_winner': 1,
                         }
        
        except Exception as e:
            print ('T wins API error: ', e)
            d['error'] = {'msg': str(e)}

        print ('t wins API time: ', datetime.datetime.now() - start)

        return JsonResponse(json.dumps(d), status=200, safe=False)


class PickedWinnerCountAPI(APIView):
    def get(self, request, season):
        
        start = datetime.datetime.now()
        d = {}

        if season == 'all':
            s = Season.objects.get(current=True)
        else:
            s = Season.objects.get(pk=season)

        try:
            if season == 'all':
                for u in s.get_users('obj'):
                    d[u.username] = {'winner_count': ScoreDetails.objects.filter(user=u, score=1).count()}
            else:
                for u in s.get_users('obj'):
                    d[u.username] = {'winner_count': ScoreDetails.objects.filter(user=u, score=1, pick__playerName__tournament__season=s).count()}

        except Exception as e:
            print ('Picked winner count API error: ', e)
            d['error'] = {'msg': str(e)}

        print ('picked winner count API time: ', datetime.datetime.now() - start)

        return JsonResponse(json.dumps(d), status=200, safe=False)


class AvgPointsAPI(APIView):
    def get(self, request, season):
        
        start = datetime.datetime.now()
        d = {}
        try:
            if season == 'all':
                tournaments = Tournament.objects.all().order_by('pk')
            else:
                tournaments = Tournament.objects.filter(season=Season.objects.get(pk=season)).order_by('pk')
            for t in tournaments:
                for ts in TotalScore.objects.filter(tournament=t).order_by('score'):
                    if ts.score != 999:
                        try:
                            d.get(ts.user.username).update({'played': d.get(ts.user.username).get('played') + 1,
                                                'total_score': d.get(ts.user.username).get('total_score') + ts.score,
                                 })

                        except Exception as e:

                            d[ts.user.username] = {'played': 1,
                            'total_score':ts.score,
                            }

            #print (d)
            for user, data in d.items():
                d.get(user).update({'average': round(d.get(user).get('total_score')/d.get(user).get('played'), 0)})

        except Exception as e:
            print ('Avg points API error: ', e)
            d['error'] = {'msg': str(e)}

        print ('avg points API time: ', datetime.datetime.now() - start)

        return JsonResponse(json.dumps(d), status=200, safe=False)


class AvgCutsAPI(APIView):
    def get(self, request, season):
        
        start = datetime.datetime.now()
        d = {}

        try:
            if season == 'all':
                s = Season.objects.get(current=True)
                tournaments = Tournament.objects.filter(has_cut=True).order_by('pk')
            else:
                s = Season.objects.get(pk=season)
                tournaments = Tournament.objects.filter(season=s, has_cut=True).order_by('pk')

            for u in s.get_users('obj'):
                d[u.username] = {'played': 0,
                                'cuts': 0,
                                }

            for t in tournaments:
                if not TotalScore.objects.filter(tournament=t, cut_count__gte=1).exists():
                    continue
                else:
                    for ts in TotalScore.objects.filter(tournament=t).order_by('score'):
                        if ts.score != 999 and ts.cut_count:
                            d.get(ts.user.username).update({'played': d.get(ts.user.username).get('played') + 1,
                                                'cuts': d.get(ts.user.username).get('cuts') + ts.cut_count,
                                })

            for user, data in d.items():
                if d.get(user).get('played') != 0 and d.get(user).get('cuts') !=0:
                    d.get(user).update({'average_cuts': round(d.get(user).get('cuts')/d.get(user).get('played'), 2)})

        except Exception as e:
            print ('Avg points API error: ', e)
            d['error'] = {'msg': str(e)}
        print (d)
        print ('avg points API time: ', datetime.datetime.now() - start)

        return JsonResponse(json.dumps(d), status=200, safe=False)


class MostPickedAPI(APIView):
    def get(self, request, season):
        
        start = datetime.datetime.now()
        d = {}
        try:
            if season == 'all':
                s = Season.objects.get(current=True)
            else:
                s = Season.objects.get(pk=season)
            for u in s.get_users('obj'):
                if season == 'all':
                    picks = Picks.objects.filter(user=u).order_by().values('playerName__golfer__golfer_name').annotate(c=Count('playerName__golfer__golfer_name'))
                    if picks:
                        most_picked = max(picks, key=lambda x:x['c'])
                    else:
                        most_picked = {'c': 'None'}
                else:
                    picks = Picks.objects.filter(user=u, playerName__tournament__season=s).order_by().values('playerName__golfer__golfer_name').annotate(c=Count('playerName__golfer__golfer_name'))
                    #print (picks)
                    if picks:
                        most_picked = max(picks, key=lambda x:x['c'])
                    else:
                        most_picked = {'c': 'None'}


                d[u.username] = {'most_picked_golfer': most_picked.get('playerName__golfer__golfer_name'),
                                'times_picked': most_picked.get('c'),

                                }

        except Exception as e:
            print ('Most Picked API error: ', e)
            d['error'] = {'msg': str(e)}
        print (d)
        print ('most picked API time: ', datetime.datetime.now() - start)

        return JsonResponse(json.dumps(d), status=200, safe=False)


class PGALeaderboard(APIView):
    def get(self, request, pk, refresh=None):
        
        start = datetime.datetime.now()
        d = {}
        try:
            t = Tournament.objects.get(pk=pk)
            if t.complete or not refresh:
                sd = ScoreDict.objects.get(tournament=t)
                data = sd.espn_api_data
                espn = espn = espn_api.ESPNData(t=t, data=data)
            else:
                espn = espn_api.ESPNData(force_refresh=True)
            
            d['leaderboard'] = espn.get_leaderboard()
            
        except Exception as e:
            print ('PGA Leaderboard API error: ', e)
            d['error'] = {'msg': str(e)}
        #print (d)
        print ('PGA leaderboard API time: ', datetime.datetime.now() - start)

        return JsonResponse(json.dumps(d), status=200, safe=False)


class SummaryStatsAPI(APIView):
    #def get(self, request, pk, refresh=None):
    def get(self, request, pk):
        
        start = datetime.datetime.now()
        d = {}
        try:
            t = Tournament.objects.get(pk=pk)
            sd = ScoreDict.objects.get(tournament=t)
            if t.good_api_data():
                if t.complete:
                    #sd = ScoreDict.objects.get(tournament=t)
                    data = sd.espn_api_data
                    espn = espn = espn_api.ESPNData(t=t, data=data)
                else:
                    espn = espn_api.ESPNData(force_refresh=True)

                cut_line = espn.cut_line()
                if cut_line.get('cut_score') == 0:
                    cut_line.update({'cut_score': 'E'})
                
                d['source'] = 'espn_api'
                d['cut_num'] = espn.cut_num()
                d['cut_info'] = cut_line
                d['leaders'] = espn.leaders()
                d['leader_score'] = espn.leader_score()
                d['curr_round'] = espn.get_round()
                d['round_status'] = espn.get_round_status()
            else:
                #this section doesn't work, need to adjust
                web_data = json.loads(sd.pick_data).get('display_data')
                d['source'] = 'espn_scrape'
                d['cut_num'] = ''
                d['cut_info'] = web_data.get('cut_line')
                d['leaders'] = web_data.get('leaders')
                d['leader_score'] = ''
                d['curr_round'] = ''
                d['round_status'] = web_data.get('round_status')


        except Exception as e:
            print ('Summart Stats API error: ', e)
            d['error'] = {'msg': str(e)}
        print ('summary stats dict: ', d)
        print ('Summary Stats API time: ', datetime.datetime.now() - start)

        return JsonResponse(json.dumps(d), status=200, safe=False)


class GetMsgsAPI(APIView):
    def get(self, request, pk):
        
        start = datetime.datetime.now()
        d = {}
        try:
            t = Tournament.objects.get(pk=pk)
            hc = {}
            for user in Picks.objects.values('user__username').distinct().order_by('user_id'):
                hc[user.get('user__username')] = {}
            handicaps = Picks.objects.filter(playerName__tournament=t).values('user__username').order_by('user__username').annotate(Sum('playerName__handi'))
            for h in handicaps:
                hc.get(h.get('user__username')).update({'total': h.get('playerName__handi__sum')})
            bd = golf_serializers.BonusDetailSerializer(BonusDetails.objects.filter(tournament=t).exclude(bonus_points=0), many=True).data
            pm = golf_serializers.PickMethodSerializer(PickMethod.objects.filter(tournament=t).exclude(method__in=[1,2]), many=True).data
            
            d['handicap'] = hc
            d['bonus_dtl'] = bd
            d['pick_method'] = pm

        except Exception as e:
            print ('Get Msgs API error: ', e)
            d['error'] = {'msg': str(e)}
        #print (d)
        print ('Messages API time: ', datetime.datetime.now() - start)

        return JsonResponse(json.dumps(d), status=200, safe=False)


class BuildFieldAPI(APIView):
    def post(self, request):
        start = datetime.datetime.now()
        d = {}

        try:
            print (request.data, type(request.data))
            
            pga_t_num = request.data.get('pga_t_num')
            espn_t_num = request.data.get('espn_t_num')
            if Tournament.objects.filter(season__current=True, pga_tournament_num=pga_t_num).exists():
                d['error'] = {'msg': 'Tournament for that pga t number and season already exists'}
            else:
                populateField.create_groups(pga_t_num, espn_t_num)
                d['status'] = {'msg': 'complete'}


        except Exception as e:
            print ('Build Field API error: ', e)
            d['error'] = {'msg': str(e)}
        #print (d)
        print ('Build Field API time: ', datetime.datetime.now() - start)

        return JsonResponse(json.dumps(d), status=200, safe=False)


class FieldUpdatesAPI(APIView):
    def get(self, request):
        print ('updateing field data')
        start = datetime.datetime.now()
        t = Tournament.objects.get(current=True)
        d = {}
        try:
            fed_ex = populateField.get_fedex_data(t)
            individual_stats = populateField.get_individual_stats()

            for f in Field.objects.filter(tournament=t):
                if t.pga_tournament_num not in ['470', '018']:
                    f.handi = f.handicap()
                else:
                    f.handi = 0

                f.prior_year = f.prior_year_finish()

                recent = OrderedDict(sorted(f.recent_results().items(), reverse=True))

                f.recent = recent
                f.season_stats = f.golfer.summary_stats(t.season) 

                if fed_ex.get(f.playerName):
                    f.season_stats.update({'fed_ex_points': fed_ex.get(f.playerName).get('points'),
                                           'fed_ex_rank': fed_ex.get(f.playerName).get('rank')})
                else:
                    f.season_stats.update({'fed_ex_points': 'n/a',
                                           'fed_ex_rank': 'n/a'})

                if individual_stats.get(f.playerName):
                    player_s = individual_stats.get(f.playerName)
                    for k, v in player_s.items():
                        if k != 'pga_num':
                            f.season_stats.update({k: v})

                f.save()

            d['status'] = {'msg': 'Updated Field Complete'}
        except Exception as e:
            print ('Update Field API error: ', e)
            d['error'] = {'msg': str(e)}
        
        print ('Update Field API time: ', datetime.datetime.now() - start)

        return JsonResponse(json.dumps(d), status=200, safe=False)


class UpdateGolferResultsAPI(APIView):
    def get(self, request, min_key, max_key):
        print ('starting golfer results update')
        start = datetime.datetime.now()
        d = {}
 
        newest_g = Golfer.objects.all().last()
        
        if newest_g.pk - max_key < 25: 
            print ('NEW golfers adding to max key', newest_g)
            max_key = newest_g.pk

        try:
            for g in Golfer.objects.filter(pk__gte=min_key, pk__lte=max_key):
                g.results = g.get_season_results()
                g.save()

            d['status'] = {'msg': 'Golfer Results Updates Complete range pks: ' + str(min_key) + ' - ' + str(max_key)}
        
        except Exception as e:
            print ('Update Golfer Results API error: ', e)
            d['error'] = {'msg': str(e)}
        
        print ('Update Golfer Results API time: ', datetime.datetime.now() - start, 'range: ', str(min_key), ' - ', str(max_key))

        return JsonResponse(json.dumps(d), status=200, safe=False)


class SetupStatsAPI(APIView):
    def get(self, request, pga_t_num, espn_t_num):
        
        start = datetime.datetime.now()
        d = {}
        t = Tournament.objects.get(current=True)
        if t.espn_t_num != espn_t_num or t.pga_tournament_num != pga_t_num:
            d['error'] = {'msg': 'Tnums not equal for current T'}
            return JsonResponse(json.dumps(d), status=200, safe=False)

        try:
            field_db_count = Field.objects.filter(tournament=t).count()
            espn_count = len(espn_api.ESPNData().field())

            #should centralize this code somewhere, duplicated wiht populateField.get_field()
            headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36'}
            json_url = 'https://statdata-api-prod.pgatour.com/api/clientfile/Field?T_CODE=r&T_NUM=' + str(t.pga_tournament_num) +  '&YEAR=' + str(t.season.season) + '&format=json'
            req = urllib.request.Request(json_url, headers=headers)
            data = json.loads(urllib.request.urlopen(req).read())

            pga_count = len([x for x in data["Tournament"]["Players"] if x.get('isAlternate') == "No"])

            d['status'] = {'espn_count': espn_count, 
                           'pga_count': pga_count, 
                            'field_db_count': field_db_count}
        except Exception as e:
            print ('Setup Summary Stats API error: ', e)
            d['error'] = {'msg': str(e)}
        
        print ('Setup Summary Status API time: ', datetime.datetime.now() - start)

        return JsonResponse(json.dumps(d), status=200, safe=False)


class SDStatusAPI(APIView):
    def get(self, request):
        
        start = datetime.datetime.now()
        d = {}
        try:
            for t in Tournament.objects.filter(season__current=True).exclude(current=True).order_by('-pk'):
                sd = ScoreDict.objects.get(tournament=t)
                d[t.name] = {'sd_valid': sd.data_valid()}

        except Exception as e:
            print ('SD Status API error: ', e)
            d['error'] = {'msg': str(e)}
        
        print ('SD Status API time: ', datetime.datetime.now() - start)

        return JsonResponse(json.dumps(d), status=200, safe=False)


class GetFieldAPI(APIView):
    def get(self, request, pk):
        
        start = datetime.datetime.now()
        d = {}
        try:
            t = Tournament.objects.get(pk=pk)
            f = Field.objects.filter(tournament=t)
            field = serializers.serialize('json', f)
            groups = serializers.serialize('json', Group.objects.filter(tournament=t))
                
            d['field'] = field
            d['groups'] =  groups

        except Exception as e:
            print ('GetFieldAPI error: ', e)
            d['error'] = {'msg': str(e)}
        
        print ('GetFieldAPI time: ', datetime.datetime.now() - start)

        return JsonResponse(json.dumps(d), status=200, safe=False)


class GetGolfersOBJAPI(APIView):
    def get(self, request, pk):
        
        start = datetime.datetime.now()
        d = {}
        try:
            t = Tournament.objects.get(pk=pk)
            g_keys = Field.objects.filter(tournament=t).values_list('golfer__pk', flat=True)
            #golfers = serializers.serialize('json', Golfer.objects.filter(pk__in=g_keys))
            golfers = golf_serializers.GolferSerializer(Golfer.objects.filter(pk__in=g_keys), many=True).data
            d['golfers'] =  golfers
            if t.pga_tournament_num == '018':  #Zurich 
                p_keys = Field.objects.filter(tournament=t).values_list('partner_golfer__pk', flat=True)
                partners = golf_serializers.GolferSerializer(Golfer.objects.filter(pk__in=p_keys), many=True).data
                d['partners'] = partners

        except Exception as e:
            print ('GetGolferOBJAPI error: ', e)
            d['error'] = {'msg': str(e)}
        
        print ('GetGolferOBJAPI time: ', datetime.datetime.now() - start)

        return JsonResponse(json.dumps(d), status=200, safe=False)


class StartedDataAPI(APIView):
    def get(self, request, pk):
        
        start = datetime.datetime.now()
        d = {}
        try:
            t = Tournament.objects.get(pk=pk)
            started_golfers = []
            lock_groups = []  
            espn = espn_api.ESPNData()
            after_espn_start = datetime.datetime.now()
            if t.special_field() and (t.started() and not t.late_picks):
                t_started = True
                started_golfers = list(Field.objects.filter(tournament=t).values_list('golfer__espn_number', flat=True))
            elif t.special_field() and (t.set_notstarted or t.late_picks):
                t_started = False
            elif t.set_started:
                t_started = True
            elif t.set_notstarted:
                t_started = False
            elif not espn.started() or t.late_picks:
                t_started = False
            else:
                t_started = espn.started()
                started_golfers = espn.started_golfers_list()
                for g in Group.objects.filter(tournament=t):
                      if g.lock_group(espn, self.request.user):
                         lock_groups.append(g.pk) 

            d['t_started'] =  t_started
            d['started_golfers'] = started_golfers
            d['lock_groups'] = lock_groups
            print ('GetStertedDataAPI after espn time: ', datetime.datetime.now() - after_espn_start)
            print (d)
        except Exception as e:
            d['t_started'] =  False
            d['started_golfers'] = []
            d['lock_groups'] = []

            print ('GetStartedDataAPI error: ', e)
            d['error'] = {'msg': str(e)}
        
        
        print ('GetStertedDataAPI time: ', datetime.datetime.now() - start)

        return JsonResponse(json.dumps(d), status=200, safe=False)


class FedExSummaryView(LoginRequiredMixin, TemplateView):
    login_url = 'login'
    template_name = 'golf_app/fedex_summary.html'

    def get_context_data(self, **kwargs):
        start = datetime.datetime.now()
        context = super(FedExSummaryView, self).get_context_data(**kwargs)
        context.update(fedEx_summary_context_data(self.request.user, kwargs.get('pk')))
        print ('fedex summary context duration', datetime.datetime.now() - start)
        for k, v in context.items():
            print (k,v)
            print ('-------------')

        return context


class FedExSummaryEmail(TemplateView):
    template_name = 'golf_app/fedex_summary_email.html'

    def get_context_data(self, **kwargs):
        start = datetime.datetime.now()
        context = super(FedExSummaryEmail, self).get_context_data(**kwargs)
        base_data = fedEx_summary_context_data()
        season = FedExSeason.objects.get(season__current=True)  # make a param?
        b_r = HttpRequest()
        b_api = FedExPicksByScore()
        by_score = dict(json.loads(b_api.get(b_r, season.pk).content))
        i_r = HttpRequest()
        
        display_dict = {}
        display_dict['user_data'] = json.loads(season.season.get_total_points())

        i_api = FedExInOutAPI()
        in_out = dict(json.loads(i_api.get(i_r, display_dict.get('user_data')).content))

        d_r = HttpRequest()
        d_api = FedExDetailAPI()
        detail = dict(json.loads(d_api.get(d_r, season.pk, 'email', display_dict.get('user_data')).content))

        fed_ex_totals = season.player_points()
        
        for k,v in base_data.get('stats').items():
            display_dict.get('user_data').get(k).update({'in_top30': v.get('in_top30'),
                                        'outside_top30': v.get('outside_top30'),
                                        'fed_ex_rank': fed_ex_totals.get(k).get('rank'),
                                        })

        for k,v in by_score.items():
            display_dict.get('user_data').get(k).update({'plus_20': v.get('plus_20'),
                                        'minus_80': v.get('minus_80'),
                                        'at_risk': v.get('at_risk'),
                                        'onthe_verge': v.get('onthe_verge') })

        for k,v in in_out.items():
            display_dict.update({k: v})

        display_dict.update({'details': {}})
        for k, v in detail.items():
            display_dict.get('details').update({k:v})

        prior_tournaments = Tournament.objects.filter(season__current=True).exclude(current=True).order_by('pk')
        last_t = prior_tournaments.last()
        t = Tournament.objects.get(current=True)

        t_3_ago = json.loads(prior_tournaments.reverse()[2].season.get_total_points(prior_tournaments.reverse()[2]))
        t_5_ago = json.loads(prior_tournaments.reverse()[4].season.get_total_points(prior_tournaments.reverse()[4]))

        #results = {}
        prior_5 = Tournament.objects.filter(season__current=True).order_by('-pk')[:6]  #using 6 to include 5 old and the current

        for u, data in t_5_ago.items():
            y = []
            for pt in [x for x in reversed(prior_5)]:
                d = [x.get('diff') for k, x in json.loads(pt.season.get_total_points(pt)).items() if k== u]
                y.append(d[0])
    
            coefficients, residuals, _, _, _ = np.polyfit(range(len(y)),y,1,full=True)
            mse = residuals[0]/(len(y))
            #print (max(y), min(y))
            nrmse = np.sqrt(mse)/(max(y) - min(y))    

            #print (coefficients, type(coefficients[0]))
            if coefficients[0] < 0:
                desc = 'Trending Down'
            else:
                desc = 'Trending Up'
            #results[u.username] = {'slope': str(coefficients[0]), 'nrmse': str(nrmse), 'desc': desc}
            #print('Slope ' + str(coefficients[0]))
            #print('NRMSE: ' + str(nrmse))

            c_total = [v.get('diff') for k, v in display_dict.get('user_data').items() if k == u][0]

            display_dict.get('user_data').get(u).update({'trend':{
                                                'current': c_total,
                                                'five': int(c_total) - int([v.get('diff') for k, v in t_5_ago.items() if k == u][0]),
                                                'three': int(c_total) - int([v.get('diff') for k, v in t_3_ago.items() if k == u][0]),
                                                'slope': str(coefficients[0]),
                                                'nrmse': str(nrmse),
                                                'desc': desc
                                                            }})
            #print ('ccccc : ', u, c_total, int([v.get('diff') for k, v in t_5_ago.items() if k == u][0]))

        d = json.loads(t.season.get_total_points())
        last_d = json.loads(last_t.season.get_total_points(last_t))

        current_wk_first = [k for k,v in d.items() if v.get('rank') == 1]
        last_wk_first =  [k for k,v in last_d.items() if v.get('rank') == 1]

        current_wk_second = [k for k,v in d.items() if v.get('rank') == 2]
        last_wk_second = [k for k,v in last_d.items() if v.get('rank') == 2]

        if len(current_wk_first) == 1 and len(last_wk_first) == 1:
            if current_wk_first[0] != last_wk_first[0]:
                msg1 = 'Congrats to ' + str(current_wk_first[0]) + 'for taking the overall lead. ' +   str(current_wk_second[0]) + ' leads the chasers, trailing by ' + \
                    str([v.get('total') for v in d.values() if v.get('rank') == 1][0] - [v.get('total') for v in d.values() if v.get('rank') == 2][0]) 
                    
            elif [v.get('total') for v in d.values() if v.get('rank') == 1][0] - [v.get('total') for v in last_d.values() if v.get('rank') == 2][0] < 100:
                msg1 = str(current_wk_first[0]) + ' remains in first, a tight race with ' + str(current_wk_second[0]) + ' only ' + \
                    str([v.get('total') for v in d.values() if v.get('rank') == 1][0] - [v.get('total') for v in d.values() if v.get('rank') == 2][0]) + \
                    ' points behind.'
            elif [v.get('total') for v in d.values() if v.get('rank') == 1][0] - [v.get('total') for v in last_d.values() if v.get('rank') == 2][0] < 100:
                msg1 = str(current_wk_first[0]) + 'remains in first with a solid lead of ' + str(current_wk_second[0]) + ' points over ' + \
                    str([v.get('total') for v in d.values() if v.get('rank') == 1][0] - [v.get('total') for v in d.values() if v.get('rank') == 2][0]) + \
                    '.'

        sched = espn_schedule.ESPNSchedule()

        context.update({'display_dict': display_dict, 
                        'last_t': last_t,
                        'msg1': msg1,
                        'complete': sched.complete_events(),
                        'remaining': sched.remaining_events()

        })
        
        print ('fedex summary context duration', datetime.datetime.now() - start)
        return context


def fedEx_summary_context_data(user=None, pk=None):
        if pk:
            f_season = FedExSeason.objects.get(pk=pk)
        else:
            f_season = FedExSeason.objects.get(season__current=True)

        order_list = []
        stats = {}
        d = {}
        if user:
            order_list.append(user.username)
        for u in f_season.season.get_users('obj') :
            if u != user:
                order_list.append(u.username)
            stats[u.username] = f_season.above_below_line(u)

        #print (order_list)
        d.update({
            'fedex_season': f_season,
            'users': f_season.season.get_users('obj'),
            'order': order_list,
            'stats': stats,
        })
        print ('fed ex summart func done')
        return d


class FedExPicksByScore(APIView):
    def get(self, request, pk):
        
        start = datetime.datetime.now()
        d = {}
        try:
            fedex_season = FedExSeason.objects.get(pk=pk)

            for u in fedex_season.season.get_users('obj'):
                d[u.username] = fedex_season.picks_by_score(u)
                d.get(u.username).update(fedex_season.picks_at_risk(u))
                
        except Exception as e:
            print ('FedExPicksByScore error: ', e)
            d['error'] = {'msg': str(e)}
        
        
        print ('FedExGetPicksByScore time: ', datetime.datetime.now() - start)

        #return JsonResponse(json.dumps(d), status=200, safe=False)
        return JsonResponse(d, status=200, safe=False)


class FedExInOutAPI(APIView):
    def get(self, request, user_order=None):
        
        start = datetime.datetime.now()
        t = Tournament.objects.get(current=True)
        d = {'into_top30': {},
             'out_top30': {}}
        try:
            # for pick in FedExPicks.objects.filter(pick__season__season__current=True).values('pick__golfer').distinct():
            #     #print (pick)
            #     p = FedExPicks.objects.filter(pick__season__season__current=True, pick__golfer=pick.get('pick__golfer')).first()
                
            #     rank_data = [v for k,v in t.fedex_data.items() if k == p.pick.golfer.golfer_name]
            #     if len(rank_data) == 1:
            #         data = rank_data[0]
            #         if data.get('rank') and int(data.get('rank')) < 31 and int(data.get('last_week_rank')) > 30:
            #             d.get('into_top30').update({p.pick.golfer.golfer_name: list(FedExPicks.objects.filter(pick__season__season__current=True, pick__golfer=p.pick.golfer).values_list('user__username', flat=True))})
            #         elif data.get('rank') and int(data.get('rank')) > 30 and int(data.get('last_week_rank')) < 31:
            #             d.get('out_top30').update({p.pick.golfer.golfer_name: list(FedExPicks.objects.filter(pick__season__season__current=True, pick__golfer=p.pick.golfer).values_list('user__username', flat=True))})
            d.get('into_top30').update({k:v for k,v in t.fedex_data.items() if k != 'player_points' and int(v.get('rank')) < 31 and (v.get('last_week_rank') != '' and int(v.get('last_week_rank')) >30)})
            d.get('out_top30').update({k:v for k,v in t.fedex_data.items() if k != 'player_points' and int(v.get('rank')) > 30 and (v.get('last_week_rank') != '' and int(v.get('last_week_rank')) < 31)})

            for k,v in d.get('into_top30').items():
                d.get('into_top30').get(k).update({'picks': {}})
                for u, data in user_order.items():
                    if FedExPicks.objects.filter(pick__golfer__golfer_name=k, user__username=u).exists():
                        d.get('into_top30').get(k).get('picks').update({u: True})
                    else:
                        d.get('into_top30').get(k).get('picks').update({u: False})

            for k,v in d.get('out_top30').items():
                d.get('out_top30').get(k).update({'picks': {}})
                for u, data in user_order.items():
                    if FedExPicks.objects.filter(pick__golfer__golfer_name=k, user__username=u).exists():
                        d.get('out_top30').get(k).get('picks').update({u: True})
                    else:
                        d.get('out_top30').get(k).get('picks').update({u: False})

        except Exception as e:
            print ('FedExInOutAPI error: ', e)
            d['error'] = {'msg': str(e)}
        
        print ('InOut d: ', d)
        print ('FedExinOutAPI time: ', datetime.datetime.now() - start)

        return JsonResponse(d, status=200, safe=False)


class FedExDetailAPI(APIView):
    def get(self, request, pk, mode=None, user_order=None):
        
        print ('user ORDER : ', user_order)
        start = datetime.datetime.now()
        d = {}
        sorted_d = {}
        try:
            fedex_season = FedExSeason.objects.get(pk=pk)
            t = Tournament.objects.get(current=True)
            for p in FedExPicks.objects.filter(pick__season=fedex_season).values('pick__golfer').distinct():
                pick = FedExPicks.objects.filter(pick__season=fedex_season, pick__golfer__pk=p.get('pick__golfer')).first()
                users = list(FedExPicks.objects.filter(pick__season=fedex_season, pick__golfer__pk=p.get('pick__golfer')).values_list('user__username', flat=True))
                r =  [v.get('rank') for k,v in t.fedex_data.items() if k == pick.pick.golfer.golfer_name]
                if len(r) != 1:
                    rank = 999
                else:
                    rank = r[0]
                d[pick.pick.golfer.golfer_name] = {'user_list': users,
                                                    'score': pick.score,
                                                    'soy_owgr': pick.pick.soy_owgr,
                                                    'rank': rank
                                                    }
                if mode=='email':
                    d.get(pick.pick.golfer.golfer_name).update({'user_dict': {}})
                    for u, data in user_order.items():
                        if u in users:
                            d.get(pick.pick.golfer.golfer_name).get('user_dict').update({u: pick.score})
                        else:
                            d.get(pick.pick.golfer.golfer_name).get('user_dict').update({u: ''})


            sorted_d = dict(sorted(d.items(), key=lambda x: int(x[1]['rank'])))
            #print (sorted_d, type(sorted_d))
        except Exception as e:
            print ('FedExPicksByScore error: ', e)
            sorted_d['error'] = {'msg': str(e)}
        
        
        print ('FedExDetailsAPI time: ', datetime.datetime.now() - start)

        return JsonResponse(sorted_d, status=200, safe=False)
