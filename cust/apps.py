from django.apps import AppConfig


class CustConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cust'
    
    def ready(self):
        from . import signals