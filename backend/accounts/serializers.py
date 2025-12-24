from rest_framework import serializers
from django.contrib.auth import get_user_model
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import UserDetailsSerializer
from .models import Profile, Follow

User = get_user_model()


class CustomRegisterSerializer(RegisterSerializer):
    # 1. 입력받을 추가 필드 정의
    nickname = serializers.CharField(
        max_length=50,
        required=False,      # 필드 자체가 없어도 됨
        allow_blank=True,
        allow_null=True,
        default="MovwaUser",
        help_text="별명 (입력하지 않거나, null/빈 값인 경우 'MovwaUser'로 설정됨)"    # API 문서(Swagger)에 설명 표시
    )

    # 입력값이 들어왔을 때, 내용을 검사하고 바꿔치기하는 함수
    def validate_nickname(self, value):
        # value가 None(null)이거나 ""(빈 문자열)이면 -> "MovwaUser"로 덮어씌움
        if not value: 
            return "MovwaUser"
        return value
    
    def save(self, request):
        user = super().save(request)
        
        # 필드 옵션에서 'default'를 설정했으므로, 
        # validated_data에는 무조건 nickname 값이 들어있습니다. (입력값 또는 기본값)
        user.nickname = self.validated_data.get('nickname') 
        user.save()
        
        return user


class CustomUserDetailsSerializer(UserDetailsSerializer):
    class Meta(UserDetailsSerializer.Meta):
        fields = (
            'pk',
            'email',
            'username',
            'nickname',
        )



class ProfileImageMixin(serializers.Serializer):
    # 프로필 이미지 URL 생성을 위한 공통 Mixin
    profile_image_url = serializers.SerializerMethodField()

    def get_profile_image_url(self, obj):
        # obj가 User인 경우 profile로 접근, Profile인 경우 그대로 사용
        profile = getattr(obj, 'profile', None)
        
        # profile이 없으면 obj가 Profile일 수도 있음
        if profile is None and hasattr(obj, 'profile_image'):
            profile = obj
        
        if profile and hasattr(profile, 'profile_image') and profile.profile_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(profile.profile_image.url)
            return profile.profile_image.url
        return None  # 프론트엔드에서 기본 이미지 처리 (null 반환)


class ProfileSerializer(ProfileImageMixin, serializers.ModelSerializer):
    # 프로필 조회용 (User 내부용)
    
    class Meta:
        model = Profile
        fields = ['bio', 'profile_image', 'profile_image_url', 'updated_at']
        read_only_fields = ['updated_at']


class UserSimpleSerializer(ProfileImageMixin, serializers.ModelSerializer):
    """
    사용자 목록/간단 조회용
    팔로우 목록, 검색 결과 등에서 사용하는 경량화된 Serializer
    """
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'nickname', 'profile_image_url', 'is_following']

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # 쿼리 최적화를 위해 exists() 사용 (Follow 모델 직접 조회)
            return Follow.objects.filter(follower=request.user, following=obj).exists()
        return False


class UserDetailSerializer(ProfileImageMixin, serializers.ModelSerializer):
    """
    사용자 상세 조회용 (마이페이지, 유저페이지)
    프로필 + 팔로우 정보 포함
    """
    bio = serializers.CharField(source='profile.bio', read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'nickname', 'email', 
            'bio', 'profile_image_url', 
            'followers_count', 'following_count', 
            'is_following', 'date_joined'
        ]
        read_only_fields = ['id', 'username', 'email', 'date_joined']

    def get_followers_count(self, obj):
        # 팔로워 수
        return obj.followers.count()
    
    def get_following_count(self, obj):
        # 팔로잉 수
        return obj.followings.count()
    
    def get_is_following(self, obj):
        # 현재 로그인한 사용자가 이 사용자를 팔로우하는지
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            if request.user == obj:
                return False  # 본인은 팔로우 대상 아님
            return Follow.objects.filter(follower=request.user, following=obj).exists()
        return False


class UserUpdateSerializer(ProfileImageMixin, serializers.ModelSerializer):
    """
    회원정보 수정 (User 테이블 + Profile 테이블 동시 수정)
    닉네임 + 프로필(bio, image) 수정
    """
    
    bio = serializers.CharField(required=False, allow_blank=True)
    profile_image = serializers.ImageField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = User
        fields = ['nickname', 'bio', 'profile_image', 'profile_image_url']
        read_only_fields = ['profile_image_url']

    def validate_profile_image(self, value):
        # 이미지 크기 제한 (5MB)
        if value and value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('이미지 크기는 5MB 이하여야 합니다.')
        return value

    def update(self, instance, validated_data):
        # 1. User 정보 수정 (nickname)
        if 'nickname' in validated_data:
            instance.nickname = validated_data['nickname']
            instance.save()

        # 2. Profile 정보 수정 (bio, image)
        # Signal로 프로필이 자동 생성되지만, 만약을 대비한 방어 코드
        if hasattr(instance, 'profile'):
            profile = instance.profile
        else:
            # 혹시 프로필이 없다면 생성 (방어 코드)
            profile = Profile.objects.create(user=instance)
        
        if 'bio' in validated_data:
            profile.bio = validated_data['bio']
        if 'profile_image' in validated_data:
            profile.profile_image = validated_data['profile_image']
        
        profile.save()
        
        # 3. profile을 다시 로드하여 최신 상태 반영
        instance.refresh_from_db()
        return instance


class FollowSerializer(serializers.ModelSerializer):
    # 팔로우 관계 조회용
    # UserSimpleSerializer를 재사용하여 코드 중복 제거
    follower = UserSimpleSerializer(read_only=True)
    following = UserSimpleSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['id', 'created_at']