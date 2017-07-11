import os
from django.core.management.base import BaseCommand
from ...utils import openssl


class Command(BaseCommand):
    help = 'Create the SSL certificates for Client'

    def add_arguments(self, parser):
        parser.add_argument('dir_prefix', help='Output directory path-prefix')
        parser.add_argument('hostname', help='Client host name')

    def handle(self, *args, **options):
        openssl.gen_client(os.path.abspath(options['dir_prefix']), options['hostname'])
