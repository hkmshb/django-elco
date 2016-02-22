from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse

from .forms import StationForm
from .models import Station, PowerLine
from .constants import Voltage



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


