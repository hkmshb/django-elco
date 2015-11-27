from django.conf.urls import include, patterns, url
from .views import stations as station_views, \
                   ratings as rating_views




rating_transformer_urls = [
    url(r'^$', rating_views.transformer_list, name='rating-transformer-list'),
    url(r'^create$', rating_views.transformer_manage, name='rating-transformer-create'),
    url(r'^delete$', rating_views.transformer_delete, name='rating-transformer-delete'),
    url(r'^(?P<record_id>\d+)/', 
        include([
            url(r'^$', rating_views.transformer_display, name='rating-transformer-detail'),
            url(r'^update$', rating_views.transformer_manage, name='rating-transformer-update'),
        ]
    )),
]

station_urls = [
    url(r'^$', station_views.station_list, name='station-list'),
    url(r'^create$', station_views.station_manage, name='station-create'),
    url(r'^delete$', station_views.station_delete, name='station-multi-delete'),
    url(r'^(?P<station_id>\d+)/',
        include([
            url(r'^$', station_views.station_display, name='station-detail'),
            url(r'^update$', station_views.station_manage, name='station-update'),
            url(r'^delete$', station_views.station_delete, name='station-delete'),
        ]
    )),
    
    # station assets urls
    url(r'^(?P<station_id>\d+)/(?P<asset_type_name>(transformers|feeders))/',
        include([
            url(r'^$', station_views.station_display, name='station-asset-list'),
            url(r'^create$', station_views.station_asset_manage, name='station-asset-create'),
            url(r'^(?P<asset_id>\d+)/',
                include([
                    url(r'^update$', station_views.station_asset_manage, name='station-asset-update'),
                ]
            )),
        ]
    )),
]

urlpatterns = [
    url(r'^ratings/transformers/', include(rating_transformer_urls)),
    url(r'^stations/(?P<type_name>(transmissions|injections|distributions))/', 
        include(station_urls)),
]

