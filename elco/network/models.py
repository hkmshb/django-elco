from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from ..core.places import State
from .constants import Voltage, Condition
from .validators import validate_transformer_rating_code_format, \
        validate_transformer_rating_code



class AbstractBaseModel(models.Model):
    """
    An abstract base model that provides an `is_active` field and other fields 
    for tracking dates of creation and last update for a database entity.
    """
    is_active = models.BooleanField(_("Active"), default=True, db_index=True)
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)
    last_updated = models.DateTimeField(_("Last Updated"), auto_now=True,
                                        null=True)
    
    class Meta:
        abstract = True


class Station(AbstractBaseModel):
    """
    Represents a power station within an electricity distribution power network.
    """
    TRANSMISSION = 'T'
    INJECTION    = 'I'
    DISTRIBUTION = 'D'
    
    TYPE_NAME_ID_MAP = {
        'transmissions': TRANSMISSION,
        'injections':    INJECTION,
        'distributions': DISTRIBUTION,
    }
    
    STATION_CHOICES = (
        (TRANSMISSION, 'Transmission'),
        (INJECTION,    'Injection'),
        (DISTRIBUTION, 'Distribution'),
    )
    
    code = models.CharField(_("Code"), max_length=10, unique=True)
    name = models.CharField(_("Name"), max_length=100)
    type = models.CharField(_("Type"), max_length=1, choices=STATION_CHOICES)
    is_dedicated = models.BooleanField(_("Dedicated"), default=False)
    voltage_ratio = models.PositiveSmallIntegerField(
        _("Voltage Ratio"), choices=Voltage.Ratio.ALL_CHOICES)
    address_line1 = models.CharField(
        _("Address Line #1"), max_length=50)
    address_line2 = models.CharField(
        _("Address Line #2"), max_length=50, blank=True)
    city = models.CharField(_("City"), max_length=25)
    state = models.CharField(
        _("State"), max_length=2, choices=State.ALL_CHOICES)
    source_feeder = models.ForeignKey(
        'PowerLine', null=True, default=None, blank=True,
        verbose_name=_("Source Feeder"), on_delete=models.PROTECT)
    date_commissioned = models.DateField(
        _("Date Commissioned"), null=True, blank=True)
    notes = models.TextField(_("Notes"), blank=True)
    
    def __str__(self):
        return '%s %s' % (self.code, self.name)
    
    @property
    def address(self):
        fields = [self.address_line1, self.address_line2, self.city]
        fields = [f.strip() for f in fields if f]
        fields.append(self.get_state_display())
        return u", ".join(fields)
    
    def clean(self):
        pass
    
    def get_absolute_url(self):
        return reverse('station-detail', args=[self.type_name, self.id])
    
    def get_asset_list_url(self, asset_label):
        return reverse('station-detail',
            args=[self.type_name, self.id, asset_label])
    
    def get_feeder_list_url(self):
        return reverse('station-detail',
            args=[self.type_name, self.id, 'feeders'])
    
    def get_transformer_list_url(self):
        return reverse('station-detail',
            args=[self.type_name, self.id, 'transformers'])
    
    @staticmethod
    def get_type_name(type_id):
        for name, id in Station.TYPE_NAME_ID_MAP.items():
            if type_id == id:
                return name
        raise ValueError(_("Unknown station type id: %s") % type_id)
    
    @staticmethod
    def get_type_id(type_name):
        if type_name not in Station.TYPE_NAME_ID_MAP:
            raise ValueError(_("Unknown station type name: %s") % type_name)
        return Station.TYPE_NAME_ID_MAP[type_name]
    
    @staticmethod
    def is_feeder_asset_label(type_name):
        return type_name == 'feeders'
    
    @staticmethod
    def get_feeder_asset_label():
        return 'feeders'
    
    @staticmethod
    def asset_labels():
        return [
            "transformers",
            "feeders",
        ]


class PowerLine(AbstractBaseModel):
    """
    Represents a power line within an electricity distribution power network.
    """
    FEEDER  = 'F' 
    UPRISER = 'U'
    
    POWERLINE_CHOICES = (
        (FEEDER,  'Feeder'),
        (UPRISER, 'Upriser')
    )
    
    # acceptable voltage levels
    MVOLT_H = Voltage.MVOLT_H
    MVOLT_L = Voltage.MVOLT_L
    LVOLT   = Voltage.LVOLT
    
    VOLTAGE_CHOICES = (
        (MVOLT_H, '33KV'),
        (MVOLT_L, '11KV'),
        (LVOLT,   '0.415KV'),
    )
    
    code = models.CharField(_("Code"), max_length=10, unique=True)
    name = models.CharField(_("Name"), max_length=100)
    type = models.CharField(_("Type"), max_length=1, 
                choices=POWERLINE_CHOICES)
    voltage = models.PositiveSmallIntegerField(
        _("Voltage"), choices=VOLTAGE_CHOICES)
    is_dedicated = models.BooleanField(_("Dedicated"), default=False)
    source_station = models.ForeignKey(
        'Station', to_field='code', 
        verbose_name=_("Source Station"), on_delete=models.PROTECT)
    date_commissioned = models.DateField(
        _("Date Commissioned"), null=True, blank=True)
    notes = models.TextField(_("Notes"), blank=True)
    
    def __str__(self):
        return "%s %s" % (self.name, self.get_voltage_display())
    
    class Meta:
        unique_together = ('name', 'voltage')


