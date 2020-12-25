from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from fb_app import views

app_name = 'fb_app'

urlpatterns = [
    url(r'^games_list/$',views.GameListView.as_view(),name='games_list'),
    url(r'^games_list/(?P<pk>\d+)/$',views.GameListView.as_view(),name='games_list'),
    url(r'^scores_list/$',views.NewScoresView.as_view(),name='scores_list'),
    url(r'^scores_list/(?P<pk>\d+)/$',views.NewScoresView.as_view(),name='scores_list'),
    url(r'^fools/$',views.NewScoresView.as_view(),name='fools', kwargs={'league':'ff'}),
    url(r'^picks_list/$',views.PicksListView.as_view(),name='picks_list'),
    url(r'^picks_list/(?P<pk>\d+)/$',views.PicksListView.as_view(),name='picks_list'),
    url(r'^season_total/$',views.SeasonTotals.as_view(),name='season_total'),
    url(r'^about/$', views.AboutView.as_view(),name='about'),
    url(r'^all_time/$', views.AllTime.as_view(),name='all_time'),
    url(r'^ajax_get_games/$', views.ajax_get_games,name='ajax_get_games'),
    path('update_scores/', views.UpdateScores.as_view()),
    path('update_proj/', views.UpdateProj.as_view()),
    path('get_picks/', views.GetPicks.as_view()),
    path('get_weeks/', views.GetWeeks.as_view()),
    path('fb_leaderboard/', views.FBLeaderboard.as_view()),
    #path('get_games/', views.GetGames.as_view()),
    #path('get_pick/', views.GetPick.as_view()),
    url(r'^get_pick/$',views.GetPick.as_view(),name='get_pick'),
    url(r'^spread_view/$',views.SpreadView.as_view(),name='spread_view'),
    url(r'^get_spreads/(?P<pk>\d+)/$',views.GetSpreads.as_view(),name='get_spreads'),
    url(r'^new_scores/$',views.NewScoresView.as_view(),name='new_scores'),

    ]
