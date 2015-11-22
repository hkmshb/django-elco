from django.conf.urls import include, patterns, url
from .views import stations as station_views, \
                   ratings as rating_views



rating_xfmr_urls = [
    url(r'^$', rating_views.transformer_list, name='rating-transformer-list'),
    url(r'^create$', rating_views.transformer_manage, 
        name='rating-transformer-create'),
    url(r'^(?P<record_id>\d+)/', include([
        url(r'^$', rating_views.transformer_display, name='rating-transformer-display'),
        url(r'^update$', rating_views.transformer_manage, name='rating-transformer-update'),
    ])),
]


station_urls = [
    url(r'^$', station_views.station_list, name='station-list'),
    url(r'^create$', station_views.station_manage, name='station-create'),
    url(r'^(?P<station_id>\d+)/$', station_views.station_display, 
        name='station-display'),
    url(r'^(?P<station_id>\d+)/(?P<asset_type_name>(transformers|feeders))/$',
        station_views.station_display, name='station-asset-list'),
]


urlpatterns = [
    url(r'^ratings/transformers/', include(rating_xfmr_urls)),
    url(r'^stations/(?P<type_name>(transmissions|injections|distributions))/', 
        include(station_urls)),
]

