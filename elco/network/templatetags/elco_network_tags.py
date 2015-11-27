from elco.core.registry import register
from ..models import TransformerRating, Station, PowerLine, Transformer



@register.assignment_tag
def get_rating_xfmr_table_fields_with_model():
    fields = ['code', 'capacity', 'voltage_ratio']
    return (fields, TransformerRating)


@register.filter
def is_active_station_asset_label(label, request_path):
    path_chunks = [p for p in request_path.split('/') if p]
    if len(path_chunks) >= 5:
        return path_chunks[4] == label
    return label in ('', 'transformers')


@register.filter
def make_station_asset_action_url(request_path, action):
    path_chunks = [p for p in request_path.split('/') if p]
    if len(path_chunks) >= 5:
        path_chunks.append(action)
    else:
        path_chunks.extend(["transformers", action])
    return "/%s" % "/".join(path_chunks)


@register.filter
def make_station_asset_list_url(request_path, label):
    path_chunks = [p for p in request_path.split('/') if p]
    if len(path_chunks) == 4:
        path_chunks.append(label)
    elif len(path_chunks) == 5:
        if not request_path.endswith(label + '/'):
            path_chunks[4] = label
    return "/%s/" % "/".join(path_chunks)


@register.assignment_tag
def get_station_table_fields_with_model(station_type_id):
    fields = ['code', 'name', 'voltage_ratio','is_dedicated', 'city', 'state']
    if station_type_id in (Station.INJECTION, Station.DISTRIBUTION):
        fields.append('source_feeder')
    return (fields, Station)


@register.assignment_tag
def get_station_asset_table_fields_with_model(station, asset_label):
    model = Transformer
    fields = ['rating', 'serialno', 'condition','date_installed']
    if station.is_feeder_asset_label(asset_label):
        model = PowerLine
        fields = ['code', 'name', 'voltage', 'is_dedicated', 'date_commissioned']
    return (fields, model)