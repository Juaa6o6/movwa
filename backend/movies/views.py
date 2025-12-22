from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination

from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Movie
from .serializers import MovieListSerializer

# 페이지네이션 설정 (기본 10개씩)
class MoviePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

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