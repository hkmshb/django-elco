from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from address.models import AddressField

from .constants import Condition, Voltage
from .validators import validate_powerline_code_format,\
        validate_station_code_format, validate_transformer_rating_code,\
        validate_transformer_rating_code_format, MSG_INVALID_FORMAT


# message constants
MSG_TSTATION_SOURCE_FEEDER_NOT_SUPPORTED = _(
    "Source feeder for Transmission Station not supported.")
MSG_XSTATION_INPUT_MISMATCH_FEEDER = _(
    "Source feeder voltage mismatch Station input voltage for voltage ratio.")
MSG_XSTATION_CODE_MISMATCH_VOLTAGE_RATIO = _(
    "There is a mismatch between provided code and voltage ratio.")
MSG_FMT_INVALID_VOLTAGE_RATIO = \
    "Invalid voltage ratio provided for %s station category."



class AbstractBaseModel(models.Model):
    """An abstract base model that provides an `is_active` field and other fields
    for tracking dates of creation and last update for a databas entity.
    """
    is_active = models.BooleanField(_("Active"), default=True, db_index=True)
    date_created = models.DateField(_("Date Created"), auto_now_add=True)
    last_updated = models.DateField(_("Last Updated"), auto_now=True, null=True)
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        abstract = True


class Station(AbstractBaseModel):
    """Represents a power station within an electric distribution power network."""
    TRANSMISSION = 'T'
    INJECTION    = 'I'
    DISTRIBUTION = 'D'
    
    CATEGORY_CHOICES = (
        (TRANSMISSION, 'Transmission'),
        (INJECTION,    'Injection'),
        (DISTRIBUTION, 'Distribution'),
    )
    
    code = models.CharField(_("Code"), max_length=10, unique=True,
                validators=[validate_station_code_format])
    alt_code = models.CharField(_("Alternate Code"), max_length=10, blank=True)
    name = models.CharField(_("Name"), max_length=100)
    category = models.CharField(_("Category"), max_length=1, 
                                choices=CATEGORY_CHOICES)
    public = models.BooleanField(_("Public"), default=True)
    voltage_ratio = models.PositiveSmallIntegerField(
        _("Voltage Ratio"), choices=Voltage.Ratio.CHOICES)
    source_feeder = models.ForeignKey(
        'PowerLine', verbose_name=_("Source Feeder"),
        null=True, blank=True, default=None)
    address = AddressField(
        verbose_name=_("Address"), null=True, blank=True)
    date_commissioned = models.DateField(
        _("Date Commissioned"), null=True, blank=True)
    
    class Meta:
        unique_together = ('name', 'category')
    
    def __str__(self):
        return "%s %s" % (self.name, self.get_voltage_ratio_display())
    
    def clean(self):
        # ensure valid voltage assigned based on category
        self._validate_voltage_ratio()
        self._validate_source_feeder()
        self._validate_code()
    
    def _validate_code(self):
        """Code format has been validated by field validator. Validation here
        ensures portions of the code match station characteristics.
        """
        # ensure fields required to perform validation are present
        if not self.code or not self.category or not self.voltage_ratio:
            return
        
        # ensure start_char matches category
        start_char = self.get_category_display()[0]
        if start_char == 'D':
            start_char = 'S'
        
        if not self.code or self.code[0].upper() != start_char:
            raise ValidationError(MSG_INVALID_FORMAT)
        
        # ensure embedded voltage code matches voltage ratio
        voltage_code = self.get_voltage_ratio_display()[0]
        if self.code[1] != voltage_code:
            raise ValidationError(MSG_XSTATION_CODE_MISMATCH_VOLTAGE_RATIO)
    
    def _validate_voltage_ratio(self):
        message_fmt = MSG_FMT_INVALID_VOLTAGE_RATIO
        category, voltage_ratio = self.category, self.voltage_ratio
        
        # ensure fields required to perform validation are present
        if not voltage_ratio or not category:
            return
        
        expected_choices = (Voltage.Ratio.TRANSMISSION_CHOICES
            if category == Station.TRANSMISSION
            else Voltage.Ratio.INJECTION_CHOICES
                if category == Station.INJECTION
                else Voltage.Ratio.DISTRIBUTION_CHOICES
        )
        
        expected_ratios = [x[0] for x in expected_choices]
        if voltage_ratio and voltage_ratio not in expected_ratios:
            category_name = ("Transmission"
                if category == Station.TRANSMISSION
                else "Injection"
                    if category == Station.INJECTION
                    else "Distribution"
            )
            err_message = _(message_fmt % category_name)
            raise ValidationError(err_message)
    
    def _validate_source_feeder(self):
        if not self.source_feeder:
            return
        
        if self.category == Station.TRANSMISSION:
            raise ValidationError(MSG_TSTATION_SOURCE_FEEDER_NOT_SUPPORTED)
        
        # ok for Inj. and Dist. S/S with MVOLTH_LVOLT ratio
        expected_input_voltage = Voltage.MVOLTH
        if self.category == Station.DISTRIBUTION:
            if self.voltage_ratio == Voltage.Ratio.MVOLTL_LVOLT:
                expected_input_voltage = Voltage.MVOLTL
        
        if self.source_feeder.voltage != expected_input_voltage:
            raise ValidationError(MSG_XSTATION_INPUT_MISMATCH_FEEDER)


