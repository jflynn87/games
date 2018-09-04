from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View, TemplateView, ListView, DetailView, CreateView, UpdateView, FormView
from golf_app.models import Field, Tournament, Picks, Group, TotalScore, ScoreDetails
from golf_app.forms import  UserForm, CreatePicksForm
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


# Create your views here.

class CreatePicksView(LoginRequiredMixin,CreateView):
    login_url = '/golf_app/user_login/'
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
    login_url = '/golf_app/user_login/'
    template_name = 'golf_app/field_list.html'
    model = Field
    redirect_field_name = 'golf_app/picks_list.html'

    def get_context_data(self,**kwargs):
        context = super(FieldListView, self).get_context_data(**kwargs)
        context.update({
        'field_list': Field.objects.all(),
        'tournament': Tournament.objects.all(),
        })
        return context


    def post(self, request):
        group = Group.objects.all()
        form = request.POST
        user = User()

        tournament = Tournament.objects.all()

        for t in tournament:
            if datetime.date.today() >= t.start_date:
                print (t.start_date)
                print (timezone.now())
                return HttpResponse ("Sorry it is too late to submit picks.")


        if len(Picks.objects.filter(user=form['userid'])) > 0:
            return render (request, 'golf_app/field_list.html',
                 {'field_list': Field.objects.all(),
                  'picks_list': Picks.objects.all(),
                  'error_message':  "You have already made picks, please select view picks above",
                        })

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
                {'field_list': Field.objects.all(),
                 'picks_list': Picks.objects.all(),
                 'form':form,
                 'error_message':  "Missing Picks, try again",
                     })

        return redirect('golf_app:picks_list')


class PicksListView(LoginRequiredMixin,ListView):
    login_url = '/golf_app/user_login/'
    redirect_field_name = 'golf_app/pick_list.html'
    model = Picks

    def get_queryset(self):
        print (self.request.user)
        return Picks.objects.filter(user=self.request.user)

    def get_context_data(self,**kwargs):
        context = super(PicksListView, self).get_context_data(**kwargs)
        context.update({
        'field_list': Field.group,
        'tournament_list': Tournament.objects.all(),
        'picks_list': self.get_queryset(),
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




def index(request):
    return render(request, 'index.html', {
    'tournament': Tournament.objects.all(),
    })


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('golf_app:field'))

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


    return render(request,'golf_app/registration.html',
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
                if Picks.objects.filter(user=user):
                    return HttpResponseRedirect(reverse('golf_app:picks_list'))
                else:
                    return HttpResponseRedirect(reverse('golf_app:field'))
            else:
                return HttpResponse("Your account is not active")
        else:
            print ("someone tried to log in and failed")
            print ("Username: {} and password {}".format(username,password))
            return HttpResponse("invalid login details supplied")
    else:
        return render(request, 'golf_app/login.html', {})


class ScoreListView(ListView):
    template_name = 'golf_app/scores.html'
    model=TotalScore

    def get(self, request):

        tournament = Tournament.objects.all()

        for t in tournament:
            if datetime.date.today() >= t.start_date:
                return calc_score.calc_score(request)
            else:
                return HttpResponse("Come back on the tournament start day!")


def setup(request):

    if request.method == "GET":
        if request.user.is_superuser:
           return render(request, 'golf_app/setup.html')
        else:
           return HttpResponse('Not Authorized')
    if request.method == "POST":
        url_number = request.POST.get('tournament_number')
        populateField.create_groups(url_number)
        return HttpResponseRedirect(reverse('golf_app:field'))
