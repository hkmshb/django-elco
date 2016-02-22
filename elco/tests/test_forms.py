from django.test import TestCase
from ..forms import PowerLineForm, StationForm
from ..models import PowerLine, Station
from ..constants import Voltage



class BaseFormTestCase(TestCase):
    
    def _assert_field_disabled(self, form, field_name):
        self.assertIn('disabled', form.fields[field_name].widget.attrs)
    
    def _assert_field_not_disabled(self, form, field_name):
        self.assertNotIn('disabled', form.fields[field_name].widget.attrs)


class StationFormTestCase(BaseFormTestCase):
    
    def setUp(self):
        pass
    
    def test_category_not_disabled_for_unconstrained_form(self):
        self._assert_field_not_disabled(StationForm(), 'category')
    
    def test_voltage_ratio_not_disabled_for_unconstrained_form(self):
        self._assert_field_not_disabled(StationForm(), 'voltage_ratio')
    
    def test_source_feeder_not_disabled_for_unconstrained_form(self):
        self._assert_field_not_disabled(StationForm(), 'source_feeder')
    
    def test_category_disabled_for_category_constrained_form(self):
        form = StationForm(Station.TRANSMISSION)
        self._assert_field_disabled(form, 'category')
    
    def test_source_feeder_removed_for_transmission_constrained_form(self):
        form = StationForm(Station.TRANSMISSION)
        self.assertNotIn('source_feeder', form.fields.keys())


class PowerLineFormTestCase(BaseFormTestCase):
    
    def setUp(self):
        self.station = Station.objects.create(
                            code='I301', name='Sample IS',
                            category=Station.INJECTION, 
                            voltage_ratio=Voltage.Ratio.HVOLTL_MVOLTH)
    
    def test_type_not_disabled_for_unconstrained_form(self):
        self._assert_field_not_disabled(PowerLineForm(), 'type')
    
    def test_voltage_not_disabled_for_unconstrained_form(self):
        self._assert_field_not_disabled(PowerLineForm(), 'voltage')
    
    def test_source_station_not_disabled_for_unconstrained_form(self):
        self._assert_field_not_disabled(PowerLineForm(), 'source_station')
    
    def test_type_disabled_for_type_constrained_form(self):
        form = PowerLineForm(PowerLine.FEEDER)
        self._assert_field_disabled(form, 'type')
    
    def test_source_station_disabled_for_source_station_constrained_form(self):
        form = PowerLineForm(None, self.station)
        self._assert_field_disabled(form, 'source_station')
    
    def test_type_disabled_for_source_station_constrained_form(self):
        form = PowerLineForm(None, self.station)
        self._assert_field_disabled(form, 'type')
    
    def test_voltage_disabled_for_source_station_constrained_form(self):
        form = PowerLineForm(None, self.station)
        self._assert_field_disabled(form, 'voltage')
    
    def test_MVHOLTx_voltage_available_for_feeder_type_constrained_form(self):
        form = PowerLineForm(PowerLine.FEEDER)
        choices = list(form.fields['voltage'].choices)
        self.assertEqual(3, len(choices))
        voltages = [choice[0] for choice in choices]
        self.assertIn(Voltage.MVOLTH, voltages)
        self.assertIn(Voltage.MVOLTL, voltages)
        self.assertNotIn(Voltage.LVOLT, voltages)
    
    def test_hi_me_source_station_available_for_feeder_type_constrained_form(self):
        form = PowerLineForm(PowerLine.FEEDER)
        choices = list(form.fields['source_station'].choices)
        if len(choices) > 1:
            names = str([str(choice[1]) for choice in choices])
            self.assertTrue('11KV' in names or '33KV' in names)
            self.assertTrue('0.415KV' not in names)
    
    def test_lo_source_station_available_for_upriser_type_constrained_form(self):
        form = PowerLineForm(PowerLine.UPRISER)
        choices = list(form.fields['source_station'].choices)
        if len(choices) > 1:
            names = str([str(choice[1]) for choice in choices])
            self.assertTrue('0.415KV' in names)
            self.assertTrue('11KV' not in names and '33KV' not in names and
                            '132KV' not in names and '330KV' not in names)

