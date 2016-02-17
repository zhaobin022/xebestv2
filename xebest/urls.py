"""xebest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from cmdb import views
from cmdb import cmdb_url

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$',views.index ),
    url(r'^login/$',views.login ),
    url('^logout/$', views.logout),
    url(r'^server/list/', views.server_list),
    url(r'^backuplist/', views.backup_list),
    url(r'^loglist/', views.log_list),
    url(r'^delete_backup/', views.delete_backup),
    url(r'^display_dir_content/', views.display_dir_content),
    url(r'^display_log_detail/', views.display_log_detail),
    url(r'^api/',include(cmdb_url)),
    url(r'^cmdb_main/', views.cmdb_main),


]
