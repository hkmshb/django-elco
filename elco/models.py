from django.db import models
from django.utils.translation import ugettext_lazy as _
from address.models import AddressField

from .constants import Condition, Voltage



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
    address = AddressField(_("Address"), null=True, blank=True)
    date_commissioned = models.DateField(
        _("Date Commissioned"), null=True, blank=True)
    
    def __str__(self):
        return "%s %s" % (self.name, self.get_voltge_ratio_display())


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
    
    code = models.CharField(_("Code"), max_length=10, unique=True)
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


