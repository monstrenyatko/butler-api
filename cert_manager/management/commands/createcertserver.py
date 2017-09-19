import os
from django.conf import settings
from django.core.management.base import BaseCommand
from ...utils import openssl


class Command(BaseCommand):
    help = 'Create the SSL certificates for Server'

    def add_arguments(self, parser):
        parser.add_argument('--path', '-p', help='Certificates directory path-prefix', default=settings.APP_DATA_CERT_DIR)
        parser.add_argument('--name', help='Server host name')

    def handle(self, *args, **options):
        if options['name']:
            openssl.gen_server(os.path.abspath(options['path']), options['name'])
        else:
            openssl.gen_server(os.path.abspath(options['path']))
