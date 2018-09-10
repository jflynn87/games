from django.shortcuts import render
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.views.generic import (View,TemplateView,
                                ListView,DetailView,
                                CreateView,DeleteView,
                                UpdateView)
from run_app.models import Shoes, Run
from run_app.forms import CreateRunForm

# Create your views here.

class ShoeCreateView(CreateView):
    fields = ("name","active",)
    model = Shoes
    success_url = reverse_lazy("run_app:shoe_list")

class ShoeListView(ListView):
    model = Shoes
    queryset = Shoes.objects.all().order_by('-active')

class ShoeUpdateView(UpdateView):
    fields = ('active',)
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
