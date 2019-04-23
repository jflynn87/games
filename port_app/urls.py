from django.conf.urls import url
from django.urls import path
from port_app import views

#Template tagging
app_name = 'port_app'

urlpatterns= [
    url(r'^dashboard/$',views.DashboardView.as_view(),name='dashboard'),
    url(r'^add_position/$',views.CreatePositionView.as_view(),name='add_position'),
    url(r'^ajax/symbol_lookup/$',views.symbol_lookup,name='symbol_lookup'),


]
