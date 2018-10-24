from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, TemplateView, ListView, DetailView, CreateView, UpdateView, FormView
from golf_app.models import Field, Tournament, Picks, Group, TotalScore, ScoreDetails
from golf_app.forms import  CreatePicksForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateResponseMixin
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
import datetime
from golf_app import populateField, calc_score
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Min, Q


# Create your views here.

class CreatePicksView(LoginRequiredMixin,CreateView):
    login_url = 'login'
    template_name = 'golf_app/make_picks.html'
    model = Picks
    #redirect_field_name = 'golf_app/picks_list.html'
    fields = ('playerName',)

    def post(self, request):
        if request.method == "POST":
            form = CreatePicksForm(request.POST)

        if form.is_valid():
            print (form)
        else:
            print ("bad form")

    def get_context_data(self,**kwargs):
        context = super(CreatePicksView, self).get_context_data(**kwargs)
        context.update({
        'field_list': Field.objects.all(),
        'picks': Picks.objects.all(),
        })
        return context


####  below here works in v1
class FieldListView(LoginRequiredMixin,ListView):
    login_url = 'login'
    template_name = 'golf_app/field_list.html'
    model = Field
    redirect_field_name = 'golf_app/picks_list.html'

    def get_context_data(self,**kwargs):
        context = super(FieldListView, self).get_context_data(**kwargs)
        context.update({
        'field_list': Field.objects.filter(tournament=Tournament.objects.get(current=True)),
        'tournament': Tournament.objects.get(current=True),
        })
        return context


    def post(self, request):
        tournament = Tournament.objects.get(current=True)
        group = Group.objects.filter(tournament=tournament)
        form = request.POST
        user = User()

        if datetime.date.today() >= tournament.start_date:
            print (tournament.start_date)
            print (timezone.now())
            return HttpResponse ("Sorry it is too late to submit picks.")


        if len(Picks.objects.filter(playerName__tournament=tournament, user=form['userid'])) > 0:
            return render (request, 'golf_app/field_list.html',
                 {'field_list': Field.objects.filter(tournament=tournament),
                  'picks_list': Picks.objects.filter(tournament=tournament, user=form['userid']),
                  'error_message':  "You have already made picks, please select view picks above",
                        })

        print (len(form), len(group))
        if (len(form)-2) == len(group):
            for k, v in form.items():
               if k != 'csrfmiddlewaretoken' and k!= 'userid':
                   picks = Picks()
                   picks.user = User.objects.get(pk=form['userid'])
                   picks.playerName = Field.objects.get(pk=v)
                   picks.save()
        else:
            #return reverse ('FieldListView')
            return render (request, 'golf_app/field_list.html',
                {'field_list': Field.objects.filter(tournament=tournament),
                 'picks_list': Picks.objects.filter(playerName__tournament__current=True, user=form['userid']),
                 'form':form,
                 'error_message':  "Missing Picks, try again",
                     })

        return redirect('golf_app:picks_list')


class PicksListView(LoginRequiredMixin,ListView):
    login_url = 'login'
    redirect_field_name = 'golf_app/pick_list.html'
    model = Picks

    #def get_queryset(self):
    #    print (self.request.user)
    #    return Picks.objects.filter(playerName__tournament__current=True,user=self.request.user)

    def get_context_data(self,**kwargs):
        context = super(PicksListView, self).get_context_data(**kwargs)
        context.update({
        #'field_list': Field.group,
        'tournament': Tournament.objects.get(current=True),
        'picks_list': Picks.objects.filter(playerName__tournament__current=True,user=self.request.user),
        })
        return context

    def post(self,request):
        form = request.POST
        user = User()

        tournament = Tournament.objects.all()

        for t in tournament:
            if datetime.date.today() >= t.start_date:
                return HttpResponse ("Sorry it is too late to change picks.")

        for pick in self.get_queryset():
            pick.delete()

        return render (request, 'golf_app/field_list.html',
            {'field_list': Field.objects.all(),
             'picks_list': Picks.objects.all(),
             'error_message':  "Picks Deleted.  Please enter new picks.",
                 })


