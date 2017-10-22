from django.core.management.base import BaseCommand
from ...utils import cleanup


class Command(BaseCommand):
    help = 'Delete FW files which are no longer referenced by DB'

    def handle(self, *_, **__):
        files = cleanup.get_unused_fw_files()
        cleanup.remove_unused_fw_files(files)
