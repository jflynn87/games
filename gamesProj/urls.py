"""gamesProj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from golf_app import views
from fb_app import views
from main import views as main_views
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$', main_views.index,name='index'),
    url(r'^register/$',main_views.register,name='register'),
    url(r'^login/$',main_views.user_login,name='login'),
    url(r'^logout/$',main_views.user_logout,name='logout'),
    url(r'^fb_app/', include('fb_app.urls',namespace='fb_app')),
    url(r'^golf_app/', include('golf_app.urls',namespace='golf_app')),
    url(r'^run_app/', include('run_app.urls',namespace='run_app')),

]
