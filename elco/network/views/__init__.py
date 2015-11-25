from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.contrib import messages



# string constants
MSG_FMT_SUCCESS_DELETE = 'Selected %s delete successfully.'
MSG_FMT_ERROR_DELETE = 'None of the selected %s were deleted.'
MSG_FMT_WARN_DELETE = (
    'Some of the selected %s were deleted successfully. '
    'However %s of the selection could not be deleted.')


def manage_object_deletion(request, model, model_name, return_url, ids):
    target_ids = list(ids or request.POST.getlist('record_ids'))
    if request.method == 'POST' and target_ids:
        try:
            failed_ids = []
            for item_id in target_ids:
                try:
                    item = model.objects.get(pk=item_id)
                    item.delete()
                except ObjectDoesNotExist:
                    failed_ids.append(item_id)
            
            target_count = len(target_ids)
            failed_count = len(failed_ids)
            messages.add_message(request,
                level=(messages.SUCCESS if failed_count == 0 else messages.WARNING
                    if failed_count < target_count else messages.ERROR),
                message=(MSG_FMT_SUCCESS_DELETE % model_name
                    if failed_count == 0 else
                        MSG_FMT_WARN_DELETE % (model_name, target_count - failed_count)
                            if failed_count < target_count else
                                MSG_FMT_ERROR_DELETE % model_name),
                extra_tags=('success' if failed_count == 0 else 'warning'
                    if failed_count < target_count else 'danger')
            )
        except Exception as ex:
            messages.error(request, str(ex), extra_tags='danger')
            raise ex
    return redirect(return_url)

