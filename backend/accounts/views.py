from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import User, Follow
from .serializers import (
    UserDetailSerializer,
    UserUpdateSerializer,
    UserSimpleSerializer,
    FollowSerializer,
)


# U-08: 프로필 조회
@extend_schema(
    tags=['accounts'],
    summary='사용자 프로필 조회',
    description='특정 사용자의 프로필 상세 정보를 조회합니다. username으로 조회하며, 팔로워/팔로잉 수를 포함합니다.',
    parameters=[
        OpenApiParameter(
            name='username',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='조회할 사용자의 username'
        )
    ],
    responses={200: UserDetailSerializer}
)
class UserDetailView(generics.RetrieveAPIView):
    """
    특정 사용자의 프로필 상세 정보를 조회합니다.
    - username으로 조회
    - 팔로워/팔로잉 수 포함
    - 로그인한 사용자의 경우 is_following 포함
    """
    serializer_class = UserDetailSerializer
    lookup_field = 'username'
    
    def get_queryset(self):
        # 탈퇴하지 않은 사용자만 조회
        # [최적화] ProfileImageMixin이 profile을 참조하므로 select_related로 미리 로드
        return User.objects.filter(is_active=True).select_related('profile')


# U-09: 프로필 수정
@extend_schema(
    tags=['accounts'],
    summary='내 프로필 수정',
    description='로그인한 사용자의 프로필을 수정합니다. nickname, bio, profile_image를 수정할 수 있습니다.',
    request=UserUpdateSerializer,
    responses={200: UserUpdateSerializer}
)
class UserUpdateView(generics.UpdateAPIView):
    """
    로그인한 사용자의 프로필을 수정합니다.
    - 본인만 수정 가능
    - nickname, bio, profile_image 수정 가능
    """
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        # 항상 현재 로그인한 사용자의 프로필을 수정
        # [최적화] update 시에도 profile 접근하므로 select_related 사용
        return User.objects.select_related('profile').get(pk=self.request.user.pk)


# U-10: 팔로우 토글
@extend_schema(
    tags=['accounts'],
    summary='팔로우 토글',
    description='특정 사용자를 팔로우하거나 언팔로우합니다. 이미 팔로우 중이면 언팔로우, 아니면 팔로우합니다.',
    parameters=[
        OpenApiParameter(
            name='username',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='팔로우/언팔로우할 사용자의 username'
        )
    ],
    responses={
        200: OpenApiTypes.OBJECT,
        400: OpenApiTypes.OBJECT
    },
    examples=[
        OpenApiExample(
            '팔로우 성공',
            value={
                'detail': '팔로우 했습니다.',
                'is_following': True,
                'target_username': 'user2',
                'followers_count': 10,
                'following_count': 5
            },
            response_only=True
        )
    ]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_toggle(request, username):
    """
    특정 사용자를 팔로우하거나 언팔로우합니다.
    - 본인은 팔로우 불가
    - 이미 팔로우 중이면 언팔로우, 아니면 팔로우
    """
    target_user = get_object_or_404(User, username=username, is_active=True)
    
    # 본인 팔로우 방지
    if target_user == request.user:
        return Response(
            {'detail': '본인을 팔로우할 수 없습니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 팔로우 토글 (User 모델의 메서드 활용)
    is_following = request.user.toggle_follow(target_user)
    
    # 프론트엔드 실시간 업데이트를 위한 상세 정보 포함
    return Response({
        'detail': '팔로우 했습니다.' if is_following else '언팔로우 했습니다.',
        'is_following': is_following,
        'target_username': target_user.username,
        'followers_count': target_user.followers.count(),
        'following_count': target_user.followings.count()
    }, status=status.HTTP_200_OK)


# U-11: 팔로워 목록 조회
@extend_schema(
    tags=['accounts'],
    summary='팔로워 목록 조회',
    description='특정 사용자를 팔로우하는 사용자 목록을 조회합니다.',
    parameters=[
        OpenApiParameter(
            name='username',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='팔로워 목록을 조회할 사용자의 username'
        )
    ],
    responses={200: UserSimpleSerializer(many=True)}
)
class FollowersListView(generics.ListAPIView):
    """
    특정 사용자를 팔로우하는 사용자 목록을 조회합니다.
    """
    serializer_class = UserSimpleSerializer
    
    def get_queryset(self):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username, is_active=True)
        # 해당 사용자를 팔로우하는 사람들 (followers)
        # [최적화] UserSimpleSerializer가 profile_image_url을 사용하므로 select_related 필수
        return user.followers.filter(is_active=True).select_related('profile').order_by('-id')


# U-12: 팔로잉 목록 조회
@extend_schema(
    tags=['accounts'],
    summary='팔로잉 목록 조회',
    description='특정 사용자가 팔로우하는 사용자 목록을 조회합니다.',
    parameters=[
        OpenApiParameter(
            name='username',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='팔로잉 목록을 조회할 사용자의 username'
        )
    ],
    responses={200: UserSimpleSerializer(many=True)}
)
class FollowingsListView(generics.ListAPIView):
    """
    특정 사용자가 팔로우하는 사용자 목록을 조회합니다.
    """
    serializer_class = UserSimpleSerializer
    
    def get_queryset(self):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username, is_active=True)
        # 해당 사용자가 팔로우하는 사람들 (followings)
        # [최적화] UserSimpleSerializer가 profile_image_url을 사용하므로 select_related 필수
        return user.followings.filter(is_active=True).select_related('profile').order_by('-id')


# 추가: 현재 로그인한 내 정보 조회
@extend_schema(
    tags=['accounts'],
    summary='내 정보 조회',
    description='현재 로그인한 사용자의 프로필 정보를 조회합니다. 프론트엔드에서 Navbar, 프로필 표시용으로 사용됩니다.',
    responses={200: UserDetailSerializer}
)
class CurrentUserView(generics.RetrieveAPIView):
    """
    현재 로그인한 사용자의 프로필 정보를 조회합니다.
    - GET /api/v1/users/me/
    - 프론트엔드에서 Navbar, 프로필 표시용으로 사용
    - username 없이도 내 정보에 접근 가능
    """
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        # request.user를 직접 반환 (현재 로그인한 사용자)
        # [최적화] profile 정보도 함께 조회
        return User.objects.select_related('profile').get(pk=self.request.user.pk)


# 추가: 회원 탈퇴 (Soft Delete)
@extend_schema(
    tags=['accounts'],
    summary='회원 탈퇴',
    description='현재 로그인한 사용자를 탈퇴 처리합니다 (Soft Delete). DB에서 삭제하지 않고 is_active=False로 변경합니다.',
    responses={
        200: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            '탈퇴 성공',
            value={'detail': '회원 탈퇴가 완료되었습니다.'},
            response_only=True
        )
    ]
)
class UserDeleteView(generics.DestroyAPIView):
    """
    현재 로그인한 사용자를 탈퇴 처리합니다 (Soft Delete).
    - DELETE /api/v1/users/me/
    - is_active=False로 변경 (DB에서 삭제하지 않음)
    - deleted_at에 탈퇴 시간 기록
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        # User 모델에 정의된 soft_delete() 메서드 활용
        user.soft_delete()
        return Response(
            {'detail': '회원 탈퇴가 완료되었습니다.'},
            status=status.HTTP_200_OK
        )
