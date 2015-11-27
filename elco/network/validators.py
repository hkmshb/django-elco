from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .constants import Voltage



def validate_transformer_rating_code_format(value):
    err_message = _("Invalid Transformer Rating code format")
    if (value and len(value) == 5 and value[0] in ('P', 'D') and 
        value[1] in ('3', '1')):
        digits = value[2:] if value[-1] not in ('M', 'm') else value[2:-1]
        
        try: return int(digits)
        except: pass
    raise ValidationError(err_message)


def validate_transformer_rating_code(code, capacity, voltage_ratio):
    err_message = _("This field is required")
    if not code:
        raise ValidationError(err_message)
    
    err_message = _("Mismatch between Transformer Rating code and values")
    
    # validate coded capacity
    coded_capacity = (code[2:] if code[-1] not in ('M', 'm') else code[2:-1])
    multiplier = (1 if code[-1] not in ('M','m') else 
                    100 if code[-1] == 'm' else 1000)
    
    try:
        coded_value = int(coded_capacity) * multiplier
    except:
        raise ValidationError(err_message)
    
    if coded_value != capacity:
        raise ValidationError(err_message)
    
    # validate coded voltage ratio
    expected = []
    if code[0] == 'P':
        expected = ((Voltage.Ratio.HVOLTL_2_MVOLTH,)
                        if code[1] == '3'
                        else (Voltage.Ratio.HVOLTL_2_MVOLTH,
                              Voltage.Ratio.MVOLTH_2_MVOLTL))
    else:
        expected = ((Voltage.Ratio.MVOLTH_2_LVOLT,)
                        if code[1] == '3'
                        else (Voltage.Ratio.MVOLTL_2_LVOLT,))
    if voltage_ratio not in expected:
        raise ValidationError(err_message)

