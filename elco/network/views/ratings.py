# TemplateResponse used instead of render in order to allow access to context
# object in unit tests not using django test client

from django.shortcuts import redirect, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db.models import Q

from ..forms import TransformerRatingForm
from ..models import TransformerRating
from . import manage_object_deletion


# transformer ratings list
def transformer_list(request, template='elco/rating/xfmr-list.html'):
    records = TransformerRating.objects.all()
    return TemplateResponse(request,
        template, {
        'records': records
    })


def transformer_manage(request, record_id=None, 
                       template='elco/rating/xfmr-form.html'):
    record = TransformerRating()
    if record_id:
        record = get_object_or_404(TransformerRating, pk=record_id)
    
    if request.method == 'POST':
        form = TransformerRatingForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            
            message = _("The transformer rating has been added.")
            if record_id:
                message = _("The transformer rating has been updated.")
            messages.success(request, message, extra_tags='success')
            
            if '_save_addnew' in request.POST:
                target_url_name = 'rating-transformer-create'
                return redirect(reverse(target_url_name))
            
            target_url_name = 'rating-transformer-detail'
            return redirect(reverse(target_url_name, args=[form.instance.id]))
    else:
        form = TransformerRatingForm(instance=record)
    return TemplateResponse(request,
        template, {
        'form': form, 
    })


def transformer_display(request, record_id=None,
                        template='elco/rating/xfmr-detail.html'):
    record = get_object_or_404(TransformerRating, pk=record_id)
    return TemplateResponse(request,
        template, {
        'form': TransformerRatingForm(instance=record),
        'record': record,
    })


def transformer_delete(request, record_id=None):
    return manage_object_deletion(request, ids=record_id, 
        model_name='transformer rating',
        model=TransformerRating, 
        return_url=reverse('rating-transformer-list')
    )