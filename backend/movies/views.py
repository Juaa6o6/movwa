from django.utils import timezone
from datetime import timedelta, date
from django.db.models import Q, Case, When, IntegerField, Max

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination

from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.shortcuts import get_object_or_404

from .models import Movie, UserMovieLog, BoxOfficeRank
from .serializers import (
    MovieListSerializer, MovieDetailSerializer,
    MovieLikeSerializer, MovieSaveSerializer, MovieRateSerializer,
    BoxOfficeRankSerializer,
    YouTubeVideoSerializer,
)

# 페이지네이션 설정 (기본 10개씩)
class MoviePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

# 언어 필터링 헬퍼 함수
def apply_language_filter(queryset, request):
    """
    쿼리 파라미터 'language'에 따라 영화 필터링
    - ko (기본값): 한글 제목 포함 영화만
    - all: 모든 영화
    - en: 영어 영화만
    """
    language = request.query_params.get('language', 'ko')
    
    if language == 'ko':
        # 한글이 포함된 제목 (한국 영화 + 한글화된 외국 영화)
        queryset = queryset.filter(title__regex=r'[가-힣]')
    elif language == 'en':
        # 영어만 (한글 없음)
        queryset = queryset.exclude(title__regex=r'[가-힣]')
    # 'all'인 경우 필터링 안 함
    
    return queryset

# 영화 목록 조회
class MovieListView(APIView):
    permission_classes = [AllowAny] # 인증 없이 누구나 조회 가능

    @extend_schema(
        tags=['movies'],
        summary="영화 목록 조회",
        description="전체 영화 목록을 조회합니다. 페이지네이션이 적용되어 있습니다.",
        parameters=[
            OpenApiParameter(name='page', description='페이지 번호', required=False, type=int),
            OpenApiParameter(name='language', description='언어 필터 (ko: 한글[기본값], all: 전체, en: 영어)', required=False, type=str),
        ],
        responses={200: MovieListSerializer(many=True)}
    )
    def get(self, request):
        # 1. ORM 조회 (최적화 적용)
        movies = Movie.objects.all().prefetch_related('genres')
        
        # 2. 언어 필터링 적용
        movies = apply_language_filter(movies, request)
        
        # 3. 정렬
        movies = movies.order_by('-release_date')
        
        # 4. 페이지네이션 처리
        
        # 4. 페이지네이션 처리
        paginator = MoviePagination()
        paginated_movies = paginator.paginate_queryset(movies, request)
        
        # 5. 직렬화 (Serializer)
        serializer = MovieListSerializer(paginated_movies, many=True)
        
        # 6. 응답 반환
        return paginator.get_paginated_response(serializer.data)

# 영화 상세 정보 조회
class MovieDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['movies'],
        summary="영화 상세 조회",
        description="영화의 상세 정보를 조회합니다. (줄거리, 출연진, 예고편 등)",
        responses={200: MovieDetailSerializer}
    )
    
    def get(self, request, pk):

        # DB에서 영화 찾기 (없으면 404 에러 자동 발생)
        movie = get_object_or_404(Movie, pk=pk)

        # 직렬화 (상세 정보 전용 Serializer 사용)
        serializer = MovieDetailSerializer(movie)

        return Response(serializer.data)
    

# 특정 유저와 영화에 대한 로그(UserMovieLog)를 가져오거나, 없으면 새로 생성
def get_user_movie_log(user, movie_pk):

    movie = get_object_or_404(Movie, pk=movie_pk)
    # get_or_create: (객체, 생성여부_boolean) 튜플을 반환
    log, created = UserMovieLog.objects.get_or_create(user=user, movie=movie)
    return log

# 좋아요 / 싫어요 / 평가없음
class MovieLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['movies'],
        summary="영화 좋아요/싫어요 등록",
        description="is_liked: true(좋아요), false(싫어요), null(평가취소)",
        request=MovieLikeSerializer,
        responses=MovieLikeSerializer
    )
    def post(self, request, pk):
        log = get_user_movie_log(request.user, pk)
        serializer = MovieLikeSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            # partial update: 기존 평점이나 찜 상태는 건드리지 않고 '좋아요'만 수정
            log.is_liked = serializer.validated_data['is_liked']
            log.save(update_fields=['is_liked', 'updated_at'])

            return Response(serializer.data, status=status.HTTP_200_OK)
        
