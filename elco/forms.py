from django.utils.translation import ugettext_lazy as _
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


