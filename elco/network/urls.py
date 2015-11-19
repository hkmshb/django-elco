from django.conf.urls import include, patterns, url
from . import views



station_urls = [
    url(r'^$', views.station_list, name='station-list'),
]


urlpatterns = [
    url(r'^stations/(?P<type_name>(transmissions|injections|distributions))/', 
        include(station_urls)),
]
