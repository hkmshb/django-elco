from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse

from .forms import StationForm, PowerLineForm
from .models import Station, PowerLine
from .constants import Voltage
from _testcapi import the_number_three



def manage_station(request, category=None,
                   powerline_id=None,
                   station_id=None,
                   template_name='elco/station_form.html',
                   model_form = StationForm,
                   redirect_url=None,
                   extra_context=None):
    """Use to create new and modify existion Station objects. 
    
    NOTE: The fields category and powerline_id are mutually exclusive with
    the later selected over the former if both are provided.
    """
    station = Station()
    source_feeder = None
    post_extra = {}
    
    if not station_id:
        if powerline_id:
            # constraint some other fields based no provided source feeder
            # here a station is being managed in relation to a feeder...
            source_feeder = get_object_or_404(PowerLine, pk=powerline_id)
            station.source_feeder = source_feeder
            
            post_extra['source_feeder'] = source_feeder.code
            if source_feeder.voltage == Voltage.MVOLTL:
                station.voltage_ratio = Voltage.Ratio.MVOLTL_LVOLT
                station.category = category = Station.DISTRIBUTION
                post_extra.update({
                    'voltage_ratio': station.voltage_ratio,
                    'category': station.category,
                })
        elif category:
            category = category.strip().title()
            if len(category) == 1:
                station.category = category
            else:
                category = Station.get_category_value(category)
                station.category = category
            post_extra['category'] = category
    else:
        station = get_object_or_404(Station, pk=station_id)
    
    # ensure a redirect can be performed
    if not redirect_url:
        redirect_url = reverse('list_stations')
    else:
        redirect_url = resolve_url(redirect_url)
    
    if request.method == 'POST':
        post_dict = request.POST.copy()
        post_dict.update(post_extra)
        
        form = model_form(category, source_feeder, instance=station, 
                          data=post_dict)
        if form.is_valid():
            form.save()
            return redirect(redirect_url)
    else:
        form = model_form(category, source_feeder, instance=station)
    
    context = {'form': form}
    if extra_context:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context)


def manage_powerline(request, line_type=None,
                     station_id=None,
                     powerline_id=None,
                     template_name='elco/powerline_form.html',
                     model_form=PowerLineForm,
                     redirect_url=None,
                     extra_context=None):
    """Use to create new and modify existing PowerLine objects.
    
    NOTE: The fields line_type and station_id are mutually exclusive with the
    later selected over the former if both are provided.
    """
    powerline = PowerLine()
    source_station = None
    post_extra = {}
    
    if not powerline_id:
        if station_id:
            # constraint some other fields based on provided source station
            # here a powerline is being managed in relation to a station...
            source_station = get_object_or_404(Station, pk=station_id)
            powerline.source_station = source_station
            post_extra['source_station'] = source_station.code
            
            voltage = Voltage.Ratio.get_lo_volt(source_station.voltage_ratio)
            powerline.voltage = voltage
            post_extra['voltage'] = voltage
            
            line_type = (PowerLine.UPRISER
                if voltage == Voltage.LVOLT
                else PowerLine.FEEDER)
            powerline.type = line_type
            post_extra['type'] = line_type
        elif line_type:
            line_type = line_type.strip().title()
            if len(line_type) == 1:
                powerline.type = line_type
            else:
                line_type = PowerLine.get_type_value(line_type)
                powerline.line_type = line_type
            post_extra['type'] = line_type
    else:
        powerline = get_object_or_404(PowerLine, pk=powerline_id)
    
    # ensure a redirect can be performed
    if not redirect_url:
        redirect_url = reverse('list_powerlines')
    else:
        redirect_url = resolve_url(redirect_url)
    
    if request.method == 'POST':
        post_dict = request.POST.copy()
        post_dict.update(post_extra)
        
        form = model_form(line_type, source_station, instance=powerline,
                          data=post_dict)
        if form.is_valid():
            form.save()
            return redirect(redirect_url)
    else:
        form = model_form(line_type, source_station, instance=powerline)
        
    context = {'form': form}
    if extra_context:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context)


