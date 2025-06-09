
from django.apps import AppConfig

class PricingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pricing'  # should match your app name

    def ready(self):
        # Import sigals only after the app is ready
        import pricing.signals