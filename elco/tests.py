from django.test import TestCase
from django.core.exceptions import ValidationError

from .models import Station
from .constants import Condition, Voltage



class StationTestCase(TestCase):
    def setUp(self):
        self.station = Station(code='T101', name='Sample', 
                               category=Station.TRANSMISSION,
                               voltage_ratio=Voltage.Ratio.HVOLTL_MVOLTH)
    
    def test_string_repr(self):
        self.assertEqual('Sample 132/33KV', str(self.station))
    
    def test_rejects_invalid_voltage_ratios_for_transmission(self):
        bad_voltage_ratios = (
            list(Voltage.Ratio.INJECTION_CHOICES) +
            list(Voltage.Ratio.DISTRIBUTION_CHOICES))
        
        self._test_rejects_invalid_voltage_ratios(code='T101', 
            category=Station.TRANSMISSION, bad_ratios=bad_voltage_ratios)
    
    def test_rejects_invalid_voltage_ratios_for_injection(self):
        bad_voltage_ratios = (
            list(Voltage.Ratio.TRANSMISSION_CHOICES) +
            list(Voltage.Ratio.DISTRIBUTION_CHOICES))
        
        self._test_rejects_invalid_voltage_ratios(code='I101',
            category=Station.INJECTION, bad_ratios= bad_voltage_ratios)
    
    def test_rejects_invalid_voltage_ratios_for_distribution(self):
        bad_voltage_ratios = (
            list(Voltage.Ratio.TRANSMISSION_CHOICES) +
            list(Voltage.Ratio.INJECTION_CHOICES))
        
        self._test_rejects_invalid_voltage_ratios(code='S10001', 
            category=Station.DISTRIBUTION, bad_ratios=bad_voltage_ratios)
    
    def _test_rejects_invalid_voltage_ratios(self, code, category, bad_ratios):
        for ratio in bad_ratios:
            bad_station = Station(
                code=code, name='Sample', category=category,
                voltage_ratio=ratio[0])
        
            with self.assertRaises(ValidationError) as ex:
                bad_station.full_clean()
            
            self.assertIn("Invalid voltage ratio", str(ex.exception))