class ScoreListView(DetailView):
    template_name = 'golf_app/scores.html'
    model=TotalScore

    def dispatch(self, request, *args, **kwargs):
        if kwargs.get('pk') == None:
            tournament = Tournament.objects.get(current=True)
            self.kwargs['pk'] = str(tournament.pk)
        #if self.request.POST:
        #    kwargs.pop('pk',None)
        print ('dispatch', self.kwargs)
        return super(ScoreListView, self).dispatch(request, *args, **kwargs)

    def get(self, request, **kwargs):

        print (self.kwargs)
        print (request)
        tournament = Tournament.objects.get(pk=self.kwargs.get('pk'))

        if datetime.date.today() >= tournament.start_date:
            scores = calc_score.calc_score(self.kwargs, request)
            return render(request, 'golf_app/scores.html', {'scores':scores[0],
                                                        'detail_list':scores[1],
                                                        'leader_list':scores[2],
                                                        'cut_data':scores[3],
                                                        'lookup_errors': scores[4],
                                                        })
        else:
           return HttpResponse("Come back on the tournament start day!")


class SeasonTotalView(ListView):
    template_name="golf_app/season_total.html"
    model=Tournament

    def get_context_data(self, **kwargs):
        display_dict = {}
        user_list = []
        winner_dict = {}

        for user in TotalScore.objects.values('user_id').distinct().order_by('user_id'):
            user_list.append(User.objects.get(pk=user.get('user_id')))
            print (user_list)


        for tournament in Tournament.objects.filter(season__current=True):
            score_list = []
            for score in TotalScore.objects.filter(tournament=tournament).order_by('user_id'):
                score_list.append(score)
            if tournament.complete:
                winner_list = []
                winner = TotalScore.objects.filter(tournament=tournament).order_by('score')
                winning_score = winner.annotate(Min('score'))
                num_of_winners = winner.filter(score=score.score, tournament=tournament).count()
                if num_of_winners == 1:
                    score_list.append(User.objects.get(pk=score.user.pk))
                    winner_data = (tournament, [User.objects.get(pk=score.user.pk)], num_of_winners)
                    winner_list.append(winner_data)
                elif num_of_winners > 1:
                    users = TotalScore.objects.filter(tournament=tournament, score=score.score)
                    win_user_list = []
                    for user in users:
                        score_list.append(User.objects.get(pk=user.user.pk))
                        win_user_list.append(User.objects.get(pk=user.user.pk))
                    winner_data = (tournament, win_user_list, num_of_winners)
                    winner_list.append(winner_data)
                else:
                     print ('something wrong with winner lookup', 'num of winners: ', len(winner))
            display_dict[tournament] = score_list
            # print ('winner list', winner_list[0][1])
            # print (len(winner_list))
            # for winner in winner_list[0]:
            #     winner_dict[winner.user]: tournament
            # print (winner_dict)



        context = super(SeasonTotalView, self).get_context_data(**kwargs)
        context.update({
        'display_dict':  display_dict,
        'user_list': user_list,
        })
        print (context)
        return context


def setup(request):

    if request.method == "GET":
        if request.user.is_superuser:
           return render(request, 'golf_app/setup.html')
        else:
           return HttpResponse('Not Authorized')
    if request.method == "POST":
        url_number = request.POST.get('tournament_number')
        print (url_number, type(url_number))
        try:
            if Tournament.objects.get(pga_tournament_num=str(url_number), season__current=True).exists():
                error_msg = ("tournament already exists" + str(url_number))
                return render(request, 'golf_app/setup.html', {'error_msg': error_msg})
        except ObjectDoesNotExist:
            populateField.create_groups(url_number)
            return HttpResponseRedirect(reverse('golf_app:field'))
