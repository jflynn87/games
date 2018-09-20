from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views.generic import (View,TemplateView,
                                ListView,DetailView,
                                CreateView,DeleteView,
                                UpdateView)
from braces.views import SelectRelatedMixin
from run_app.models import Shoes, Run
from run_app.forms import CreateRunForm
from django.db.models import Sum, Count
import datetime
from dateutil.relativedelta import relativedelta
from django.db.models.functions import ExtractWeek, ExtractYear

# Create your views here.

class DashboardView(ListView):
    model = Run
    #select_related = ('shoes',)
    template_name = 'run_app/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        year_data = (Run.objects.filter(date__gt='2011-12-31').annotate(year=ExtractYear('date')).values('year')
        .annotate(dist=Sum('dist')))
        week_data = (Run.objects.filter(date__gte="2017-12-31").annotate(week=ExtractWeek('date')).values('week')
        .annotate(dist=Sum('dist')))
        for year in year_data:
            print (year)
        year = "2018"
        for week in week_data:
            d = str(year) + str('-W') + str(week.get('week'))
            w = datetime.datetime.strptime(d + '-0', '%Y-W%W-%w')
            print (w, week.get('dist'))
        return context

class ShoeCreateView(CreateView):
    fields = ("name","active","main_shoe")
    model = Shoes
    success_url = reverse_lazy("run_app:shoe_list")

class ShoeListView(ListView):
    model = Shoes
    queryset = Shoes.objects.all().order_by('-id')

    def get_context_data(self, **kwargs):
        context = super(ShoeListView, self).get_context_data(**kwargs)
        dist = Run.objects.values('shoes').annotate(total_dist=Sum('dist')).order_by('-shoes__id')
        list = zip(self.object_list, dist)
        num_runs = Run.objects.all().count()
        total_dist = Run.objects.aggregate(Sum('dist'))
        runtime = Run.objects.aggregate(Sum('time'))
        total_time = runtime.get('time__sum')
        total_cals = Run.objects.aggregate(Sum('cals'))
        start_date = Run.objects.earliest('date')
        summary_list = [num_runs, total_dist, total_time, total_cals, start_date]

        context.update({
             'shoes_list': list,
             'total_dist': total_dist,
             'num_runs': num_runs,
             'total_time': total_time,
             'total_cals': total_cals,
             'start_date': start_date
         })

        return context


class ShoeUpdateView(UpdateView):
    fields = ('active', 'main_shoe')
    model = Shoes
    success_url = reverse_lazy("run_app:shoe_list")

class ShoeDeleteView(DeleteView):
    model= Shoes
    success_url = reverse_lazy("run_app:shoe_list")

class RunCreateView(CreateView):
    model = Run
    form_class = CreateRunForm
    success_url = reverse_lazy("run_app:run_list")

class RunListView(ListView):
    model = Run
    queryset = Run.objects.all().order_by('-date')
    paginate_by = 50

class RunDetailView(DetailView):
    pass

class RunUpdateView(UpdateView):
    fields = ('date','dist', 'cals', 'time', 'location', 'shoes')
    model = Run
    success_url = reverse_lazy("run_app:shoe_list")


class RunDeleteView(DeleteView):
    model= Run
    success_url = reverse_lazy("run_app:shoe_list")
