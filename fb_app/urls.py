from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from fb_app import views

app_name = 'fb_app'

urlpatterns = [
    #url(r'^make_picks/$',views.CreatePicksView.as_view(),name='make_picks'),
    url(r'^user_login/$',views.user_login,name="user_login"),
    url(r'^register/$',views.register,name='register'),
    #url(r'^setup_games/$',views.setup_games,name='setup_games'),
    url(r'^games_list/$',views.GameListView.as_view(),name='games_list'),
    url(r'^scores_list/$',views.ScoresView.as_view(),name='scores_list'),
    url(r'^picks_list/$',views.PicksListView.as_view(),name='picks_list'),
    

    ]
