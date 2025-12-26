from django.urls import path
from .views import (
    # 기존 조회 View
    MovieListView,
    MovieDetailView,
    MovieSearchView,
    
    # 상호작용(Action) View
    MovieLikeView,
    MovieSaveView,
    MovieRateView,
    UserMovieLogBulkView,
    
    # 마이페이지/목록 조회 View
    MySaveListView,
    MyRatedListView,
    MyRatedLogListView,
    TodaysPickListView,
    
    # 큐레이션 View
    BoxOfficeView,
    UpcomingMoviesView,
    TopRatedMoviesView,
    MovieRecommendationBatchView,
    
    # YouTube 관련 영상
    MovieRelatedVideosView,
)

app_name = 'movies'

urlpatterns = [

    # 1. 영화 정보 조회 (Public/General)
    path('', MovieListView.as_view(), name='movie-list'),
    path('search/', MovieSearchView.as_view(), name='movie-search'),  # 반드시 <uuid:pk>/ 보다 위에!
    path('boxoffice/', BoxOfficeView.as_view(), name='boxoffice'),
    path('upcoming/', UpcomingMoviesView.as_view(), name='upcoming'),
    path('top-rated/', TopRatedMoviesView.as_view(), name='top-rated'),
    path('recommendations/batch/', MovieRecommendationBatchView.as_view(), name='movie-recommendations-batch'),
    path('<uuid:pk>/', MovieDetailView.as_view(), name='movie-detail'),


    # 2. 영화 상호작용 (Actions)
    # URL 구조: /movies/{id}/{action}/
    path('<uuid:pk>/like/', MovieLikeView.as_view(), name='movie-like'),
    path('<uuid:pk>/save/', MovieSaveView.as_view(), name='movie-save'),
    path('<uuid:pk>/rate/', MovieRateView.as_view(), name='movie-rate'),
    path('<uuid:pk>/related-videos/', MovieRelatedVideosView.as_view(), name='movie-related-videos'),
    path('user-logs/', UserMovieLogBulkView.as_view(), name='movie-user-logs'),


    # 3. 사용자 개인화 목록 (My Lists)
    # URL 구조: /movies/my/{list_type}/
    path('my/saved/', MySaveListView.as_view(), name='my-saved-list'),
    path('my/rated/', MyRatedListView.as_view(), name='my-rated-list'),
    path('my/rated/logs/', MyRatedLogListView.as_view(), name='my-rated-log-list'),
    path('my/todays-pick/', TodaysPickListView.as_view(), name='todays-pick'),
]
