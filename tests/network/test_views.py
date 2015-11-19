from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse

from elco.network.constants import Voltage
from elco.network.models import Station
from elco.network import views

from ..factories import StationFactory



class StationListViewTest(TestCase):
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_can_list_stations_by_type(self):
        common = dict(voltage_ratio = Voltage.Ratio.HVOLTL_2_MVOLTH,
                      type = Station.TRANSMISSION) 
        StationFactory(code='TS0X', name='Station 0X', **common)
        StationFactory(code='TS0Y', name='Station 0Y', **common)
        StationFactory(code='TS0Z', name='Station 0Z', **common)
        
        station_type_name = 'transmissions'
        url = reverse('station-list', args=[station_type_name])
        request = self.factory.get(url)
        
        resp = views.station_list(request, station_type_name, 'elco/station/base.html')
        self.assertEqual(200, resp.status_code)
        
        context = resp.context_data
        self.assertTrue(context['station_type_name'], station_type_name)
        self.assertEqual(3, len(context['records']))
    