class PowerLine(AbstractBaseModel):
    """Represents a power line within an electric distribution power network."""
    FEEDER  = 'F'
    UPRISER = 'U'
    
    POWERLINE_CHOICES = (
        (FEEDER,  'Feeder'),
        (UPRISER, 'Upriser')
    )
    
    # acceptable voltage levels
    VOLTAGE_CHOICES = (
        (Voltage.MVOLTH, Voltage._text[Voltage.MVOLTH]),
        (Voltage.MVOLTL, Voltage._text[Voltage.MVOLTL]),
        (Voltage.LVOLT,  Voltage._text[Voltage.LVOLT]),
    )
    
    code = models.CharField(_("Code"), max_length=10, unique=True,
            validators=[validate_powerline_code_format])
    alt_code = models.CharField(_("Alternate Code"), max_length=10, blank=True)
    name = models.CharField(_("Name"), max_length=100)
    type = models.CharField(_("Type"), max_length=1,
                choices=POWERLINE_CHOICES)
    voltage = models.PositiveSmallIntegerField(
        _("Voltage"), choices=VOLTAGE_CHOICES)
    public = models.BooleanField(_("Public"), default=True)
    source_station = models.ForeignKey(
        'Station', to_field='code', verbose_name=_("Source Station"))
    date_commissioned = models.DateField(
        _("Date Commissioned"), null=True, blank=True)
    
    class Meta:
        unique_together = ('name', 'voltage')
    
    def __str__(self):
        return "%s %s" % (self.name, self.get_voltage_display())


class TransformerRating(AbstractBaseModel):
    """Represents a transformer power rating. Capacity value is expected to be 
    in KVA thus 6MVA should be provided as 6000KVA. 
    
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
    code = models.CharField(_("Code"), max_length=5, unique=True,
                validators=[validate_transformer_rating_code_format])
    capacity = models.PositiveIntegerField(_("Capacity"))
    voltage_ratio = models.PositiveSmallIntegerField(
        _("Voltage Ratio"), choices=Voltage.Ratio.CHOICES)
    
    def __str__(self):
        return "%s, %s" % (self.capacity, self.get_voltage_ratio_display())
    
    class Meta:
        unique_together = ('capacity', 'voltage_ratio')
    
    def clean(self):
        # ensure coded rating & capacity match actual values
        validate_transformer_rating_code(
            self.code, self.capacity, self.voltage_ratio)


class EquipmentBase(AbstractBaseModel):
    """Represents the abstract base class for equipments."""
    serialno = models.CharField(
        _("Serial #"), max_length=50, blank=True, unique=True)
    model = models.CharField(
        _("Model"), max_length=100, blank=True)
    manufacturer = models.CharField(
        _("Manufacturer"), max_length=100, blank=True)
    condition = models.PositiveSmallIntegerField(
        _("Condition"), choices=Condition.CHOICES)
    station = models.ForeignKey(
        Station, to_field='code', verbose_name=_("Station"))
    date_installed = models.DateField(
        _("Date Installed"), null=True, blank=True)
    date_manufactured = models.DateField(
        _("Date Manufactured"), null=True, blank=True)
    
    class Meta:
        abstract = True


class Transformer(EquipmentBase):
    """Represents all classes (power, distribution) of transformers within an
    electricity distribution network.
    """
    code = models.CharField(_("Code"), max_length=10)
    rating = models.ForeignKey(
        TransformerRating, to_field='code', verbose_name=_("Rating"))
    
    class Meta:
        unique_together = ('code', 'station')

