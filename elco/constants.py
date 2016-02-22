from django.utils.translation import ugettext_lazy as _
from collections import OrderedDict



class Condition:
    """Provides a listing of equipment and device conditions."""
    UNKNOWN, OK, BURNT, DAMAGED, FAULTY = range(5)
    
    # display text
    _text = OrderedDict({
        UNKNOWN:'Unknown', 
        OK:'OK',
        BURNT: 'Burnt',
        DAMAGED:'Damaged',
        FAULTY:'Faulty',
    })
    
    # choices
    CHOICES = (
        (UNKNOWN, _text[UNKNOWN]),
        (OK,      _text[OK]),
        (BURNT,   _text[BURNT]),
        (DAMAGED, _text[DAMAGED]),
        (FAULTY,  _text[FAULTY]),
    )
    
    @staticmethod
    def get_display_text(value):
        """Returns the display text for the provided condition."""
        source = Condition._text
        if value not in source.keys():
            raise ValueError("Unknown condition value provided")
        return source[value]


class Voltage:
    """Defines the standard powerline voltages within the Nigerian power grid."""
    HVOLTH = 1
    HVOLTL = 2
    MVOLTH = 3
    MVOLTL = 4
    LVOLT  = 5
    
    # display text
    _text = OrderedDict({ 
        HVOLTH:'330KV', HVOLTL:'132KV',
        MVOLTH:'33KV',  MVOLTL:'11KV',
        LVOLT:'0.415KV'
    })
    
    # voltage choices
    FEEDER_CHOICES = (
        (MVOLTH, _text[MVOLTH]),
        (MVOLTL, _text[MVOLTL]),
    )
    
    UPRISER_CHOICES = (
        (LVOLT, _text[LVOLT]),
    )
    
    @staticmethod
    def get_display_text(value):
        """Returns the display text for the provided voltage value."""
        source = Voltage._text
        if value not in source.keys():
            raise ValueError(_("Unknown voltage value provided."))
        return source[value]
    
    @staticmethod
    def get_value_from_text(text):
        """Returns the defined constant value for the provided voltage text,
        which is expected to conform to the standard format.
        """
        text = (text or '').strip().replace(' ','').upper()
        for key, value in Voltage._text.items():
            if text == value:
                return key
        raise ValueError(_("Unknown voltage text provided"))
    
    
    class Ratio:
        """Defines input/output voltage ratios for stations and equipments."""
        HVOLTH_HVOLTL = 1
        HVOLTL_MVOLTH = 2
        HVOLTL_MVOLTL = 3
        MVOLTH_MVOLTL = 4
        MVOLTH_LVOLT  = 5
        MVOLTL_LVOLT  = 6
        
        # display text
        _text = OrderedDict({
            HVOLTH_HVOLTL:'330/132KV', HVOLTL_MVOLTH:'132/33KV',
            HVOLTL_MVOLTL:'132/11KV',  MVOLTH_MVOLTL:'33/11KV',
            MVOLTH_LVOLT:'33/0.415KV', MVOLTL_LVOLT:'11/0.415KV'
        })
        
        # choices
        CHOICES = (
            (HVOLTH_HVOLTL, _text[HVOLTH_HVOLTL]),
            (HVOLTL_MVOLTH, _text[HVOLTL_MVOLTH]),
            (HVOLTL_MVOLTL, _text[HVOLTL_MVOLTL]),
            (MVOLTH_MVOLTL, _text[MVOLTH_MVOLTL]),
            (MVOLTH_LVOLT, _text[MVOLTH_LVOLT]),
            (MVOLTL_LVOLT, _text[MVOLTL_LVOLT]),
        )
        
        TRANSMISSION_CHOICES = (
            (HVOLTH_HVOLTL, _text[HVOLTH_HVOLTL]),
            (HVOLTL_MVOLTH, _text[HVOLTL_MVOLTH]),
            (HVOLTL_MVOLTL, _text[HVOLTL_MVOLTL])
        )
        
        INJECTION_CHOICES = (
            (MVOLTH_MVOLTL, _text[MVOLTH_MVOLTL]),
        )
        
        DISTRIBUTION_CHOICES = (
            (MVOLTH_LVOLT, _text[MVOLTH_LVOLT]),
            (MVOLTL_LVOLT, _text[MVOLTL_LVOLT]),
        )
        
        @staticmethod
        def get_display_text(value):
            """Returns the display text for the provided voltage ratio value."""
            source = Voltage.Ratio._text
            if value not in source.keys():
                raise ValueError(_("Unknown voltage ratio value provided."))
            return source[value]
        
        @staticmethod
        def get_value_from_text(text):
            """Returns the defined constant value for the provided voltage 
            ratio text, which is expected to conform to the standard format.
            """
            text = (text or '').strip().replace(' ','').upper()
            for key, value in Voltage.Ratio._text.items():
                if text == value:
                    return key
            raise ValueError(_("Unknown voltage ratio text provided"))
        
        @staticmethod
        def get_hi_volt(value):
            text = Voltage.Ratio.get_display_text(value)
            portion_text = "%sKV" % text.split('/')[0]
            return Voltage.get_value_from_text(portion_text)
        
        @staticmethod
        def get_lo_volt(value):
            text = Voltage.Ratio.get_display_text(value)
            portion_text = text.split('/')[1]
            return Voltage.get_value_from_text(portion_text)


# convenience methods
get_condition_display = Condition.get_display_text
get_voltage_display = Voltage.get_display_text
get_ratio_display = Voltage.Ratio.get_display_text
