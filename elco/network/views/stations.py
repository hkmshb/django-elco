# TemplateResponse used instead of render in order to allow access to context
# object in unit tests not using django test client

from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q

from ..forms import StationForm, PowerLineForm, TransformerForm
from ..models import Station, PowerLine, Transformer
from . import manage_object_deletion




# string constants
MSG_FMT_WARN_DELETE = (
    'Some of the selected %s were deleted successfully. '
    'However %s of the selection could not be deleted.')


def station_list(request, type_name, template='elco/station/list.html'):
    type_id = Station.get_type_id(type_name)
    qf = Q(type=type_id)
    records = Station.objects.filter(qf)
    
    return TemplateResponse(request,
        template, {
        'station_type_name': type_name,
        'station_type_id': type_id,
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
            messages.success(request, message, extra_tags='success')
            
            if '_save_addnew' in request.POST:
                target_url_name = 'station-create'
                return redirect(reverse(target_url_name, args=[type_name]))
            
            target_url_name = 'station-detail'
            args=[type_name, form.instance.id]
            return redirect(reverse(target_url_name, args=args))
    else:
        data = {'type': type_id}
        form = StationForm(instance=station, initial=data)
    
    return TemplateResponse(request,
        template, {
        'station_type_name': type_name,
        'station_type_id': type_id,
        'form': form,  
    })


def station_display(request, type_name, station_id,
                    asset_type_name='transformers',
                    template='elco/station/detail.html'):
    type_id = Station.get_type_id(type_name)
    qf = Q(pk=station_id) & Q(type=type_id)
    
    station = get_object_or_404(Station, qf)
    asset_class, qf2 = None, None
    if Station.is_feeder_asset_label(asset_type_name):
        asset_class = PowerLine
        qf2 = (Q(source_station__id=station_id)
             & Q(source_station__type=type_id))
    else:
        asset_class = Transformer
        qf2 = (Q(station__id=station_id) & Q(station__type=type_id))
    
    asset_list = asset_class.objects.filter(qf2)
    return TemplateResponse(request,
        template, {
        'form': StationForm(instance=station),
        'station': station,
        'station_type_name': type_name,
        'station_type_id': type_id,
        'asset_type_name': asset_type_name,
        'asset_list': asset_list,
    })


def station_delete(request, type_name, station_id=None):
    return manage_object_deletion(request, ids=station_id,
        model_name='stations',
        model=Station, 
        return_url=reverse('station-list', args=[type_name])
    )


def station_asset_manage(request, type_name, station_id,
                         asset_type_name='transformers', asset_id=None,
                         template='elco/station/asset-form.html'):
    # ensure station exists
    type_id = Station.get_type_id(type_name)
    qf = Q(pk=station_id) & Q(type=type_id)
    station = get_object_or_404(Station, qf)
    
    # prepare for asset creation
    asset_class, asset_form = (Transformer, TransformerForm)
    if Station.is_feeder_asset_label(asset_type_name):
        asset_class, asset_form = (PowerLine, PowerLineForm)
    
    asset = asset_class()
    if asset_id:
        asset = get_object_or_404(asset_class, pk=asset_id)
    
    if request.method == 'POST':
        form = asset_form(data=request.POST, instance=asset)
        if form.is_valid():
            form.save()
            
            msg_fmt = "The %s has been " % asset_type_name[:-1]
            message = _(msg_fmt + "created.")
            if asset_id:
                message = _(msg_fmt + "updated.")
            messages.success(request, message)
            
            next_url = request.POST.get('next', None)
            return_url = request.META.get('HTTP_REFERER', next_url)
            args = [type_name, station_id, asset_type_name]
            return redirect(reverse('station-asset-list', args=args) or return_url)
    else:
        form = asset_form(instance=asset)
    return TemplateResponse(request,
        template, {
        'asset_type_name': asset_type_name,
        'form': form,
    })

