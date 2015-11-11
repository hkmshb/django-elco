


class Voltage:
    """
    Defines standard power line voltages within the Nigerian power grid.
    """
    class Text:
        HVOLT_H = '330KV'
        HVOLT_L = '132KV'
        MVOLT_H = '33KV'
        MVOLT_L = '11KV'
        LVOLT   = '0.415KV'
    
    # Voltage Values
    HVOLT_H = 1
    HVOLT_L = 2
    MVOLT_H = 3
    MVOLT_L = 4
    LVOLT   = 5
    
    
    class Ratio:
        """
        Defines input/output voltage ratios for stations and equipments.
        """
        class Text:
            """
            Defines text for the voltage ratios.
            """
            HVOLTH_2_HVOLTL = '330/132KV'
            HVOLTL_2_MVOLTH = '132/33KV'
            HVOLTL_2_MVOLTL = '132/11KV'
            MVOLTH_2_MVOLTL = '33/11KV'
            MVOLTH_2_LVOLT  = '33/0.415KV'
            MVOLTL_2_LVOLT  = '11/0.415KV'
        
        # Voltage Ratio Values
        HVOLTH_2_HVOLTL = 1
        HVOLTL_2_MVOLTH = 2
        HVOLTL_2_MVOLTL = 3
        MVOLTH_2_MVOLTL = 4
        MVOLTH_2_LVOLT  = 5
        MVOLTL_2_LVOLT  = 6
        
        # Voltage Ratio Choices
        TRANSMISSION_CHOICES = (
            (HVOLTH_2_HVOLTL, Text.HVOLTH_2_HVOLTL),
            (HVOLTL_2_MVOLTH, Text.HVOLTL_2_MVOLTH),
            (MVOLTH_2_MVOLTL, Text.MVOLTH_2_MVOLTL),
        )
        
        DISTRIBUTION_CHOICES = (
            (MVOLTH_2_LVOLT, Text.MVOLTH_2_LVOLT),
            (MVOLTL_2_LVOLT, Text.MVOLTL_2_LVOLT),
        )
        
        ALL_CHOICES = (
            (HVOLTH_2_HVOLTL, Text.HVOLTH_2_HVOLTL),
            (HVOLTL_2_MVOLTH, Text.HVOLTL_2_MVOLTH),
            (MVOLTH_2_MVOLTL, Text.MVOLTH_2_MVOLTL),
            (MVOLTH_2_LVOLT, Text.MVOLTH_2_LVOLT),
            (MVOLTL_2_LVOLT, Text.MVOLTL_2_LVOLT),
        )
