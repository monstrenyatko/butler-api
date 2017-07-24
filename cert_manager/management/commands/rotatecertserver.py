import os
from django.conf import settings
from django.core.management.base import BaseCommand
from ...utils import openssl


class Command(BaseCommand):
    help = 'Rotate the SSL certificates for Server'

    def add_arguments(self, parser):
        parser.add_argument('--path', '-p', help='Certificates directory path-prefix', default=settings.APP_DATA_CERT_DIR)

    def handle(self, *args, **options):
        openssl.rotate_server(os.path.abspath(options['path']))
