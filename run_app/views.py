from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import (View,TemplateView,
                                ListView,DetailView,
                                CreateView,DeleteView,
                                UpdateView)
from braces.views import SelectRelatedMixin
from run_app.models import Shoes, Run, Schedule, Plan
from run_app.forms import CreateRunForm
from django.db.models import Sum, Count, Max
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.db.models.functions import ExtractWeek, ExtractYear
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from run_app import scrape_runs, strava 
from rest_framework.views import APIView
from rest_framework.response import Response
import json




# Create your views here.

class DashboardView(ListView):
    model = Plan
    #model = Run
    #select_related = ('shoes',)
    template_name = 'run_app/dashboard.html'



    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        week_start = datetime.datetime.today() - timedelta(days=180)

        year_data = (Run.objects.filter(date__gt='2011-12-31').annotate(year=ExtractYear('date')).values('year')
        .annotate(dist=Sum('dist'), time=Sum('time'), cals=Sum('cals'), num=Count('date')))

        total_data = (Run.objects.aggregate(tot_dist=Sum('dist'), tot_time=Sum('time'), tot_cals=Sum('cals'), num=Count('date')))

        shoe_data = Run.objects.filter(shoes__active=True).values('shoes__name', 'shoes_id').annotate(dist=Sum('dist'), num=(Count('date'))).order_by('-dist')

        week_data = (Run.objects.filter(date__gte=week_start).annotate(year=ExtractYear('date')).annotate(week=ExtractWeek('date')).values('year', 'week')
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
            w = datetime.datetime.strptime(d + '-1', '%G-W%V-%u')
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
        #'schedules': Plan.objects.filter(end_date__gt=datetime.datetime.now())
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

    def form_valid(self, form):
        cd = form.cleaned_data
        self.object = form.save()
        date = form.cleaned_data.get('date')
        Schedule.objects.filter(date=date).update(run=Run.objects.get(date=date))
        return HttpResponseRedirect(self.get_success_url())

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
    success_url = reverse_lazy("run_app:dashboard")

class ScheduleView(DetailView):
    model=Plan

    def get_context_data(self, **kwargs):
            context = super(ScheduleView, self).get_context_data(**kwargs)
            plan = Plan.objects.get(pk=self.kwargs.get('pk'))
            today = datetime.datetime.now()
            if today <= datetime.datetime.combine(plan.end_date, datetime.datetime.min.time()):
                current_week = Schedule.objects.filter(date=today).values('week').first()
                last_week = Schedule.objects.filter(week=int(current_week.get('week'))-1).values('week').first()
                next_week = Schedule.objects.filter(week=int(current_week.get('week'))+1).values('week').first()
                print (last_week, current_week, next_week)

            expected = Schedule.objects.filter(Q(plan__id=plan.id) & Q(date__lte=today) & Q(dist__gt=0)).aggregate((Sum('dist')), (Count('date')))
            actual = Run.objects.filter(Q(date__lte=today) & Q(date__gte=plan.start_date)).aggregate(Sum('dist'), (Count('date')))
            base_expected = Schedule.objects.filter(Q(plan__id=plan.id) & Q(date__lte='2018-12-16') & Q(dist__gt=0)).aggregate((Sum('dist')), (Count('date')))
            base_actual = Run.objects.filter(Q(date__lte='2018-12-16') & Q(date__gte=plan.start_date)).aggregate(Sum('dist'), (Count('date')))
            race_expected = Schedule.objects.filter(Q(plan__id=plan.id) & Q(date__lte=today) & Q(date__gte='2018-12-17') & Q(dist__gt=0)).aggregate((Sum('dist')), (Count('date')))
            race_actual = Run.objects.filter(Q(date__lte=today) & Q(date__gte='2018-12-17')).aggregate(Sum('dist'), (Count('date')))

            base_plan_km = base_expected.get('dist__sum')*1.6
            base_expected['plan_km']=base_plan_km
            base_actual['dist_percent']= (base_actual.get('dist__sum')/base_expected.get('plan_km')) * 100
            base_actual['run_percent']= (base_actual.get('date__count')/base_expected.get('date__count')) * 100

            race_plan_km = race_expected.get('dist__sum')*1.6
            race_expected['plan_km']=race_plan_km
            race_actual['dist_percent']= (race_actual.get('dist__sum')/race_expected.get('plan_km')) * 100
            race_actual['run_percent']= (race_actual.get('date__count')/race_expected.get('date__count')) * 100

            plan_km = expected.get('dist__sum')*1.6
            expected['plan_km']=plan_km
            actual['dist_percent']= (actual.get('dist__sum')/expected.get('plan_km')) * 100
            actual['run_percent']= (actual.get('date__count')/expected.get('date__count')) * 100
            print (actual)



            if plan.end_date - datetime.datetime.now().date() > datetime.timedelta(days=7):
                context.update( {
                'plan': plan,
                'last_week': Schedule.objects.filter(plan__pk=self.kwargs.get('pk'), week__in=[last_week.get('week')]),
                'current_week': Schedule.objects.filter(plan__pk=self.kwargs.get('pk'), week__in=[current_week.get('week')]),
                'next_week': Schedule.objects.filter(plan__pk=self.kwargs.get('pk'), week__in=[next_week.get('week')]),
                'schedule': Schedule.objects.filter(plan__pk=self.kwargs.get('pk')).exclude(week__in=[last_week.get('week'), current_week.get('week'), next_week.get('week')]),
                'expected': expected,
                'actual': actual,
                'base_expected': base_expected,
                'base_actual': base_actual,
                'race_expected': race_expected,
                'race_actual': race_actual,

                })
            else:
                context.update( {
                'plan': plan,
                'last_week': None,
                'current_week': None,
                'next_week': None,
                'schedule': Schedule.objects.filter(plan__pk=self.kwargs.get('pk')).order_by('-date'),
                'expected': expected,
                'actual': actual,
                'base_expected': base_expected,
                'base_actual': base_actual,
                'race_expected': race_expected,
                'race_actual': race_actual,

                })

            #print (context)
            return context

class getRunKeeperData(APIView):

    def get(self, num):
        
        run_data = strava.StravaData()
        run_dict = run_data.get_runs()

        print (run_dict)

        for day, data in run_dict.items():
            #print ('starting 4 loop', date, data)
            if data[0] == "Run":
                date = day.split('T')[0]
                dist = round(data[1]/1000,2)
                time = timedelta(seconds=data[2])
                cals = data[3]
                shoes = Shoes.objects.get(main_shoe=True)
                location = 1
                print (date)


                Run.objects.get_or_create(date=datetime.datetime.strptime(date, '%Y-%m-%d'), 
                dist = dist, 
                time = time,
                cals = cals,
                shoes = Shoes.objects.get(main_shoe=True),
                location = 1
                )
            else:
                print ('not a run: ', data[0])
        
        return Response(json.dumps({'runs': run_dict,
                          
         }), 200)

