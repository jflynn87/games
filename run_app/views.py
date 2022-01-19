from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.generic import (View,TemplateView,
                                ListView,DetailView,
                                CreateView,DeleteView,
                                UpdateView)

from run_app.models import Shoes, Run, Schedule, Plan
from run_app.forms import CreateRunForm
from django.db.models import Sum, Count, Max
import datetime
from datetime import timedelta

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
                print ('start week: ', start_week)
                try:
                    compare_week = week_data.get(year=str(datetime.datetime.strftime(start_week, '%Y')), week=str(datetime.datetime.strftime(start_week, '%W')))
                    wk_total_dist = compare_week.get('total_dist')
                    wk_long_run = compare_week.get('max_dist')
                except ObjectDoesNotExist:
                    wk_total_dist = 0
                    wk_long_run = 0
                #print ('data: ', start_week, compare_week, wk_total_dist, weekly_total)
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
        print (context)
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
    #fields = ('date','dist', 'cals', 'time', 'location', 'shoes')
    model = Run
    success_url = reverse_lazy("run_app:run_list")
    form_class=CreateRunForm


class RunDeleteView(DeleteView):
    model= Run
    success_url = reverse_lazy("run_app:run_list")

class ScheduleView(DetailView):
    model=Plan

    def get_context_data(self, **kwargs):
            today = datetime.datetime.now()
            try:
                plan = Plan.objects.get(pk=self.kwargs.get('pk'))
                for day in Schedule.objects.filter(plan=plan, run=None, date__lte=datetime.datetime.today()):
                    print ('updating plan', day)
                    if Run.objects.filter(date=day.date).exists():
                        print (day.date)
                        run = Run.objects.get(date=day.date)
                        day.run = run
                        day.save()
                        print ('updated schedule', day)
            except Exception as e:
                print ('no schedule update', e)
                


            context = super(ScheduleView, self).get_context_data(**kwargs)
            plan = Plan.objects.get(pk=self.kwargs.get('pk'))
            #today = datetime.datetime.now()
            if today <= datetime.datetime.combine(plan.end_date, datetime.datetime.min.time()):
                current_week = Schedule.objects.filter(date=today).values('week').first()
                last_week = Schedule.objects.filter(week=int(current_week.get('week'))-1).values('week').first()
                next_week = Schedule.objects.filter(week=int(current_week.get('week'))+1).values('week').first()
                print (last_week, current_week, next_week)

            expected = Schedule.objects.filter(Q(plan__id=plan.id) & Q(date__lte=today) & Q(dist__gt=0)).aggregate((Sum('dist')), (Count('date')))
            actual = Run.objects.filter(Q(date__lte=today) & Q(date__gte=plan.start_date)).aggregate(Sum('dist'), (Count('date')))
            #base_expected = Schedule.objects.filter(Q(plan__id=plan.id) & Q(date__lte=plan.start_date) & Q(dist__gt=0)).aggregate((Sum('dist')), (Count('date')))
            #base_actual = Run.objects.filter(Q(date__lte=plan.start_date) & Q(date__gte=plan.start_date)).aggregate(Sum('dist'), (Count('date')))
            
            race_expected = Schedule.objects.filter(Q(plan__id=plan.id) & Q(date__lte=today) & Q(date__gte=plan.start_date) & Q(dist__gt=0)).aggregate((Sum('dist')), (Count('date')))
            race_actual = Run.objects.filter(Q(date__lte=today) & Q(date__gte=plan.start_date)).aggregate(Sum('dist'), (Count('date')))
           

            #base_plan_km = base_expected.get('dist__sum')*1.6
            #base_expected['plan_km']=base_plan_km
            #base_actual['dist_percent']= (base_actual.get('dist__sum')/base_expected.get('plan_km')) * 100
            #base_actual['run_percent']= (base_actual.get('date__count')/base_expected.get('date__count')) * 100

            race_plan_km = race_expected.get('dist__sum')*1.6
            race_expected['plan_km']=race_plan_km
            race_actual['dist_percent']= (race_actual.get('dist__sum')/race_expected.get('plan_km')) * 100
            race_actual['run_percent']= (race_actual.get('date__count')/race_expected.get('date__count')) * 100

            #plan_km = expected.get('dist__sum')*1.6
            #expected['plan_km']=plan_km
            #actual['dist_percent']= (actual.get('dist__sum')/expected.get('plan_km')) * 100
            #actual['run_percent']= (actual.get('date__count')/expected.get('date__count')) * 100
            print (actual)



            if plan.end_date - datetime.datetime.now().date() > datetime.timedelta(days=7):
                context.update( {
                'plan': plan,
                'last_week': Schedule.objects.filter(plan__pk=self.kwargs.get('pk'), week__in=[last_week.get('week')]),
                'current_week': Schedule.objects.filter(plan__pk=self.kwargs.get('pk'), week__in=[current_week.get('week')]),
                'next_week': Schedule.objects.filter(plan__pk=self.kwargs.get('pk'), week__in=[next_week.get('week')]),
                'schedule': Schedule.objects.filter(plan__pk=self.kwargs.get('pk')).exclude(week__in=[last_week.get('week'), current_week.get('week'), next_week.get('week')]).order_by('date'),
                'expected': expected,
                'actual': actual,
                #'base_expected': base_expected,
                #'base_actual': base_actual,
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
                #'base_expected': base_expected,
                #'base_actual': base_actual,
                'race_expected': race_expected,
                'race_actual': race_actual,

                })

            #print (context)
            return context

class getRunKeeperData(APIView):

    #def __init__(self):
    #    print ('init')

    def get(self, num):
        
        try:
            print ('get')
            #try:
            run_data = strava.StravaData()
            run_dict = run_data.get_runs()

            print ('-----')
            print (run_dict, len(run_dict))
            #activities = run_dict['activities']
            for data in json.loads(run_dict):
                print ('starting 4 loop', data)
                if data['activity'] == "Run":
                    date = data['date'].split('T')[0]
                    dist = round(data['distance']/1000,2)
                    time = timedelta(seconds=data['time'])
                    cals = data['calories']
                    #shoe = Shoes.objects.get(main_shoe=True)
                    #location = 1

                    print ('shoes', type(Shoes.objects.get(main_shoe=True)))

                    if Run.objects.filter(date=datetime.datetime.strptime(date, '%Y-%m-%d'), dist = dist).exists():
                        pass
                    else:
                        run = Run()

                        run.date=datetime.datetime.strptime(date, '%Y-%m-%d')
                        run.dist = dist 
                        run.time = time
                        run.cals = cals
                        
                        run.shoes = Shoes.objects.get(main_shoe=True)
                        run.location = 1

                        run.save()
                     
                else:
                    print ('not a run: ', data)
            
            return Response(run_dict, 200)

                #return JsonResponse(json.dumps(run_dict), 200)
                #return JsonResponse(run_dict )
        except Exception as e:
            print ('api error', e)
            return Response(json.dumps({'error': str(e)}), 401)

