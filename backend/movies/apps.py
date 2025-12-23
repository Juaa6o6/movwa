from django.apps import AppConfig

class MoviesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'movies'  # 기존 설정 유지 (settings.py의 INSTALLED_APPS에 적힌 이름과 같아야 함)

    def ready(self):
        # 여기서는 경로를 정확히 찾아가야 하므로 backend.movies.signals가 맞습니다.
        try:
            import backend.movies.signals
        except ImportError:
            # 혹시 경로 에러가 나면 movies.signals로 시도
            import movies.signals