# readingcv/apps.py
from django.apps import AppConfig

class ReadingcvConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'readingcv'

    def ready(self):
        import readingcv.signals  # important : charger les signaux
