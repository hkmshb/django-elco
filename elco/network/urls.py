from django.conf.urls import include, patterns, url
from . import views



station_urls = [
    url(r'^$', views.station_list, name='station-list'),
    url(r'^create$', views.station_manage, name='station-create'),
    url(r'^(?P<station_id>\d+)/$', views.station_display, name='station-display'),
]


urlpatterns = [
    url(r'^stations/(?P<type_name>(transmissions|injections|distributions))/', 
        include(station_urls)),
]
