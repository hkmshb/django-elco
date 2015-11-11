from django.test import TestCase
from django.core.exceptions import ValidationError

from ..factories import StationFactory, PowerLineFactory
from elco.network.models import Station, PowerLine
from elco.core.places import State



class StationTestCase(TestCase):
    
    def test_address_omits_unavailable_address_fields(self):
        obj = StationFactory.build(address_line1='Address line #1',
                city='Kano',
                state=State.KANO)
        self.assertEqual('Address line #1, Kano, Kano', obj.address)
    
    def test_address_with_complete_address_fields(self):
        obj = StationFactory.build(address_line1='Address line #1',
                address_line2='line #2',
                city='Kano',
                state=State.KANO)
        self.assertEqual('Address line #1, line #2, Kano, Kano', obj.address)
    
    def test_duplicate_codes_are_invalid(self):
        station = StationFactory(code='TS-0X')
        with self.assertRaises(ValidationError):
            obj = StationFactory.build(code='TS-0X', name='Station')
            obj.full_clean()


class PowerLineTestCase(TestCase):
    
    def test_duplicate_codes_are_invalid(self):
        pwln = PowerLineFactory(code='FX00X', name='Feeder 0X')
        with self.assertRaises(ValidationError):
            obj = PowerLineFactory.build(code='FX00X', name='Feeder 0Y')
            obj.full_clean()
    
    