from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views.generic import (View,TemplateView,
                                ListView,DetailView,
                                CreateView,DeleteView,
                                UpdateView)
from run_app.models import Shoes, Run
from run_app.forms import CreateRunForm
from django.db.models import Sum
import datetime

# Create your views here.

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
        total_time = str(datetime.timedelta(seconds=runtime))
        total_cals = Run.objects.aggregate(Sum('time'))
        start_date = Run.objects.earliest('date')
        summary_list = [num_runs, total_dist, total_time, total_cals, start_date]
        print (num_runs, total_dist,  total_time, start_date.date)
        context.update({
             'shoes_list': list,
             'summary_list': summary_list
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

class RunListView(ListView):
    model = Shoes
    queryset = Run.objects.all().order_by('-date')
    paginate_by = 50

class RunDetailView(DetailView):
    pass

class RunUpdateView(UpdateView):
    fields = ('active',)
    model = Shoes
    success_url = reverse_lazy("run_app:shoe_list")


class RunDeleteView(DeleteView):
    model= Shoes
    success_url = reverse_lazy("run_app:shoe_list")
