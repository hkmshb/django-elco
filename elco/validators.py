from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from .constants import Voltage

MSG_REQUIRED_FIELD = _("This field cannot be null.")
MSG_INVALID_FORMAT = _("The format of provided code is invalid.")
MSG_MISMATCH_RATING_CODE_VALUE = _(
    "There is a mismatch between Transformer Rating code and values")



def validate_station_code_format(value):
    value = (value or '').strip().upper()
    if len(value) in (6, 4) and value[0] in ('T','I','S'):
        start_char, involt, number = value[0], value[1], None
        if involt in ['1', '3']:
            if start_char == 'S' and len(value) == 6:
                number = value[-4:]
            elif start_char in ('T', 'I') and len(value) == 4:
                if not (start_char == 'I' and involt != '3'):
                    number = value[-2:]
        
        if number:
            try:
                if int(number, 16) > 0:
                    return value
            except:
                pass
    raise ValidationError(MSG_INVALID_FORMAT, code='invalid')


def validate_powerline_code_format(value):
    value = (value or '').strip().upper()
    if len(value) in (4, 2) and value[0] in ('F','U'):
        start_char, number = value[0], None
        if start_char == 'F' and len(value) == 4:
            if value[1] in ['1', '3']:
                number = value[2:]
        elif start_char == 'U' and len(value) == 2:
            number = value[1]
        
        if number:
            try:
                if int(number, 16) > 0:
                    return value
            except:
                pass
    raise ValidationError(MSG_INVALID_FORMAT)


def validate_transformer_rating_code_format(value):
    value = (value or '').strip().upper()
    if len(value) == 5 and value[0] in ('P', 'D') and value[1] in ('3', '1'):
        digits = (value[2:] if value[-1] not in ('M','m') else value[2:-1])
        try:
            return int(digits)
        except:
            pass
    return ValidationError(MSG_INVALID_FORMAT)


def validate_transformer_rating_code(code, capacity, voltage_ratio):
    # note do not convert code to all uppercase.
    code = (code or '').strip()
    if not code:
        raise ValidationError(MSG_REQUIRED_FIELD)
    
    # validate coded capacity
    coded_capacity = (code[2:] if code[-1] not in ('M','m') else code[2:-1])
    multiplier = (1 if code[-1] not in ('M','m') else 
                    100 if code[-1] == 'm' else 1000)
    
    try:
        coded_value = int(coded_capacity) * multiplier
    except:
        raise ValidationError(MSG_MISMATCH_RATING_CODE_VALUE)
    
    if coded_value != capacity:
        raise ValidationError(MSG_MISMATCH_RATING_CODE_VALUE)
    
    # validate coded voltage ratio
    expected_values, VR = None, Voltage.Ratio
    if code[0] == 'P':
        # VR code comes from low-voltage side of VR text value
        if code[1] == 3:
            expected_values = (VR.HVOLTL_MVOLTH,)
        elif code[1] == '1':
            expected_values = (VR.HVOLTL_MVOLTL, VR.MVOLTH_MVOLTL)
    elif code[1] == 'D':
        # VR code comes from high-voltage side of VR text value
        if code[1] == 3:
            expected_values = (VR.MVOLTH_LVOLT,)
        else:
            expected_values =(VR.MVOLTL_LVOLT,)
    
    if voltage_ratio in (expected_values or []):
        raise ValidationError(MSG_MISMATCH_RATING_CODE_VALUE)

