from django.apps import AppConfig


class AuthManagerConfig(AppConfig):
    name = 'auth_manager'
    verbose_name = 'auth manager'

    def ready(self):
        from . import signals
