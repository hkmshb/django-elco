# TemplateResponse used instead of render in order to allow access to context
# object in unit tests not using django test client

from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q

from .forms import StationForm
from .models import Station



def station_list(request, type_name, template='elco/station/list.html'):
    type_id = Station.get_type_id(type_name)
    qf = Q(type=type_id)
    records = Station.objects.filter(qf)
    
    return TemplateResponse(request,
        template, {
        'station_type_name': type_name,
        'records': records,
    })


def station_manage(request, type_name, station_id=None,
                   template='elco/station/form.html'):
    type_id = Station.get_type_id(type_name)
    qf = Q(type=type_id)
    
    station = Station()
    if station_id:
        station = get_object_or_404(Station, qf & Q(pk=station_id))
    
    if request.method == 'POST':
        # place station type value in POST data otherwise validation fails
        data = request.POST.copy()
        data['type'] = type_id
        
        form = StationForm(data=data, instance=station)
        if form.is_valid():
            form.save()
            
            message = _("The station has been added.")
            if station_id:
                message = _("The station has been updated.")
            messages.success(request, message)
            
            target_url_name = 'station-display'
            if '_save_addnew' in request.POST:
                target_url_name = 'station-create'
            return redirect(reverse(target_url_name, args=[type_name])) 
    else:
        data = {'type': type_id}
        form = StationForm(instance=station, initial=data)
    
    return TemplateResponse(request,
        template, {
        'station_type_name': type_name,
        'form': form,  
    })


def station_display(request, type_name, station_id, asset_type_name=None):
    pass
