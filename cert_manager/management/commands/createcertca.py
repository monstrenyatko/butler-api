import os
from django.core.management.base import BaseCommand
from ...utils import openssl


class Command(BaseCommand):
    help = 'Create the SSL CA'

    def add_arguments(self, parser):
        parser.add_argument('dir_prefix', help='Output directory path-prefix')

    def handle(self, *args, **options):
        openssl.gen_ca(os.path.abspath(options['dir_prefix']))
