# TemplateResponse used instead of render in order to allow access to context
# object in unit tests not using django test client

from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.db.models import Q

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

