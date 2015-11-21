from elco.core.registry import register



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

