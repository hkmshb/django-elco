from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Station, PowerLine, TransformerRating, Transformer
from .constants import Voltage



def build_transformer_rating_code(capacity, voltage_ratio):
    POWER_VRS = (Voltage.Ratio.Text.HVOLTL_2_MVOLTH,
                 Voltage.Ratio.Text.HVOLTL_2_MVOLTL,
                 Voltage.Ratio.Text.MVOLTH_2_MVOLTL)
    
    DIST_VRS  = (Voltage.Ratio.Text.MVOLTH_2_LVOLT, 
                 Voltage.Ratio.Text.MVOLTL_2_LVOLT)
    
    # normalize voltage ration
    voltage_ratio = voltage_ratio.replace(' ', '').upper()
    if voltage_ratio not in POWER_VRS and voltage_ratio not in DIST_VRS:
        raise ValueError(_("Invalid Voltage Ratio value"))
    
    # encode transformer type and voltage ratio
    xfmr_type = 'P' if voltage_ratio in POWER_VRS else 'D'
    xfmr_vr = voltage_ratio.replace('KV', '')
    xfmr_vr = xfmr_vr[-1] if xfmr_type == 'P' else xfmr_vr[0]
    
    err_message = _("Invalid power transformer capacity")
    xfmr_cap = ''
    if capacity < 1000:
        if xfmr_type == 'P':
            raise ValueError(err_message)
        else:
            xfmr_cap = '{:0>3}'.format(capacity)
    else:
        quotient, remainder = (capacity // 1000), (capacity % 1000)
        if quotient >= 1000:
            raise ValueError(err_message)
        
        if remainder == 0:
            xfmr_cap = ('{:0>2}M' if quotient < 100 else '{}').format(str(quotient))
        else:
            xfmr_cap = '{}{[0]}m'.format(str(quotient), str(remainder))
    
    code = '{}{}{}'.format(xfmr_type, xfmr_vr, xfmr_cap)
    if len(code) != 5:
        raise ValueError(err_message)
    return code


class StationForm(forms.ModelForm):
    
    class Meta:
        model = Station
        fields = [
            'code', 'name', 'type', 'voltage_ratio', 'source_feeder', 
            'address_line1', 'address_line2', 'city', 'state', 
            'is_dedicated', 'date_commissioned', 'notes'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows':2,})
        }


class PowerLineForm(forms.ModelForm):
    
    class Meta:
        model = PowerLine
        fields = [
            'code', 'name', 'type', 'voltage', 'is_dedicated',
            'source_station', 'date_commissioned', 'notes',
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2, })
        }


class TransformerRatingForm(forms.ModelForm):
     
    class Meta:
        model = TransformerRating
        fields = ['code', 'capacity', 'voltage_ratio', 'notes']


class TransformerForm(forms.ModelForm):
    
    class Meta:
        model = Transformer
        fields = [
            'condition', 'station', 'rating', 'date_installed', 'serialno', 
            'model', 'manufacturer', 'date_manufactured', 'notes',
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2, })
        }

