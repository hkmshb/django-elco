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
        
        self._assert_invalid_voltage_ratios(code='T101', 
            category=Station.TRANSMISSION, bad_ratios=bad_voltage_ratios)
    
    def test_rejects_invalid_voltage_ratios_for_injection(self):
        bad_voltage_ratios = (
            list(Voltage.Ratio.TRANSMISSION_CHOICES) +
            list(Voltage.Ratio.DISTRIBUTION_CHOICES))
        
        self._assert_invalid_voltage_ratios(code='I101',
            category=Station.INJECTION, bad_ratios= bad_voltage_ratios)
    
    def test_rejects_invalid_voltage_ratios_for_distribution(self):
        bad_voltage_ratios = (
            list(Voltage.Ratio.TRANSMISSION_CHOICES) +
            list(Voltage.Ratio.INJECTION_CHOICES))
        
        self._assert_invalid_voltage_ratios(code='S10001', 
            category=Station.DISTRIBUTION, bad_ratios=bad_voltage_ratios)
    
    def _assert_invalid_voltage_ratios(self, code, category, bad_ratios):
        for ratio in bad_ratios:
            bad_station = Station(
                code=code, name='Sample', category=category,
                voltage_ratio=ratio[0])
        
            with self.assertRaises(ValidationError) as ex:
                bad_station.full_clean()
            
            self.assertIn("Invalid voltage ratio", str(ex.exception))
    
    def test_code_len_notequal4_invalid_for_transmission(self):
        bad_codes = ('T10', 'T1001')
        for code in bad_codes:
            bad_station = Station(code=code, 
                name='Sample', category=Station.TRANSMISSION,
                voltage_ratio=Voltage.Ratio.HVOLTH_HVOLTL)
            
            self._assert_invalid_code(bad_station)
    
    def test_code_with_wrong_start_char_invalid_for_transmission(self):
        bad_codes = ('I101', 'S301')
        for code in bad_codes:
            bad_station = Station(code=code,
                name='Sample', category=Station.TRANSMISSION,
                voltage_ratio=Voltage.Ratio.HVOLTH_HVOLTL)
            
            self._assert_invalid_code(bad_station)
    
    def test_code_len_notequal4_invalid_for_injection(self):
        bad_codes = ('I10', 'I1001')
        for code in bad_codes:
            bad_station = Station(code=code,
                name='Sample', category=Station.INJECTION,
                voltage_ratio=Voltage.Ratio.MVOLTH_MVOLTL)
            
            self._assert_invalid_code(bad_station)
    
    def test_code_with_wrong_start_char_invalid_for_injection(self):
        bad_codes = ('T101', 'S101')
        for code in bad_codes:
            bad_station = Station(code=code,
                name='Sample', category=Station.INJECTION,
                voltage_ratio=Voltage.Ratio.MVOLTH_MVOLTL)
            
            self._assert_invalid_code(bad_station)
    
    def test_code_len_notequal6_invalid_for_distribution(self):
        bad_codes = ('S1000', 'S100001')
        for code in bad_codes:
            bad_station = Station(code=code,
                name='Sample', category=Station.DISTRIBUTION,
                voltage_ratio=Voltage.Ratio.MVOLTL_LVOLT)
            
            self._assert_invalid_code(bad_station)
    
    def test_code_with_wrong_start_char_invalid_for_distribution(self):
        bad_codes = ('T10001', 'I10001')
        for code in bad_codes:
            bad_station = Station(code=code,
                name='Sample', category=Station.DISTRIBUTION,
                voltage_ratio=Voltage.Ratio.MVOLTL_LVOLT)
            
            self._assert_invalid_code(bad_station)
    
    def test_code_with_wrong_embedded_voltage_ratio_for_transmisson(self):
        entries = (('T101', Voltage.Ratio.HVOLTH_HVOLTL),
                   ('T301', Voltage.Ratio.HVOLTL_MVOLTH))
        
        for code, voltage_ratio in entries:
            bad_station = Station(code=code,
                name='Sample', category=Station.TRANSMISSION,
                voltage_ratio=voltage_ratio)
            
            self._assert_invalid_code(bad_station)
    
    def test_code_with_wrong_embedded_voltage_ratio_for_injection(self):
        bad_station = Station(code='I101',
            name='Sample', category=Station.INJECTION,
            voltage_ratio=Voltage.Ratio.MVOLTH_MVOLTL)
        
        self._assert_invalid_code(bad_station)
    
    def test_code_with_wrong_embedded_voltage_ratio_for_distribution(self):
        entries = (('S10001', Voltage.Ratio.MVOLTH_LVOLT),
                   ('S30001', Voltage.Ratio.MVOLTL_LVOLT))
        
        for code, voltage_ratio in entries:
            bad_station = Station(code=code,
                name='Sample', category=Station.DISTRIBUTION,
                voltage_ratio=voltage_ratio)
            
            self._assert_invalid_code(bad_station)
    
    def _assert_invalid_code(self, station):
        with self.assertRaises(ValidationError) as ex:
            station.full_clean()
        
        self.assertIn("Invalid station code format", str(ex.exception))
