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
from django.db.models import Sum, Count, Max
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.db.models.functions import ExtractWeek, ExtractYear
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.

class DashboardView(ListView):
    model = Run
    #select_related = ('shoes',)
    template_name = 'run_app/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        year_data = (Run.objects.filter(date__gt='2011-12-31').annotate(year=ExtractYear('date')).values('year')
        .annotate(dist=Sum('dist'), time=Sum('time'), cals=Sum('cals'), num=Count('date')))

        total_data = (Run.objects.aggregate(tot_dist=Sum('dist'), tot_time=Sum('time'), tot_cals=Sum('cals'), num=Count('date')))

        shoe_data = Run.objects.filter(shoes__active=True).values('shoes__name', 'shoes_id').annotate(dist=Sum('dist'), num=(Count('date'))).order_by('-dist')

        week_data = (Run.objects.filter(date__gte="2017-9-1").annotate(year=ExtractYear('date')).annotate(week=ExtractWeek('date')).values('year', 'week')
        .annotate(total_dist=Sum('dist'), time=Sum('time'), cals=Sum('cals'), num=Count('date'), max_dist=(Max('dist'))).order_by('-year', '-week'))

        for year in year_data:
            pace = datetime.timedelta(minutes=year.get('time').total_seconds() / year.get('dist'))
            year['pace']=str(pace)[:4]

        tot_pace = datetime.timedelta(minutes=total_data.get('tot_time').total_seconds() / total_data.get('tot_dist'))
        total_data['tot_pace'] = str(tot_pace)[:4]

        for week in week_data:
            pace = datetime.timedelta(minutes=week.get('time').total_seconds() / week.get('total_dist'))
            week['pace']=str(pace)[:4]

            # format date for display and add to dict for context
            d = str(week.get('year')) + str("-W") + str(week.get('week'))
            w = datetime.datetime.strptime(d + '-1', '%Y-W%W-%w')
            week['date']=w.strftime("%b %d, %Y")

            # % change calcs
            week_i = 1
            long_run = 0
            weekly_total = 0

            while week_i <= 2:
                start_week = w - timedelta(weeks=week_i)
                try:
                    compare_week = week_data.get(year=str(datetime.datetime.strftime(start_week, '%Y')), week=str(datetime.datetime.strftime(start_week, '%W')))
                    wk_total_dist = compare_week.get('total_dist')
                    wk_long_run = compare_week.get('max_dist')
                except ObjectDoesNotExist:
                    wk_total_dist = 0
                    wk_long_run = 0
                if wk_total_dist > weekly_total:
                    weekly_total = wk_total_dist
                if wk_long_run > long_run:
                    long_run = wk_long_run
                week_i += 1

            if weekly_total > 0:
                week['tot_change']= (((week.get('total_dist') - weekly_total)/weekly_total) *100)
            else:
                week['tot_change'] = 100
            if long_run > 0:
                week['long_change'] = (((week.get('max_dist') - long_run)/long_run) * 100)
            else:
                week['long_change'] = 100

        context.update({
        'years': year_data,
        'weeks': week_data,
        'shoes': shoe_data,
        'totals': total_data,
        })
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