class TransformerRating(AbstractBaseModel):
    """
    Represents a transformer power rating. Capacity value is expected to be in
    KVA thus 6MVA should be provided as 6000KVA. 
    
    A transformer rating codes ins't an arbitrary code, its actually an encoding
    of a transformers capacity and voltage ratio values put into 5 characters.
    Thus given just a transformer rating code, it should be possible to tell the
    actual capacity and voltage ratio values. Furthermore the code captures an
    extra detail of the transformer, to tell if its a power transformer or just
    a distribution transformer. 
    
    The code format expressed using regex is as thus:
      -> (P|D)(3|1)dd(d|[Mm])
      
      where:
          P: signifies Power transformer
          D: signifies Distribution transformer
          3: the last L-side voltage ratio digit if P (132/33KV) or the last
             H-side digit if D (33/0.415KV)
          1: the last L-side voltage ratio digit if P (132/11KV) or (33/11KV)
             or the last H-side digit if D (11/0.415KV)
          d: a single digit, 0-9
          M: signifies a multiplier of 10^6
          m: signifies a multiplier of 10^5 (fractional multiplier)
    
    Rules:
      1. Code must begin with a P or D else its invalid
      2. Code must be 5 characters long with or without the multiplier
      3. The default multiplier for P-starting codes is M if its not provided
         and for D-starting codes its K (10^3) though this is never indicated.
      4. Code for power transformers MUST carry multiplier whenever possible.
      5. The standard multipliers of M and m can also be applied for K-starting
         codes.
      6. Dots are not permitted in code; the fractional multiplier MUST be used
         in code for capacities that would normally be written using fraction
         for the standard units of MVA or KVA.
      7. D-starting codes must be expressed in its most natural form where it
         ends with the K multiplier, the M or m should only be used where it
         qualifies for capacity is in the Mega range.
    
    Examples:
         Capacity       Expressed As
      1. 60MVA     ->   60M   or   060
      2. 6MVA      ->   06M   or   006
      3. 7.5MVA    ->   75m
      4. 500KVA    ->   500
      5. 50KVA     ->   050
      6. 25KVA     ->   025
      7. 1000KVA   ->   01M
      8. 1500KVA   ->   15m
    """
    code = models.CharField(
        _("Code"), max_length=5, unique=True,
        validators=[validate_transformer_rating_code_format])
    capacity = models.PositiveIntegerField(_("Capacity"))
    voltage_ratio = models.PositiveSmallIntegerField(
        _("Voltage Ratio"), choices=Voltage.Ratio.ALL_CHOICES)
    notes = models.TextField(_("Notes"), blank=True)
    
    def __str__(self):
        return '%s, %s' % (self.capacity, self.get_voltage_ratio_display())
    
    class Meta:
        unique_together = ('capacity', 'voltage_ratio')
    
    def clean(self):
        # ensure coded rating & capacity match actual values
        validate_transformer_rating_code(
            self.code, 
            self.capacity, 
            self.voltage_ratio)


class EquipmentBase(AbstractBaseModel):
    """
    Represents the abstract base class for equipments.
    """
    serialno = models.CharField(
        _("Serial #"), max_length=50, blank=True, unique=True)
    model = models.CharField(
        _("Model"), max_length=100, blank=True)
    manufacturer = models.CharField(
        _("Manufacturer"), max_length=100, blank=True)
    condition = models.PositiveSmallIntegerField(
        _("Condition"), choices=Condition.CHOICES)
    station = models.ForeignKey(
        Station, to_field='code',
        verbose_name=_("Station"), on_delete=models.PROTECT)
    date_installed = models.DateField(
        _("Date Installed"), null=True, blank=True)
    date_manufactured = models.DateField(
        _("Date Manufactured"), null=True, blank=True)
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        abstract = True


class Transformer(EquipmentBase):
    """
    Represents all classes (power, distribution) of transformers within an
    electricity distribution network.
    """
    rating = models.ForeignKey(
        TransformerRating, to_field='code',
        verbose_name=_("Rating"), on_delete=models.PROTECT)