# 나중에 볼 영화
class MovieSaveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['movies'],
        summary="나중에 볼 영화(보고싶어요)",
        description="is_saved: true(찜하기), false(찜 해제)",
        request=MovieSaveSerializer,
        responses=MovieSaveSerializer
    )
    def post(self, request, pk):
        log = get_user_movie_log(request.user, pk)
        serializer = MovieSaveSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            log.is_saved = serializer.validated_data['is_saved']
            log.save(update_fields=['is_saved', 'updated_at'])

            return Response(serializer.data, status=status.HTTP_200_OK)
        
# 평점 등록 / 수정 / 삭제
class MovieRateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['movies'],
        summary="영화 평점 등록/수정",
        description="0.5 ~ 5.0 사이의 평점을 0.5 단위로 입력합니다.",
        request=MovieRateSerializer,
        responses=MovieRateSerializer
    )
    def post(self, request, pk):
        log = get_user_movie_log(request.user, pk)
        serializer = MovieRateSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            log.rating = serializer.validated_data['rating']
            log.save(update_fields=['rating', 'updated_at'])
            return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['movies'],
        summary="영화 평점 삭제",
        description="DB에서 로그를 삭제하는 것이 아니라 rating 필드만 null로 초기화합니다.",
        responses={204: None}
    )
    def delete(self, request, pk):
        # 로그가 아예 없으면 삭제할 것도 없으므로 204 반환
        if not UserMovieLog.objects.filter(user=request.user, movie__pk=pk).exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        log = get_user_movie_log(request.user, pk)
        
        # [중요] 실제 레코드를 삭제(delete)하면 안 됨! 좋아요/찜 기록이 날아감.
        # 평점 필드만 None으로 변경 (Soft Delete 개념)
        log.rating = None
        log.save(update_fields=['rating', 'updated_at'])
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    

# [View 4] 내가 찜한 영화 목록 (M-08)
class MySaveListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['movies'],
        summary="내가 찜한 영화 목록 조회",
        description="현재 로그인한 유저가 찜(is_saved=True)한 영화 목록을 최근 순으로 조회합니다.",
        responses=MovieListSerializer(many=True)
    )
    def get(self, request):
        # 1. 내가 찜한 로그 필터링 + 최신순 정렬 + 영화 정보 로딩 최적화
        logs = UserMovieLog.objects.filter(
            user=request.user, 
            is_saved=True
        ).select_related('movie').order_by('-updated_at')
        
        # 2. 로그에서 영화 객체만 추출
        movies = [log.movie for log in logs]
        
        # 3. 직렬화
        serializer = MovieListSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# [View 5] 내가 평가한 영화 목록 (M-09)
class MyRatedListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['movies'],
        summary="내가 평가한 영화 목록 조회",
        description="현재 로그인한 유저가 평점을 남긴 영화 목록을 최근 순으로 조회합니다.",
        responses=MovieListSerializer(many=True)
    )
    def get(self, request):
        # 1. 평점이 있는(isnull=False) 로그 필터링 + 최신순 정렬
        logs = UserMovieLog.objects.filter(
            user=request.user, 
            rating__isnull=False
        ).select_related('movie').order_by('-updated_at')
        
        movies = [log.movie for log in logs]
        
        serializer = MovieListSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# [View 6] 오늘의 픽 (REC-09) - 24시간 이내 좋아요한 영화
class TodaysPickListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=['movies'],
        summary="오늘의 픽 (24시간 내 좋아요한 영화)",
        description="[REC-09] 사용자가 최근 24시간 이내에 '좋아요(is_liked=True)'를 누른 영화 목록을 최신순으로 반환합니다.",
        responses=MovieListSerializer(many=True)
    )
    def get(self, request):
        # 1. 시간 계산: 현재 시간으로부터 24시간 전 시점 구하기
        now = timezone.now()
        last_24h = now - timedelta(hours=24)

        # 2. 필터링 로직 구현
        # - user: 나
        # - is_liked: 좋아요 상태
        # - updated_at__gte: 수정된 시간이 '24시간 전'보다 크거나 같음 (즉, 최근 24시간 이내)
        logs = UserMovieLog.objects.filter(
            user=request.user,
            is_liked=True,
            updated_at__gte=last_24h  # [핵심 로직] Time Filter
        ).select_related('movie').order_by('-updated_at') # [정렬] 최신순

        # 3. 영화 객체 추출 및 직렬화
        movies = [log.movie for log in logs]
        serializer = MovieListSerializer(movies, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)


