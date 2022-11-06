#from django.contrib import admin
from django.urls import path
from wc_app import views
#from django.conf.urls import include


app_name = 'wc_app'

urlpatterns = [
    #url(r'^$',views.ShoeListView.as_view(),name='shoe_list'),
    path('wc_group_picks', views.GroupPicksView.as_view(), name='wc_group_picks'),

    ]
