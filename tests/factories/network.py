"""
"""
from datetime import datetime

import factory
from elco.network.models import Station, PowerLine
from elco.network.constants import Voltage
from elco.core.places import State



class StationFactory(factory.DjangoModelFactory):
    code = 'TS-0X'
    name = 'Station 0X'
    type = Station.TRANSMISSION
    is_dedicated = False
    voltage_ratio = Voltage.Ratio.HVOLTL_2_MVOLTH
    address_line1 = 'Address Line #1'
    city = 'City'
    state = State.KANO
    source_feeder = None
    date_commissioned = datetime.today() 
    
    class Meta:
        model = Station


class PowerLineFactory(factory.DjangoModelFactory):
    code = 'FX0XX'
    name = 'Power Line'
    type = PowerLine.FEEDER
    voltage = Voltage.MVOLT_H
    is_dedicated = False
    source_station = factory.SubFactory(StationFactory)
    date_commissioned = datetime.today()
    
    class Meta:
        model = PowerLine