# 영화 검색
class MovieSearchView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        tags=['movies'],
        summary="영화 검색",
        description="제목, 원제, 장르를 통합 검색합니다. q 파라미터에 검색어를 입력하세요.",
        parameters=[
            OpenApiParameter(
                name='q',
                description='검색어 (제목, 원제, 장르 검색)',
                required=True,
                type=str
            ),
            OpenApiParameter(
                name='sort',
                description='정렬 기준 (popularity: 인기도순[기본], relevance: 관련도순, latest: 최신순)',
                required=False,
                type=str
            ),
            OpenApiParameter(
                name='page',
                description='페이지 번호',
                required=False,
                type=int
            ),
        ],
        responses={200: MovieListSerializer(many=True)}
    )
    def get(self, request):
        # 1. 검색어 가져오기
        search_query = request.query_params.get('q', '').strip()
        
        if not search_query:
            return Response(
                {"error": "검색어(q)를 입력해주세요."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. 검색 실행 (제목 OR 원제 OR 장르)
        movies = Movie.objects.filter(
            Q(title__icontains=search_query) |
            Q(original_title__icontains=search_query) |
            Q(genres__name__icontains=search_query)
        ).prefetch_related('genres').distinct()
        
        # 3. 정렬 옵션 처리
        sort_option = request.query_params.get('sort', 'popularity')
        
        if sort_option == 'relevance':
            # 관련도순: 제목 정확일치 > 제목 시작 > 제목 포함 > 원제 포함 > 장르 일치
            movies = movies.annotate(
                relevance=Case(
                    When(title__iexact=search_query, then=4),  # 제목 정확 일치
                    When(title__istartswith=search_query, then=3),  # 제목 시작
                    When(title__icontains=search_query, then=2),  # 제목 포함
                    When(original_title__icontains=search_query, then=1),  # 원제 포함
                    default=0,  # 장르만 일치
                    output_field=IntegerField()
                )
            ).order_by('-relevance', '-popularity')
        elif sort_option == 'latest':
            # 최신순
            movies = movies.order_by('-release_date')
        else:
            # 인기도순 (기본값)
            movies = movies.order_by('-popularity')
        
        # 4. 페이지네이션
        paginator = MoviePagination()
        paginated_movies = paginator.paginate_queryset(movies, request)
        
        # 5. 직렬화
        serializer = MovieListSerializer(paginated_movies, many=True)
        
        # 6. 응답 반환
        return paginator.get_paginated_response(serializer.data)


# 박스오피스 순위 조회
class BoxOfficeView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        tags=['movies'],
        summary="박스오피스 순위 조회",
        description="KOBIS 기반 박스오피스 순위를 조회합니다. 일간/주간 선택 가능.",
        parameters=[
            OpenApiParameter(
                name='rank_type',
                description='순위 타입 (daily: 일간[기본], weekly: 주간)',
                required=False,
                type=str
            ),
            OpenApiParameter(
                name='limit',
                description='조회할 순위 개수 (기본 10개)',
                required=False,
                type=int
            ),
        ],
        responses={200: BoxOfficeRankSerializer(many=True)}
    )
    def get(self, request):
        # 1. 파라미터 가져오기 및 검증
        rank_type = request.query_params.get('rank_type', 'daily')
        
        # rank_type 검증
        if rank_type not in ['daily', 'weekly']:
            return Response(
                {"error": "rank_type은 'daily' 또는 'weekly'만 가능합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # limit 검증
        try:
            limit = int(request.query_params.get('limit', 10))
            if limit < 1 or limit > 100:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {"error": "limit은 1~100 사이의 숫자여야 합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. 최신 날짜의 박스오피스 순위 조회
        latest_date = BoxOfficeRank.objects.filter(rank_type=rank_type).aggregate(
            Max('date')
        )['date__max']
        
        if not latest_date:
            return Response(
                {"message": "박스오피스 데이터가 없습니다."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 3. 해당 날짜의 순위 조회 (상위 N개)
        ranks = BoxOfficeRank.objects.filter(
            rank_type=rank_type,
            date=latest_date
        ).select_related('movie').prefetch_related('movie__genres').order_by('rank')[:limit]
        
        # 4. 직렬화
        serializer = BoxOfficeRankSerializer(ranks, many=True)
        
        # 5. 응답 반환
        return Response({
            'date': latest_date,
            'rank_type': rank_type,
            'results': serializer.data
        }, status=status.HTTP_200_OK)


# 개봉 예정 영화 조회
class UpcomingMoviesView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        tags=['movies'],
        summary="개봉 예정 영화 조회",
        description="오늘 이후 개봉 예정인 영화를 개봉일 순으로 조회합니다.",
        parameters=[
            OpenApiParameter(
                name='limit',
                description='조회할 개수 (기본 20개)',
                required=False,
                type=int
            ),
            OpenApiParameter(
                name='language',
                description='언어 필터 (ko: 한글[기본값], all: 전체, en: 영어)',
                required=False,
                type=str
            ),
        ],
        responses={200: MovieListSerializer(many=True)}
    )
    def get(self, request):
        # 1. limit 파라미터 검증
        try:
            limit = int(request.query_params.get('limit', 20))
            if limit < 1 or limit > 100:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {"error": "limit은 1~100 사이의 숫자여야 합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. 오늘 날짜 이후 개봉 예정작 조회
        today = date.today()
        movies = Movie.objects.filter(
            release_date__gt=today
        ).prefetch_related('genres')
        
        # 3. 언어 필터링 적용
        movies = apply_language_filter(movies, request)
        
        # 4. 정렬 및 제한
        movies = movies.order_by('release_date')[:limit]
        
        # 5. 직렬화
        serializer = MovieListSerializer(movies, many=True)
        
        # 6. 응답 반환
        # 4. 응답 반환
        return Response(serializer.data, status=status.HTTP_200_OK)


# 평점 높은 영화 조회
class TopRatedMoviesView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(
        tags=['movies'],
        summary="평점 높은 영화 조회",
        description="평점이 높은 영화를 조회합니다. 최소 투표 수 100개 이상인 영화만 포함됩니다.",
        parameters=[
            OpenApiParameter(
                name='limit',
                description='조회할 개수 (기본 20개)',
                required=False,
                type=int
            ),
            OpenApiParameter(
                name='min_votes',
                description='최소 투표 수 (기본 100)',
                required=False,
                type=int
            ),
            OpenApiParameter(
                name='language',
                description='언어 필터 (ko: 한글[기본값], all: 전체, en: 영어)',
                required=False,
                type=str
            ),
        ],
        responses={200: MovieListSerializer(many=True)}
    )
    def get(self, request):
        # 1. 파라미터 검증
        try:
            limit = int(request.query_params.get('limit', 20))
            if limit < 1 or limit > 100:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {"error": "limit은 1~100 사이의 숫자여야 합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            min_votes = int(request.query_params.get('min_votes', 100))
            if min_votes < 0:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {"error": "min_votes는 0 이상의 숫자여야 합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 2. 평점 높은 영화 조회 (최소 투표 수 필터링)
        movies = Movie.objects.filter(
            vote_count__gte=min_votes
        ).prefetch_related('genres')
        
        # 3. 언어 필터링 적용
        movies = apply_language_filter(movies, request)
        
        # 4. 정렬 및 제한
        movies = movies.order_by('-vote_average', '-vote_count')[:limit]
        
        # 5. 직렬화
        serializer = MovieListSerializer(movies, many=True)
        
        # 6. 응답 반환
        return Response(serializer.data, status=status.HTTP_200_OK)


# 영화 관련 YouTube 영상 조회
class MovieRelatedVideosView(APIView):
    """
    특정 영화의 관련 YouTube 영상을 조회합니다.
    
    - 영화 제목으로 YouTube 검색
    - 리뷰, 후기, 예고편 영상 포함
    - 최대 15개 영상 반환
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        tags=['movies'],
        summary="영화 관련 YouTube 영상 조회",
        description="영화 제목으로 YouTube에서 리뷰, 후기, 예고편 영상을 검색합니다.",
        responses={200: YouTubeVideoSerializer(many=True)}
    )
    def get(self, request, pk):
        # 1. 영화 조회
        movie = get_object_or_404(Movie, pk=pk)
        
        # 2. YouTube API로 관련 영상 검색
        from .youtube_api import fetch_youtube_videos
        youtube_videos = fetch_youtube_videos(movie.title, max_results=15)
        
        # 3. 직렬화
        serializer = YouTubeVideoSerializer(youtube_videos, many=True)
        
        # 4. 응답 반환
        return Response({
            'movie_id': str(movie.id),
            'movie_title': movie.title,
            'total_videos': len(youtube_videos),
            'videos': serializer.data
        }, status=status.HTTP_200_OK)