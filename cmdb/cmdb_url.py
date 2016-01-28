from django.conf.urls import include, url
import views
urlpatterns = [

    url(r'publish/$', views.publish_api_view,name='main_api'),
    url(r'server_list/$', views.publish_api_view,name='server_list_api'),
    url(r'backup_list/$', views.publish_api_view,name='backup_list_api'),
]
