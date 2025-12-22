from django.contrib import admin
from .models import Genre, Movie, UserMovieLog, UserMovieRecommend

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    # 목록에서 보고 싶은 칼럼들
    list_display = ('title', 'release_date', 'popularity', 'vote_average', 'status')
    # 검색할 수 있는 칼럼
    search_fields = ('title', 'original_title', 'overview')
    # 필터링 옵션
    list_filter = ('status', 'release_date')

@admin.register(UserMovieLog)
class UserMovieLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'is_liked', 'is_saved', 'rating', 'updated_at')
    list_filter = ('is_liked', 'is_saved')
    search_fields = ('user__email', 'movie__title') # 유저 이메일, 영화 제목으로 검색 가능

@admin.register(UserMovieRecommend)
class UserMovieRecommendAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'score', 'rank', 'algo_type')
    list_filter = ('algo_type',)