from django.utils import timezone
from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination

from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.shortcuts import get_object_or_404

from .models import Movie, UserMovieLog
from .serializers import (
    MovieListSerializer, MovieDetailSerializer,
    MovieLikeSerializer, MovieSaveSerializer, MovieRateSerializer,
)

# 페이지네이션 설정 (기본 10개씩)
class MoviePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

# 영화 목록 조회
class MovieListView(APIView):
    permission_classes = [AllowAny] # 인증 없이 누구나 조회 가능

    @extend_schema(
        tags=["Movies"],
        summary="영화 목록 조회",
        description="전체 영화 목록을 조회합니다. 페이지네이션이 적용되어 있습니다.",
        parameters=[
            OpenApiParameter(name='page', description='페이지 번호', required=False, type=int),
        ],
        responses={200: MovieListSerializer(many=True)}
    )
    def get(self, request):
        # 1. ORM 조회 (최적화 적용)
        # [중요] genres 필드가 추가되었으므로 prefetch_related를 써야 쿼리 속도가 느려지지 않습니다.
        movies = Movie.objects.all().prefetch_related('genres').order_by('-release_date')
        
        # 2. 페이지네이션 처리
        paginator = MoviePagination()
        paginated_movies = paginator.paginate_queryset(movies, request)
        
        # 3. 직렬화 (Serializer)
        # 국가(original_language), 러닝타임(runtime), 장르(genres)가 포함된 Serializer 사용
        serializer = MovieListSerializer(paginated_movies, many=True)
        
        # 4. 응답 반환
        return paginator.get_paginated_response(serializer.data)

# 영화 상세 정보 조회
class MovieDetailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Movies'],
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