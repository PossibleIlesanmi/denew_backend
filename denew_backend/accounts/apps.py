from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'denew_backend.accounts'
    
    def ready(self):
        """Import signals when the app is ready"""
        import denew_backend.accounts.signals