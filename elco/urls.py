from django.conf.urls import include, url
from .network import urls as network_urls


urlpatterns = [
    url(r'^network/', include(network_urls)),
]
