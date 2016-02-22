from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django import forms

from .models import Station, PowerLine
from .constants import Voltage


MSG_INVALID_XFMR_CAPACITY = _("Invalid power transformer capacity")
MSG_INVALID_VOLTAGE_RATIO = _("Invalid voltage ratio value or text")



def build_transformer_rating_code(capacity, voltage_ratio):
    """Builds a Transformer Rating code based on the rules captured
    as a docstring under TransformerRating model.
    
    :capacity: Transformer capacity in KVA
    :voltage_ratio: This can be the numeric constant for a voltage ratio as 
            defined under Voltage or the string of the voltage ratio in the
            proper format e.g. 33/11KV.
    """
    VR, voltage_ratio_text = Voltage.Ratio, None
    POWER_VRS = (VR.HVOLTL_MVOLTH, VR.HVOLTL_MVOLTL, VR.MVOLTH_MVOLTL)
    
    if type(voltage_ratio) is str:
        try:
            value = VR.get_value_from_text(voltage_ratio)
            voltage_ratio_text, voltage_ratio = voltage_ratio, value
        except:
            try:
                value = int(voltage_ratio)
                voltage_ratio = value
            except:
                raise ValueError(MSG_INVALID_VOLTAGE_RATIO)
        
    if not voltage_ratio_text:
        # ensure voltage ratio value is unknown
        voltage_ratio_text = VR.get_display_text(voltage_ratio)
    
    # encode transformer type and voltage ratio
    xfmr_type = ('P' if voltage_ratio in POWER_VRS else 'D')
    xfmr_vr = voltage_ratio_text.replace('KV', '')
    xfmr_vr = xfmr_vr[-1] if xfmr_type == 'P' else xfmr_vr[0]
    
    xfmr_cap = ''
    if capacity < 1000:
        if xfmr_type == 'P':
            raise ValueError(MSG_INVALID_XFMR_CAPACITY)
        xfmr_cap ='{:0>3}'.format(capacity)
    else:
        quotient, remainder = (capacity // 1000), (capacity % 1000)
        if quotient >= 1000:
            raise ValueError(MSG_INVALID_XFMR_CAPACITY)
        
        if remainder == 0:
            xfmr_cap = ('{:0>2}M' if quotient < 100 else '{}').format(str(quotient))
        else:
            xfmr_cap = '{}{[0]}m'.format(str(quotient), str(remainder))
        
    code = '{}{}{}'.format(xfmr_type, xfmr_vr, xfmr_cap)
    if len(code) != 5:
        raise ValueError(MSG_INVALID_XFMR_CAPACITY)
    return code


def _make_generator(choices, text="One", unpack_model=None):
    def func():
        label = mark_safe("%s Select %s %s" % ('&laquo;', text, '&raquo;'))
        yield (None, label)
        
        for choice in choices:
            choice = choice if not unpack_model else unpack_model(choice)
            yield choice
    return func


class StationForm(forms.ModelForm):
    
    class Meta:
        model = Station
        fields = ['code', 'alt_code', 'name', 'category', 'voltage_ratio',
                  'source_feeder', 'address', 'public', 'date_commissioned',
                  'notes']
    
    def __init__(self, category, *args, **kwargs):
        super(StationForm, self).__init__(*args, **kwargs)
        self._prep_voltage_ratio_field(category)
        self._prep_source_feeder_field(category)
        self._prep_category_field(category)
    
    def _prep_category_field(self, category):
        field_key = 'category'
        if category:
            self.fields[field_key].widget.attrs['disabled'] = True
            self.fields[field_key].initial = category
        else:
            choices = _make_generator(Station.CATEGORY_CHOICES)
            self.fields[field_key].choices = choices
    
    def _prep_source_feeder_field(self, category):
        # expects 33KV feeder as source; distribution substations are
        # some what a misnoma as can accept both 33KV & 11KV source. 
        if category == Station.TRANSMISSION:
            choices = _make_generator([], "Not Applicable")
        else:
            manager = PowerLine.objects
            records = (manager.all() 
                if category == Station.DISTRIBUTION else
                    manager.filter(voltage=Voltage.MVOLTH))
            choices = _make_generator(records, unpack_model=lambda r: (r.id, r))
        
        # prepare field
        field_key = 'source_feeder'
        self.fields[field_key].choices = choices
        if category == Station.TRANSMISSION:
            del self.fields[field_key]
    
    def _prep_voltage_ratio_field(self, category):
        VR, choices = Voltage.Ratio, Voltage.Ratio.CHOICES
        if category == Station.TRANSMISSION:
            choices = VR.TRANSMISSION_CHOICES
        elif category == Station.INJECTION:
            choices = VR.INJECTION_CHOICES
        elif category == Station.DISTRIBUTION:
            choices = VR.DISTRIBUTION_CHOICES
        
        choices_gen = _make_generator(choices)
        self.fields['voltage_ratio'].choices = choices_gen


class PowerLineForm(forms.ModelForm):
    
    class Meta:
        model = PowerLine
        fields = ['code', 'alt_code', 'name', 'type', 'voltage', 'public',
                  'source_station', 'date_commissioned', 'notes']

    def __init__(self, line_type, source_station, hide_widgets=False,
                  *args, **kwargs):
        super(PowerLineForm, self).__init__(*args, **kwargs)
        self.hide_widgets = hide_widgets
        if source_station:
            line_type = (PowerLine.UPRISER 
                if source_station.category == Station.DISTRIBUTION
                    else PowerLine.FEEDER)
        
        self._prep_line_type_field(line_type)
        self._prep_voltage_field(line_type, source_station)
        self._prep_source_station(line_type, source_station)
    
    def _prep_line_type_field(self, line_type):
        field_key = 'type'
        if line_type:
            self.fields[field_key].initial = line_type
            if not self.hide_widgets:
                self.fields[field_key].widget.attrs['disabled'] = True
            else:
                del self.fields[field_key]
        else:
            choices = _make_generator(PowerLine.POWERLINE_CHOICES)
            self.fields[field_key].choices = choices
    
    def _prep_voltage_field(self, line_type, source_station):
        choices = PowerLine.VOLTAGE_CHOICES
        if line_type == PowerLine.FEEDER:
            choices = Voltage.FEEDER_CHOICES
        elif line_type == PowerLine.UPRISER:
            choices = Voltage.UPRISER_CHOICES
        
        choices_gen = _make_generator(choices)
        self.fields['voltage'].choices = choices_gen
        
        # settings based on source station
        if source_station:
            # get lv-/output-side voltage text
            station_out = source_station.get_voltage_ratio_display()
            station_out = station_out.split('/')[1]
            
            # get voltage value with corresponding text as above
            voltage = Voltage.get_value_from_text(station_out)
            
            field_key = 'voltage'
            self.fields[field_key].initial = voltage
            if not self.hide_widgets:
                self.fields[field_key].widget.attrs['disabled'] = True
            else:
                del self.fields[field_key]
    
    def _prep_source_station(self, line_type, source_station):
        manager = Station.objects
        if not line_type:
            records = manager.all()
        else:
            if line_type == PowerLine.UPRISER:
                records = manager.filter(category=Station.DISTRIBUTION)
            else:
                expected = (Station.TRANSMISSION, Station.INJECTION)
                records = manager.filter(category__in=expected)
        
        choices = _make_generator(records, unpack_model=lambda r: (r.code, r))
        
        # prepare field
        field_key = 'source_station'
        self.fields[field_key].choices = choices
        
        if source_station:
            self.fields[field_key].initial = source_station.code
            if not self.hide_widgets:
                self.fields[field_key].widget.attrs['disabled'] = True
            else:
                del self.fields[field_key]

