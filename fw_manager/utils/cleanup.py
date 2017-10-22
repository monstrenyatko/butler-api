import os
from datetime import datetime
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from .. import models as local_models


def get_unused_fw_files():
    # get files
    media_files = []
    for root, _, files in os.walk(os.path.join(settings.APP_DATA_FW_ROOT, settings.APP_DATA_FW_SUBDIR)):
        for name in files:
            file_path = os.path.join(root, name)
            media_files.append(os.path.relpath(file_path, settings.APP_DATA_FW_ROOT))
    # get files referenced by DB
    db_files = local_models.FirmwareModel.objects.exclude(
        Q(file__isnull=True) | Q(file__exact='')
    ).values_list('file', flat=True).distinct()
    # return files which are no longer referenced by DB
    return [os.path.join(settings.APP_DATA_FW_ROOT, x) for x in media_files if x not in db_files]

def remove_unused_fw_files(files):
    now = timezone.now()
    for file in files:
        # delete files older than...
        file_ts = timezone.make_aware(datetime.fromtimestamp(os.path.getmtime(file)))
        if file_ts < now - settings.APP_DATA_FW_UNUSED_DELAY:
            os.remove(file)
