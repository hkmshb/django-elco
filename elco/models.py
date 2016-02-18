from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from address.models import AddressField

from .constants import Condition, Voltage
from .validators import validate_powerline_code_format


# message constants
MSG_TSTATION_SOURCE_FEEDER_NOT_SUPPORTED = _(
    "Source feeder for Transmission Station not supported.")
MSG_XSTATION_INPUT_MISMATCH_FEEDER = _(
    "Source feeder voltage mismatch Station input voltage for voltage ratio")




class AbstractBaseModel(models.Model):
    """An abstract base model that provides an `is_active` field and other fields
    for tracking dates of creation and last update for a databas entity.
    """
    is_active = models.BooleanField(_("Active"), default=True, db_index=True)
    date_created = models.DateTimeField(_("Date Created"), auto_now_add=True)
    last_updated = models.DateTimeField(_("Last Updated"), auto_now=True, null=True)
    notes = models.TextField(_("Notes"), blank=True)
    
    class Meta:
        abstract = True


class Station(AbstractBaseModel):
    """Represents a power station within an electric distribution power network."""
    TRANSMISSION = 'T'
    INJECTION    = 'I'
    DISTRIBUTION = 'D'
    
    STATION_CHOICES = (
        (TRANSMISSION, 'Transmission'),
        (INJECTION,    'Injection'),
        (DISTRIBUTION, 'Distribution'),
    )
    
    code = models.CharField(_("Code"), max_length=10, unique=True)
    name = models.CharField(_("Name"), max_length=100)
    category = models.CharField(_("Category"), max_length=1, 
                                choices=STATION_CHOICES)
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
        self._validate_code_format()
        self._validate_source_feeder()
    
    def _validate_code_format(self):
        err_message = _("Invalid station code format")
        if not self.code or len(self.code) not in (4, 6):
            raise ValidationError(err_message)
        
        code_start_char = self.get_category_display()[0]
        if code_start_char == 'D':
            code_start_char = 'S'
        
        if self.code[0] != code_start_char or self.code[1] not in ('1','3'):
            raise ValidationError(err_message)
        
        # ensure code carries right voltage ratio embedded
        expected_embedded_code = self.get_voltage_ratio_display()[0]
        if self.code[1] != expected_embedded_code:
            raise ValidationError(err_message)
        
        hex_code = self.code[2:]
        expected_hex_length = (4 if code_start_char == 'S' else 2)
        if len(hex_code) != expected_hex_length:
            raise ValidationError(err_message)
        
        try:
            int(hex_code, 16)
            return
        except:
            pass
        raise ValidationError(err_message)
    
    def _validate_voltage_ratio(self):
        message_fmt = "Invalid voltage ratio provided for %s Station."
        category, voltage_ratio = self.category, self.voltage_ratio
        
        expected_choices = (Voltage.Ratio.TRANSMISSION_CHOICES
            if category == Station.TRANSMISSION
            else Voltage.Ratio.INJECTION_CHOICES
                if category == Station.INJECTION
                else Voltage.Ratio.DISTRIBUTION_CHOICES
        )
        
        expected_ratios = [x[0] for x in expected_choices]
        if voltage_ratio not in expected_ratios:
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
    
