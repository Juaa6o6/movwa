from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

# [Swagger 설정을 위한 임포트]
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, inline_serializer
from drf_spectacular.types import OpenApiTypes

from .models import Review, ReviewLike
from .serializers import ReviewSerializer, MyReviewSerializer
from .permissions import IsOwnerOrReadOnly

@extend_schema_view(
    list=extend_schema(
        tags=['Reviews'],
        summary="리뷰 목록 조회",
        description="영화별(movie_id) 필터링 및 정렬(ordering) 옵션을 제공합니다. (기본값: 인기순)",
        parameters=[
            OpenApiParameter(
                name='movie_id', 
                description='영화 UUID (특정 영화의 리뷰만 조회 시 사용)', 
                required=False, 
                type=OpenApiTypes.UUID
            ),
            OpenApiParameter(
                name='ordering', 
                description='정렬 옵션: best(좋아요순-기본값), latest(최신순), high(평점높은순), low(평점낮은순)', 
                required=False, 
                type=OpenApiTypes.STR
            ),
        ]
    ),
    create=extend_schema(
        tags=['Reviews'],
        summary="리뷰 작성",
        description="movie_id, content, rating, is_spoiler를 입력받아 리뷰를 생성합니다. (1인 1리뷰 제한)"
    ),
    retrieve=extend_schema(
        tags=['Reviews'],
        summary="리뷰 상세 조회",
        description="리뷰 ID를 통해 개별 리뷰 정보를 조회합니다."
    ),
    
    # [수정] PUT 방식은 사용하지 않으므로 Swagger에서 숨김 처리
    update=extend_schema(exclude=True),
    
    partial_update=extend_schema(
        tags=['Reviews'],
        summary="리뷰 수정 (PATCH)",
        description="본인이 작성한 리뷰의 일부 필드(content, rating 등)만 수정합니다."
    ),
    destroy=extend_schema(
        tags=['Reviews'],
        summary="리뷰 삭제",
        description="본인이 작성한 리뷰를 삭제합니다."
    ),
    like=extend_schema(
        tags=['Reviews'],
        summary="리뷰 좋아요/취소 (Toggle)",
        description="이미 좋아요를 누른 상태면 취소, 아니면 좋아요를 추가합니다.",
        request=None, 
        responses={
            200: inline_serializer(
                name='LikeResponse',
                fields={
                    'is_liked': serializers.BooleanField(),
                    'like_count': serializers.IntegerField(),
                }
            )
        }
    ),
    me=extend_schema(
        tags=['Reviews'],
        summary="내가 작성한 리뷰 목록",
        description="내가 쓴 리뷰를 최신순으로 조회합니다. (영화 정보 포함)",
        responses=MyReviewSerializer(many=True)
    ),
    content=extend_schema(
        tags=['Reviews'],
        summary="스포일러 리뷰 원본 내용 조회",
        description="마스킹 처리되지 않은 원본 텍스트를 반환합니다.",
        responses={
            200: inline_serializer(
                name='SpoilerContentResponse',
                fields={
                    'content': serializers.CharField(),
                }
            )
        }
    )
)
class ReviewViewSet(viewsets.ModelViewSet):
    """
    [리뷰 통합 ViewSet]
    - 기본 정렬: 좋아요순 (Best)
    - 수정 방식: PATCH Only (PUT 불가)
    - 중복 방지: 1인 1영화 1리뷰
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    
    # [수정] http_method_names를 정의하여 PUT을 원천 차단합니다.
    # 허용할 메서드: GET, POST, PATCH, DELETE, HEAD, OPTIONS
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        # 1. 기본 쿼리셋 (좋아요 개수 카운트 포함 - 정렬용)
        queryset = Review.objects.annotate(like_count=Count('likes'))

        # 2. 내 리뷰 모아보기 (Action이 'me'일 때)
        if self.action == 'me':
            return queryset.filter(user=self.request.user).order_by('-created_at')

        # 3. 영화별 필터링
        movie_id = self.request.query_params.get('movie_id')
        if movie_id:
            queryset = queryset.filter(movie_id=movie_id)

        # 4. 정렬 (Query Param: ?ordering=...)
        ordering = self.request.query_params.get('ordering')
        
        # [수정] 기본값(else)을 좋아요순(best)으로 변경
        if ordering == 'latest':
            queryset = queryset.order_by('-created_at')                # 최신순
        elif ordering == 'high':
            queryset = queryset.order_by('-rating', '-created_at')     # 평점 높은순
        elif ordering == 'low':
            queryset = queryset.order_by('rating', '-created_at')      # 평점 낮은순
        else:
            # ordering이 'best'이거나 없을 경우 (Default)
            queryset = queryset.order_by('-like_count', '-created_at') # 좋아요순

        return queryset

    # 시리얼라이저 교체 (내 리뷰 조회 시 MyReviewSerializer 사용)
    def get_serializer_class(self):
        if self.action == 'me':
            return MyReviewSerializer
        return super().get_serializer_class()

    # R-01: 리뷰 작성 시 작성자(user) 자동 저장
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # R-06: 리뷰 좋아요 토글 (POST /reviews/{pk}/like/)
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        review = self.get_object()
        user = request.user

        # 이미 좋아요를 눌렀다면 -> 삭제 (Unlike)
        if review.likes.filter(user=user).exists():
            review.likes.filter(user=user).delete()
            is_liked = False

        # 안 눌렀다면 -> 생성 (Like)
        else:
            ReviewLike.objects.create(review=review, user=user)
            is_liked = True
        
        # 응답 데이터: 현재 상태 및 갱신된 좋아요 개수
        return Response({
            'is_liked': is_liked,
            'like_count': review.likes.count()
        }, status=status.HTTP_200_OK)

    # R-07: 내 리뷰 모아보기 (GET /reviews/me/)
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        queryset = self.get_queryset()     # 위에서 정의한 get_queryset의 'me' 분기 탐
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # R-08: 스포일러 내용 상세 조회 (GET /reviews/{pk}/content/)
    @action(detail=True, methods=['get'])
    def content(self, request, pk=None):
        review = self.get_object()
        # 원본 내용은 Serializer를 거치지 않고 직접 반환하거나,
        # Serializer Context를 활용할 수도 있지만, 여기선 가장 가볍게 직접 반환합니다.
        return Response({'content': review.content}, status=status.HTTP_200_OK)