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
    #path('get_picks/', views.GetPicks.as_view()),
    path('get_weeks/', views.GetWeeks.as_view()),
    path('fb_leaderboard/', views.FBLeaderboard.as_view()),
    #path('get_games/', views.GetGames.as_view()),
    #path('get_pick/', views.GetPick.as_view()),
    url(r'^get_pick/$',views.GetPick.as_view(),name='get_pick'),
    url(r'^spread_view/$',views.SpreadView.as_view(),name='spread_view'),
    url(r'^get_spreads/(?P<pk>\d+)/$',views.GetSpreads.as_view(),name='get_spreads'),
    url(r'^new_scores/$',views.NewScoresView.as_view(),name='new_scores'),
    path('analytics/',views.Analytics.as_view(), name='analytics'),
    #path('result_by_team/<str:nfl_abbr>', views.GetTeamResults.as_view()),
    path('all_team_results/<int:player_key>', views.AllTeamResults.as_view()),
    path('detailed_results/<int:player_key>/<str:nfl_abbr>', views.TeamResults.as_view()),
    path('playoff_entry/',views.CreatePlayoffs.as_view(),name='playoff_entry'),
    path('playoff_entry/<int:pk>',views.UpdatePlayoffs.as_view(),name='playoff_entry'),
    path('playoff_score/',views.PlayoffScores.as_view(),name='playoff_score'),
    path('update_playoff_scores/',views.UpdatePlayoffScores.as_view(),name='update_playoff_scores'),
    path('playoff_check_started/', views.PlayoffGameStarted.as_view()),
    path('playoff_about/',views.PlayoffLogic.as_view(),name='playoff_about'),

    ]
