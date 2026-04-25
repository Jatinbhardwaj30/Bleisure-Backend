from django.apps import AppConfig


class BleisureConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bleisure'
    
    def ready(self):
        """
        Import signal handlers when the app is ready.
        """
        import bleisure.signals
