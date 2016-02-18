from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _



MSG_REQUIRED_FIELD = _("This field cannot be null.")
MSG_INVALID_FORMAT = _("Format of provided data is invalid.")


def validate_powerline_code_format(value):
    value = (value or '').strip().upper()
    if len(value) in (4, 2) and value[0] in ['F','U']:
        start_char, number = value[0], None
        if start_char == 'F':
            if value[1] in ['1', '3']:
                number = value[2:]
        else:
            number = value[1]
        
        if number:
            try:
                if int(number, 16) > 0:
                    return value
            except:
                pass
    raise ValidationError(MSG_INVALID_FORMAT)


