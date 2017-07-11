import os
from django.core.management.base import BaseCommand
from ...utils import openssl


class Command(BaseCommand):
    help = 'Rotate the SSL certificates for Server'

    def add_arguments(self, parser):
        parser.add_argument('dir_prefix', help='Certificates directory path-prefix')

    def handle(self, *args, **options):
        openssl.rotate_server(os.path.abspath(options['dir_prefix']))
