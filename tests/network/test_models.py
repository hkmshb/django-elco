from django.test import TestCase
from django.core.exceptions import ValidationError

from ..factories import StationFactory, PowerLineFactory, \
        TransformerRatingFactory, TransformerFactory

from elco.network.models import Station, PowerLine
from elco.network.constants import Voltage
from elco.core.places import State

from elco.network.forms import build_transformer_rating_code



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


class TransformerRatingTest(TestCase):
    
    def test_code_missing_transformer_type_char_are_invalid(self):
        obj = TransformerRatingFactory.build(code='3060',
                capacity=60000,
                voltage_ratio=Voltage.Ratio.HVOLTL_2_MVOLTH)
        
        with self.assertRaises(ValidationError):
            obj.clean_fields()  # missing P or D
    
    def test_code_with_invalid_xfmr_type_char_are_invalid(self):
        obj = TransformerRatingFactory.build(code='p3060',
                capacity=60000,
                voltage_ratio=Voltage.Ratio.HVOLTL_2_MVOLTH)
        
        with self.assertRaises(ValidationError):
            obj.clean_fields()  # not expected: p in code
    
    def test_code_without_unit_for_fraction_capacity_are_invalid(self):
        obj = TransformerRatingFactory.build(code='P3060',
                capacity=6000,
                voltage_ratio=Voltage.Ratio.HVOLTL_2_MVOLTH)
        
        with self.assertRaises(ValidationError):
            obj.full_clean()    # expects: P360m
    
    def test_code_with_invalid_unit_char_are_invalid(self):
        obj = TransformerRatingFactory.build(code='D350K',
                capacity=50,
                voltage_ratio=Voltage.Ratio.MVOLTH_2_LVOLT)
        
        with self.assertRaises(ValidationError):
            obj.full_clean()    # not expected: K at code end
    
    def test_code_with_fraction_unit_matches_for_fraction_capacity(self):
        obj = TransformerRatingFactory.build(code='P375m',
                capacity=7500,
                voltage_ratio=Voltage.Ratio.HVOLTL_2_MVOLTH)
        
        obj.full_clean()        # should not raise error

    #+
    #| RatingCodeBuildTest(TestCase):
    #+------------------------------------------------------------------------+
    
    def test_builds_with_mult_for_5digit_power_xfmr(self):
        code = build_transformer_rating_code(60000, '132/33KV')
        self.assertEqual('P360M', code)
    
    def test_builds_with_mult_for_4digit_power_xfmr(self):
        code = build_transformer_rating_code(5000, '132/33KV')
        self.assertEqual('P305M', code)
    
    def test_builds_with_fmult_for_4fracdigit_power_xfmr(self):
        code = build_transformer_rating_code(7500, '132/33KV')
        self.assertEqual('P375m', code)
    
    def test_builds_without_mult_for_3digit_dist_xfmr(self):
        code = build_transformer_rating_code(500, '33/0.415KV')
        self.assertEqual('D3500', code)

