from django.conf.urls import url
from django.urls import path, include
from golf_app import views
from rest_framework import routers

#Template tagging
app_name = 'golf_app'

urlpatterns= [
    url(r'^field/$',views.FieldListView.as_view(),name='field'),
    url(r'^picks_list/$',views.PicksListView.as_view(),name='picks_list'),
    url(r'^total_score/$',views.SeasonTotalView.as_view(),name='total_score'),
    url(r'^setup/$',views.setup,name='setup'),
    url(r'^about/$',views.AboutView.as_view(),name='about'),
    #url(r'^ajax/get_picks/$', views.GetPicks.as_view(), name='get_picks'),
    url(r'^all_time/$', views.AllTime.as_view(), name='all_time'),
    url(r'^get_scores/$', views.GetScores.as_view(), name='get_scores'),
    url(r'^get_db_scores/$', views.GetDBScores.as_view(), name='get_db_scores'),
    url(r'^new_scores/$', views.NewScoresView.as_view(), name='new_scores'),
    url(r'^new_scores/(?P<pk>\d+)/$',views.NewScoresView.as_view(),name='new_scores'),
    url(r'^started/$', views.CheckStarted.as_view(), name='started'),
    url(r'^optimal_picks/$',views.OptimalPicks.as_view(),name='optimal_picks'),
    #url(r'^get_info/$',views.GetInfo.as_view(),name='get_info'),
    path('get_info/<int:pk>/',views.GetInfo.as_view(),name='get_info'),
    url(r'^cbs_scores/$',views.CBSScores.as_view(),name='cbs_scores'),
    url(r'^get_field_csv/$',views.GetFieldCSV.as_view(),name='get_field_csv'),
    url(r'^get_group_num/$',views.GetGroupNum.as_view(),name='get_group_num'),
    path('golf_leaderboard/', views.GolfLeaderboard.as_view()),
    path('golf_withdraw/', views.Withdraw.as_view()),
    path('field_get_picks/', views.GetPicks.as_view(), name='field_get_picks'),
    path('get_picks/<int:pk>/<str:username>', views.ScoreGetPicks.as_view(),name='get_picks'),
    path('check_espn_nums/', views.ValidateESPN.as_view()),
    path('scores_by_player/', views.ScoresByPlayerView.as_view(), name='scores_by_player'),
    path('api_player_score/', views.ScoresByPlayerAPI.as_view(), name='api_player_score'),
    path('get_espn_score_dict/<int:pk>/', views.ESPNScoreDict.as_view(), name='get_espn_score_dict'),
    path('get_prior_result/', views.PriorResultAPI.as_view(), name='get_prior_result'),
    path('recent_form/<str:player_num>/', views.RecentFormAPI.as_view(), name='recent_form'),
    path('update_field/', views.UpdateFieldView.as_view(), name='update_field'),
    path('get_group/<int:pk>/', views.GetGroupAPI.as_view(), name='get_group'),
    path('mp_scores/', views.MPScoresAPI.as_view(), name='mp_scores'),
    path('get_mp_records/<int:pk>', views.MPRecordsAPI.as_view(), name='get_mp_record'),
    path('total_score_chart_api/<int:season_pk>/<str:num_of_t>/', views.TrendDataAPI.as_view(), name='total_score_chart_api'),
    path('season_stats/', views.SeasonStats.as_view(), name='season_stats'),
    path('new_field_list/', views.NewFieldListView.as_view(), name='new_field_list'),
    path('get_golfer_links/<int:pk>', views.GetGolferLinks.as_view(), name='get_golfer_links'),
    path('auction_picks/', views.AuctionPickCreateView.as_view(), name='auction_picks'),
    path('auction_scores/', views.AuctionScores.as_view(), name='auction_scores'),
    path('get_golfers/', views.GetGolfers.as_view(), name='get_golfers'),
    path('get_picks_summary/<int:pk>', views.PicksSummaryData.as_view(), name='get_picks_summary'),
    path('get_country_counts/', views.OlympicGolfersByCountry.as_view(), name='get_country_counts'),
    path('get_country_picks/<int:pga_t_num>/<str:user>', views.GetCountryPicks.as_view(), name='get_country_picks'),
    path('olympic_scores/', views.OlympicScoresView.as_view(), name='olympic_scores'),
    path('fedex_picks_view/', views.FedExPicksView.as_view(), name='fedex_picks_view'),


    

    

]
