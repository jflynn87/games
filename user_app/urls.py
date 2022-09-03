#from django.contrib import admin
from django.urls import path, re_path as url
#from django.conf.urls import include, url
#from django.conf import settings
from user_app import views
from django.contrib.auth import views as auth_views

app_name = 'user_app'

urlpatterns = [
    #path('admin/', admin.site.urls),
#    url(r'^$', main_views.index,name='index'),
    #url(r'^', include('django.contrib.auth.urls')),
    #url(r'^register/$',main_views.register,name='register'),
    url(r'^signup/$', views.SignUp.as_view(),name='signup'),
    url(r'^login/$', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    #url(r'^accounts/login/$', auth_views.LoginView.as_view(template_name='user_app/login.html'), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(),name='logout'),
#    url(r'^fb_app/', include('fb_app.urls',namespace='fb_app')),
#    url(r'^golf_app/', include('golf_app.urls',namespace='golf_app')),
#    url(r'^run_app/', include('run_app.urls',namespace='run_app')),
#    url(r'^port_app/', include('port_app.urls',namespace='port_app')),
#    url(r'^', include('django.contrib.auth.urls')),
    #url(r'^api-auth/', include('rest_framework.urls')),
    path('baseball_scores/', views.GetBaseballScore.as_view())


]
