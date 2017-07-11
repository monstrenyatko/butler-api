from django.apps import AppConfig


class AuthManagerConfig(AppConfig):
    name = 'auth_manager'

    def ready(self):
        from . import signals