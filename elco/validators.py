from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


MSG_REQUIRED_FIELD = _("This field cannot be null.")
MSG_INVALID_FORMAT = _("Format of provided data is invalid.")



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
    raise ValidationError(MSG_INVALID_FORMAT)


def validate_powerline_code_format(value):
    value = (value or '').strip().upper()
    if len(value) in (4, 2) and value[0] in ['F','U']:
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


