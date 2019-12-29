from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from fb_app import views

app_name = 'fb_app'

urlpatterns = [
    #url(r'^make_picks/$',views.CreatePicksView.as_view(),name='make_picks'),
    #url(r'^user_login/$',views.user_login,name="user_login"),
    #url(r'^register/$',views.register,name='register'),
    #url(r'^setup_games/$',views.setup_games,name='setup_games'),
    url(r'^games_list/$',views.GameListView.as_view(),name='games_list'),
    url(r'^scores_list/$',views.ScoresView.as_view(),name='scores_list'),
    url(r'^fools/$',views.ScoresView.as_view(),name='fools', kwargs={'league':'ff'}),
    url(r'^golfers/$',views.ScoresView.as_view(),name='golfers', kwargs={'league':'my'}),
    #url(r'^scores_list/(?P<league>[\w-]+)/$',views.ScoresView.as_view(),name='scores_list'),
    url(r'^scores_list/(?P<pk>\d+)/$',views.ScoresView.as_view(),name='scores_list'),
    url(r'^picks_list/$',views.PicksListView.as_view(),name='picks_list'),
    url(r'^season_total/$',views.SeasonTotals.as_view(),name='season_total'),
    url(r'^about/$', views.AboutView.as_view(),name='about'),
    url(r'^all_time/$', views.AllTime.as_view(),name='all_time'),
    url(r'^ajax_get_games/$', views.ajax_get_games,name='ajax_get_games'),
    url(r'^ajax_get_spreads/$', views.ajax_get_spreads,name='ajax_get_spreads'),
    url(r'^update_nfl_scores/$', views.UpdateNFLScores.as_view(),name='update_nfl_scores'),
    url(r'^update_scores/$', views.UpdateScores.as_view(),name='update_scores'),
    url(r'^update_proj/$', views.UpdateProj.as_view(),name='update_proj'),
    url(r'^update_rank/$', views.UpdateRank.as_view(),name='update_rank'),
    url(r'^update_proj_rank/$', views.UpdateProjRank.as_view(),name='update_proj_rank'),
    url(r'^update_season_total/$', views.UpdateSeasonTotal.as_view(),name='update_season_total'),
    url(r'^update_season_rank/$', views.UpdateSeasonRank.as_view(),name='update_season_rank'),



    ]
