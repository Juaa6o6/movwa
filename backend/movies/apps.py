from django.apps import AppConfig

class MoviesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'movies'  # 기존 설정 유지 (settings.py의 INSTALLED_APPS에 적힌 이름과 같아야 함)

    def ready(self):
        import movies.signals