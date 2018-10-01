from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from run_app import views

app_name = 'run_app'

urlpatterns = [
    #url(r'^$',views.ShoeListView.as_view(),name='shoe_list'),
    url(r'^shoe_list/$',views.ShoeListView.as_view(),name='shoe_list'),
    url(r'^add_shoe/$',views.ShoeCreateView.as_view(),name='add_shoe'),
    url(r'^update_shoe/(?P<pk>\d+)/$',views.ShoeUpdateView.as_view(),name='update_shoe'),
    url(r'^delete_shoe/(?P<pk>\d+)/$',views.ShoeDeleteView.as_view(),name='delete_shoe'),
    url(r'^run_list/$',views.RunListView.as_view(),name='run_list'),
    url(r'^add_run/$',views.RunCreateView.as_view(),name='add_run'),
    url(r'^update_run/(?P<pk>\d+)/$',views.RunUpdateView.as_view(),name='update_run'),
    url(r'^delete_run/(?P<pk>\d+)/$',views.RunDeleteView.as_view(),name='delete_run'),
    url(r'^dashboard/$',views.DashboardView.as_view(),name='dashboard'),
    url(r'^plan/(?P<pk>\d+)/$',views.ScheduleView.as_view(),name='plan'),

    ]
