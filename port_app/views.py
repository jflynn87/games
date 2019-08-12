from django.shortcuts import render
from django.views.generic import View, TemplateView, ListView, DetailView, CreateView, UpdateView, FormView
from port_app.models import MarketData, Portfolio, Position
from port_app.forms import CreatePositionForm
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpRequest

import urllib.request
import json

# Create your views here.


class DashboardView(TemplateView):
    template_name='port_app/dashboard.html'

    def get_context_data(self, **kwargs):

        json_url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=MSFT&apikey=demo'

        with urllib.request.urlopen(json_url) as mktData_json_url:
            data = json.loads(mktData_json_url.read().decode())

        print (data)

        context = super(DashboardView, self).get_context_data(**kwargs)
        context.update({
                        'mkt_data': data
        })

        return context


class CreatePositionView(CreateView):
    #fields = "__all__"
    model = Position
    form_class = CreatePositionForm
    success_url = 'port_app/dashboard'

    def post(self, *args, **kwargs):
        print (self.request.POST)


def symbol_lookup(request):
    print ('symbol lookup')
    if request.is_ajax():
        symbol = request.GET.get('symbol')

        #json_url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=' + symbol + '&apikey=LMFMS9U0HUA4DV7O'
        json_url = 'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords=' + symbol + '&apikey=LMFMS9U0HUA4DV7O'
        with urllib.request.urlopen(json_url) as mktData_json_url:
            data = json.loads(mktData_json_url.read().decode())

        print (data)

        return HttpResponse(json.dumps(data), content_type="application/json")
    else:
        print ('ajax_symbol_lookup issue')
        raise Http404
