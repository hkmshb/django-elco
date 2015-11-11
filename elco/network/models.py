from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..core.places import State
from .constants import Voltage



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
        'PowerLine', null=True, default=None,
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

