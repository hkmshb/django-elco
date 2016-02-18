from django.test import TestCase
from django.core.exceptions import ValidationError

from .models import Station, PowerLine, MSG_XSTATION_INPUT_MISMATCH_FEEDER,\
        MSG_TSTATION_SOURCE_FEEDER_NOT_SUPPORTED
from .constants import Condition, Voltage
from .validators import validate_powerline_code_format,\
        MSG_REQUIRED_FIELD, MSG_INVALID_FORMAT



class StationTestCase(TestCase):
    
    def setUp(self):
        self.station = Station(
            code='T101', name='Sample', 
            category=Station.TRANSMISSION,
            voltage_ratio=Voltage.Ratio.HVOLTL_MVOLTH)
        
        self.trans_station = Station.objects.create(
            code='T102', name='Sample Station',
            category=Station.TRANSMISSION,
            voltage_ratio=Voltage.Ratio.HVOLTL_MVOLTH)
    
    def test_string_repr(self):
        self.assertEqual('Sample 132/33KV', str(self.station))
    
    def test_stations_have_unique_name_category_pair(self):
        # self.trans_station already exist here, station here tries
        # to duplicate name category pair
        station = Station(code='T103', name='Sample Station',
                    category=Station.TRANSMISSION,
                    voltage_ratio=Voltage.Ratio.HVOLTL_MVOLTH)
        
        with self.assertRaises(ValidationError) as ex:
            station.full_clean()
    
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
    
    def test_passes_validation_with_valid_code(self):
        codes = ('T110', 'T1ff')
        for code in codes:
            station = Station(code=code,
                name='Sample', category=Station.TRANSMISSION,
                voltage_ratio=Voltage.Ratio.HVOLTL_MVOLTH)
            station.full_clean()
    
    def _assert_invalid_code(self, station):
        with self.assertRaises(ValidationError) as ex:
            station.full_clean()
        
        self.assertIn("Invalid station code format", str(ex.exception))
    
    def test_transmission_with_source_feeder_not_acceptable(self):
        feeder = PowerLine.objects.create(
                    code='F301', name='Sample Feeder',
                    type=PowerLine.FEEDER, public=True,
                    voltage=Voltage.MVOLTH,
                    source_station=self.trans_station)
        
        with self.assertRaises(ValidationError) as ex:
            self.station.source_feeder = feeder
            self.station.full_clean()
        
        self.assertIn(str(MSG_TSTATION_SOURCE_FEEDER_NOT_SUPPORTED),
                      str(ex.exception))
    
    def test_substations_without_source_feeder_acceptable(self):
        station = Station(code='I301', name='Sample Station',
                    category=Station.INJECTION,
                    voltage_ratio=Voltage.Ratio.MVOLTH_MVOLTL)
        station.full_clean()
        
        station = Station(code='S10001', name='Sample Station',
                    category=Station.DISTRIBUTION,
                    voltage_ratio=Voltage.Ratio.MVOLTL_LVOLT)
        station.full_clean()
    
    def test_nonmatching_source_feeder_for_substation_invalid(self):
        feeder = PowerLine.objects.create(
                    code='F101', name='Sample Feeder',
                    type=PowerLine.FEEDER, public=True,
                    voltage=Voltage.MVOLTL,
                    source_station=self.trans_station)
        
        with self.assertRaises(ValidationError) as ex:
            station = Station(code='I301', name='Sample Station',
                        category=Station.INJECTION,
                        voltage_ratio=Voltage.Ratio.MVOLTH_MVOLTL,
                        source_feeder=feeder)
            station.full_clean()
        
        self.assertIn(str(MSG_XSTATION_INPUT_MISMATCH_FEEDER),
                      str(ex.exception))


class PowerLineTestCase(TestCase):
    
    def setUp(self):
        self.station = Station.objects.create(
                code='T10A', name='Sample TS', 
                category=Station.TRANSMISSION,
                voltage_ratio=Voltage.Ratio.HVOLTL_MVOLTH)
        
        self.powerline = PowerLine(
                code='F30A', name='Sample Feeder',
                type=PowerLine.FEEDER, voltage=Voltage.MVOLTH,
                source_station=self.station)
    
    def test_powerline_without_source_station_invalid(self):
        powerline = PowerLine(code='F30B', name='Sample PowerLine',
                        type=PowerLine.FEEDER, voltage=Voltage.MVOLTH)
        
        with self.assertRaises(ValidationError) as ex:
            powerline.full_clean()
            
        self.assertIn(str(MSG_REQUIRED_FIELD), str(ex.exception))
    
    # orig: test_code_start_char_appropriate_for_type(self):
    def test_code_with_wrong_start_char_invalid_for_feeder(self):
        pass


class ValidationTestCase(TestCase):
    
    def test_powerline_code_with_zero_as_number_invalid(self):
        not_allowed = ('F100', 'F300', 'U0')
        for code in not_allowed:
            self._assert_invalid_powerline_code_format(code)
    
    def test_powerline_code_invalid_for_wrong_start_chars(self):
        invalid_start_chars = 'ABCDEGHIJKLMNOPQRSTVWXYZ'
        for char in invalid_start_chars:
            code = '%s101' % char
            self._assert_invalid_powerline_code_format(code)
    
    def test_feeder_code_invalid_for_wrong_length(self):
        # feeder code (starts with F) length = 4
        bad_codes = ('F10', 'F1001')
        for code in bad_codes:
            self._assert_invalid_powerline_code_format(code)
    
    def test_feeder_code_invalid_for_wrong_embedded_voltage_digit_range(self):
        # expected embedded digits are 1=11KV, 3=33KV
        invalid_digits = '02456789'
        for digit in invalid_digits:
            code = 'F%s01' % digit
            self._assert_invalid_powerline_code_format(code)
    
    def test_feeder_code_invalid_for_nonhex_number(self):
        invalid_chars = 'GHIJKLMNOPQRSTUVWXYZ'
        for char in invalid_chars:
            code = 'F10%s' % char
            self._assert_invalid_powerline_code_format(code)
    
    def test_upriser_code_invalid_for_wrong_length(self):
        # upriser code (starts with U) length = 2
        bad_codes = ('U', 'U01', 'U012')
        for code in bad_codes:
            self._assert_invalid_powerline_code_format(code)
    
    def test_upriser_code_invalid_for_nonhex_number(self):
        invalid_chars = 'GHIJKLMNOPQRSTUVWXYZ'
        for char in invalid_chars:
            code = 'U%s' % char
            self._assert_invalid_powerline_code_format(code)
    
    def _assert_invalid_powerline_code_format(self, code):
        with self.assertRaises(ValidationError) as ex:
            validate_powerline_code_format(code)
        
        self.assertIn(str(MSG_INVALID_FORMAT), str(ex.exception))