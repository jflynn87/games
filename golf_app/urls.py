#from django.conf.urls import re_path as url
from django.urls import path, include, re_path as url
from golf_app import views
from rest_framework import routers

#Template tagging
app_name = 'golf_app'

urlpatterns= [
    #url(r'^field/$',views.FieldListView.as_view(),name='field'),
    path('new_field_list_1', views.FieldListView1.as_view(), name='new_field_list_1'),
    url(r'^picks_list/$',views.PicksListView.as_view(),name='picks_list'),
    url(r'^total_score/$',views.SeasonTotalView.as_view(),name='total_score'),
    url(r'^setup/$',views.setup,name='setup'),
    url(r'^about/$',views.AboutView.as_view(),name='about'),
    #url(r'^ajax/get_picks/$', views.GetPicks.as_view(), name='get_picks'),
    url(r'^all_time/$', views.AllTimeView.as_view(), name='all_time'),
    #url(r'^get_scores/$', views.GetScores.as_view(), name='get_scores'),
    path('get_scores/<int:tournament>', views.GetScores.as_view(), name='get_scores'),
    url(r'^get_db_scores/$', views.GetDBScores.as_view(), name='get_db_scores'),
    #url(r'^new_scores/$', views.NewScoresView.as_view(), name='new_scores'),
    #url(r'^new_scores/(?P<pk>\d+)/$',views.NewScoresView.as_view(),name='new_scores'),
    path('new_scores/', views.ApiScoresView.as_view(), name='new_scores'),
    path('new_scores/<int:pk>', views.ApiScoresView.as_view(), name='new_scores'),
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
    path('mp_scores/<int:pk>/', views.MPScoresAPI.as_view(), name='mp_scores'),
    path('get_mp_records/<int:pk>', views.MPRecordsAPI.as_view(), name='get_mp_record'),
    path('get_mp_ranks/<int:pk>', views.MPRankInGroup.as_view(), name='get_mp_ranks'),
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
    path('fedex_field/<str:filter>', views.FedExFieldAPI.as_view(), name='fedex_field'),
    path('fedex_picks_list/', views.FedExPicksListView.as_view(), name='fedex_picks_list'),
    path('fedex_picks_api/<int:fedex_season>/<str:filter>', views.FedExPicksAPI.as_view(), name='fedex_picks_api'),
    path('season_points/<str:season>/<str:filter>', views.SeasonPointsAPI.as_view(), name='season_points'),
    path('ryder_cup_scores/', views.RyderCupScoresView.as_view(), name='ryder_cup_scores'),
    path('ryder_cup_score_api/', views.RyderCupScoresAPI.as_view(), name='ryder_cup_score_api'),
    path('get_api_scores/<int:pk>', views.EspnApiScores.as_view(), name='get_api_scores'),
    path('api_scores_view/', views.ApiScoresView.as_view(), name='api_scores_view'),
    path('api_scores_view/<int:pk>', views.ApiScoresView.as_view(), name='api_scores_view'),
    path('total_played_api/<str:season>', views.TotalPlayedAPI.as_view(), name='total_played_api'),
    path('t_wins_api/<str:season>', views.TWinsAPI.as_view(), name='t_wins_api'),
    path('picked_winner_count_api/<str:season>', views.PickedWinnerCountAPI.as_view(), name='picked_winner_count_api'),
    path('avg_points_api/<str:season>', views.AvgPointsAPI.as_view(), name='avg_points_api'),
    path('avg_cuts_api/<str:season>', views.AvgCutsAPI.as_view(), name='avg_cuts_api'),
    path('most_picked_api/<str:season>', views.MostPickedAPI.as_view(), name='most_pickd_api'),
    path('get_pga_leaderboard/<int:pk>', views.PGALeaderboard.as_view(), name='get_pga_leaderboard'),
    path('get_summary_stats/<int:pk>', views.SummaryStatsAPI.as_view(), name='get_summary_stats'),
    path('get_msgs/<int:pk>', views.GetMsgsAPI.as_view(), name='get_msgs'),
    path('build_field/', views.BuildFieldAPI.as_view(), name='build_field'),
    #path('field_updates/', views.FieldUpdatesAPI.as_view(), name='field_updates'),
    path('field_updates/<int:min_key>/<int:max_key>', views.FieldUpdatesAPI.as_view(), name='field_updates'),
    path('golfer_results_updates/<int:min_key>/<int:max_key>', views.UpdateGolferResultsAPI.as_view(), name='golfer_results_update'),
    path('setup_summary_stats/<str:pga_t_num>/<str:espn_t_num>', views.SetupStatsAPI.as_view(), name='setup_summary_stats'),
    path('sds_status/', views.SDStatusAPI.as_view(), name='sds_status'),
    path('get_field/<int:pk>', views.GetFieldAPI.as_view(), name='get_field'),
    path('get_golfers_obj/<int:pk>', views.GetGolfersOBJAPI.as_view(), name='get_golfers_obj'),
    path('get_started_data/<int:pk>', views.StartedDataAPI.as_view(), name='get_started_data'),
    path('fedex_summary/<int:pk>', views.FedExSummaryView.as_view(), name='fedex_summary'),
    #path('fedex_summary/', views.FedExSummaryView.as_view(), name='fedex_summary'),
    path('fedex_summary/', views.FedExSummaryEmail.as_view(), name='fedex_summary'),  #use to test email on line, return to line above for prod
    path('fedex_picks_by_score/<int:pk>', views.FedExPicksByScore.as_view(), name='fedex_picks_by_score'),
    path('fedex_in_out/', views.FedExInOutAPI.as_view(), name='fedex_in_out'),
    path('fedex_detail_api/<int:pk>', views.FedExDetailAPI.as_view(), name='fedex_detail_api'),
    path('fedex_send_summary_email_api/<str:option>', views.SendFedExEmail.as_view(), name='fedex_send_sumary_email_api'),
    path('trends_view/', views.TrendsView.as_view(), name='trends_view'),
    path('trends_api/<int:pk>/<int:group>', views.TrendsAPI.as_view(), name='trends_api'),

]
