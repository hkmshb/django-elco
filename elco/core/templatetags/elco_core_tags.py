from ..registry import register
from collections import OrderedDict
from django.forms.widgets import Textarea



@register.filter
def field_verbose_name(model, field_name):
    field = model._meta.get_field_by_name(field_name)[0]
    try:
        return field.verbose_name.title()
    except:
        return field.name.replace('_','').title()


@register.filter
def field_value(record, field_name):
    try:
        try:
            field = record._meta.get_field_by_name(field_name)[0]
            if field.choices:
                return  getattr(record, 'get_%s_display' % field_name)()
        except:
            pass
        return getattr(record, field_name)
    except:
        return ''


@register.filter
def lookup(dict_, key):
    if key in dict_:
        return dict_[key]
    return ''


@register.filter
def make_chunks_of(list_, item_count=1):
    items =  list_.copy()
    if item_count > 1:
        item_chunks = []
        
        while items:
            chunk = items[:item_count]
            del items[:item_count]
            
            item_chunks.append(chunk)
        items = item_chunks
    return items


@register.filter
def make_fields_name_chunks_of(fields, item_count=1):
    field_names = [name for name in fields.keys()]
    if item_count > 1:
        name_chunks, textareas = [], []
        
        while field_names:
            chunk = field_names[:item_count]
            del field_names[:item_count]
            
            tmp = []
            for name in chunk:
                if type(fields[name].field.widget) is Textarea:
                    textareas.append([name])
                else:
                    tmp.append(name)
            name_chunks.append(tmp)
        
        if textareas:
            name_chunks.extend(textareas)
        field_names = name_chunks
    return field_names


@register.filter
def visible_fields(form):
    fields = OrderedDict()
    for field in form.visible_fields():
        fields[field.name] = field
    return fields

