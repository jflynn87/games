from django.conf.urls import url
from django.urls import path
from golf_app import views

#Template tagging
app_name = 'golf_app'

urlpatterns= [
    url(r'^field/$',views.FieldListView.as_view(),name='field'),
    url(r'^picks_list/$',views.PicksListView.as_view(),name='picks_list'),
    url(r'^total_score/$',views.SeasonTotalView.as_view(),name='total_score'),
    url(r'^setup/$',views.setup,name='setup'),
    url(r'^about/$',views.AboutView.as_view(),name='about'),
    url(r'^ajax/get_picks/$', views.GetPicks.as_view(), name='get_picks'),
    url(r'^all_time/$', views.AllTime.as_view(), name='all_time'),
    url(r'^get_scores/$', views.GetScores.as_view(), name='get_scores'),
    url(r'^get_db_scores/$', views.GetDBScores.as_view(), name='get_db_scores'),
    url(r'^new_scores/$', views.NewScoresView.as_view(), name='new_scores'),
    url(r'^new_scores/(?P<pk>\d+)/$',views.NewScoresView.as_view(),name='new_scores'),
    url(r'^started/$', views.CheckStarted.as_view(), name='started'),
    url(r'^optimal_picks/$',views.OptimalPicks.as_view(),name='optimal_picks'),
    url(r'^get_info/$',views.GetInfo.as_view(),name='get_info'),
    url(r'^cbs_scores/$',views.CBSScores.as_view(),name='cbs_scores'),
    url(r'^get_field_csv/$',views.GetFieldCSV.as_view(),name='get_field_csv'),
    url(r'^get_group_num/$',views.GetGroupNum.as_view(),name='get_group_num'),
    path('golf_leaderboard/', views.GolfLeaderboard.as_view()),
    path('golf_withdraw/', views.Withdraw.as_view()),
    path('get_picks/<int:pk>/<str:username>', views.ScoreGetPicks.as_view(),name='get_picks'),
    path('check_espn_nums/', views.ValidateESPN.as_view()),

    

]
