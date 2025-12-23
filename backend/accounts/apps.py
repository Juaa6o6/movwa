from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    
    def ready(self):
        """앱이 준비되면 실행되는 메서드"""
        import accounts.signals  # 시그널 등록!