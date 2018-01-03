from django.core.management.base import BaseCommand
from ...services import data_recorder
from ...utils import cmd

class Command(BaseCommand):
    help = 'Starts data recording for all allowed MQTT topics'

    def add_arguments(self, parser):
        parser.add_argument('--host', required=True, help='Broker IP address or hostname')

    def handle(self, *_, **options):
        cmd.run('MQTT data recorder',
                data_recorder.init_data_recorder,
                data_recorder.stop_data_recorder,
                data_recorder.loop_data_recorder,
                options['host']
        )
