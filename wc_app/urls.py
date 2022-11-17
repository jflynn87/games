#from django.contrib import admin
from django.urls import path
from wc_app import views
#from django.conf.urls import include


app_name = 'wc_app'

urlpatterns = [
    #url(r'^$',views.ShoeListView.as_view(),name='shoe_list'),
    path('wc_group_picks', views.GroupPicksView.as_view(), name='wc_group_picks'),
    path('wc_group_picks_summary', views.GroupPicksSummaryView.as_view(), name='wc_group_picks_summary'),
    path('wc_scores', views.ScoresView.as_view(), name='wc_scores'),
    path('wc_about', views.AboutView.as_view(), name='wc_about'),
    path('wc_scores_api', views.ScoresAPI.as_view()),
    path('wc_group_bonus_api/<int:team_pk>', views.GroupBonusAPI.as_view()),
    path('wc_group_stage_teams_api', views.GroupStageTeamsAPI.as_view()),
    path('wc_group_stage_picks_api', views.GroupStagePicksAPI.as_view()),
    
    #path('wc_group_bonus_api', views.GroupBonusAPI.as_view()),
    

    ]
