import os
from django.apps import AppConfig


class MonitorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitors'

    def ready(self):
        # Guard against the scheduler starting twice when Django's autoreloader is active
        if os.environ.get('RUN_MAIN') == 'true':
            from .scheduler import start
            start()
