import uuid
from django.db import models
from django.db.models import Q, CheckConstraint
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError


# 0. 커스텀 유저 매니저
class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('이메일은 필수입니다.')
        if not username:
            raise ValueError('핸들(username)은 필수입니다.')
        
        email = self.normalize_email(email)
        if not email or '@' not in email:
            raise ValueError('유효한 이메일 주소를 입력하세요.')
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)


class User(AbstractUser):
    
    # 1. PK: UUID 설정
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='사용자 식별자'
    )

    # 2. 로그인 ID: 이메일(UK 필수)
    email = models.EmailField(
        unique=True,
        max_length=255,
        verbose_name='이메일'
    )

    # 3. 핸들: 식별자 (UK 필수) - 프로필 URL 및 태그(@)용
    username = models.CharField(
        max_length=30,
        unique=True,
        verbose_name='핸들(@)'
    )

    # 4. 닉네임: 화면 표시용 이름(중복 허용, 선택(기본값))
    nickname = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default='',
        verbose_name='닉네임'
    )

    # 3. 팔로우 기능 (편의성을 위한 M2M 필드)
    # through 옵션으로 Follow 모델을 중간 테이블로 지정합니다.
    followings = models.ManyToManyField(
        'self', 
        through='Follow', 
        symmetrical=False, 
        related_name='followers', 
        blank=True,
        verbose_name='팔로우 목록'
    )

    # 5. Soft Delete 지원
    is_active = models.BooleanField(
        default=True,
        verbose_name='활성 상태'
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='삭제 일시'
    )

    # 6. 메타 정보
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    # 불필요한 필드 제거
    first_name = None
    last_name = None

    # --- 설정 변경 ---
    USERNAME_FIELD = 'email'    # 이메일로 로그인
    REQUIRED_FIELDS = ['username']      # createsuperuser 시 핸들만 추가 입력
    objects = CustomUserManager()       # 커스텀 매니저 연결

    
    def soft_delete(self):
        """Soft Delete: 사용자를 비활성화하고 삭제 시간 기록"""
        from django.utils import timezone
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()
    
    def restore(self):
        """탈퇴 취소: 사용자 복구"""
        self.is_active = True
        self.deleted_at = None
        self.save()
    
    # --- 팔로우 헬퍼 메서드 ---
    def follow(self, user):
        """다른 사용자 팔로우"""
        if user == self:
            raise ValidationError('자기 자신을 팔로우할 수 없습니다.')
        from .models import Follow
        Follow.objects.get_or_create(follower=self, following=user)
    
    def unfollow(self, user):
        """팔로우 취소"""
        from .models import Follow
        Follow.objects.filter(follower=self, following=user).delete()
    
    def is_following(self, user):
        """팔로우 여부 확인"""
        return self.followings.filter(id=user.id).exists()
    
    def toggle_follow(self, user):
        """팔로우 토글 (있으면 취소, 없으면 팔로우)
        Returns: True(팔로우함), False(언팔로우함)
        """
        if self.is_following(user):
            self.unfollow(user)
            return False
        else:
            self.follow(user)
            return True
    
    def __str__(self):
        # 닉네임이 있으면 '닉네임 (@핸들)', 없으면 '@핸들' 형태로 변환
        display_name = self.nickname or self.username
        return f"{display_name} (@{self.username})"

    
class Profile(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='프로필 식별자'
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',  # user.profile로 접근 가능
        verbose_name='사용자'
    )
    bio = models.TextField(
        blank=True,
        null=True,
        verbose_name='자기소개'
    )
    profile_image = models.ImageField(
        upload_to='profile_images/',
        blank=True,
        null=True,
        verbose_name='프로필 이미지'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='수정일시'
    )

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Follow(models.Model):
    """사용자 팔로우 관계를 관리하는 모델"""
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='팔로우 식별자'
    )
    
    # 팔로우를 요청한 사용자 (A가 B를 팔로우 -> follower: A)
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following_relations',
        verbose_name='팔로워'
    )
    
    # 팔로우를 받는 사용자 (A가 B를 팔로우 -> following: B)
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower_relations',
        verbose_name='팔로잉'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='팔로우 일시'
    )
    
    class Meta:
        # 중복 팔로우 방지: 같은 사용자 쌍은 한 번만
        unique_together = ('follower', 'following')
        # DB 레벨에서 자기 자신 팔로우 방지
        constraints = [
            CheckConstraint(
                check=~Q(follower=models.F('following')),
                name='prevent_self_follow'
            )
        ]
        # 최신 팔로우가 먼저 나오도록
        ordering = ['-created_at']
        verbose_name = 'Follow'
        verbose_name_plural = 'Follows'

    def clean(self):
        if self.follower == self.following:
            raise ValidationError('자기 자신을 팔로우할 수 없습니다.')
    
    def save(self, *args, **kwargs):
        # clean() 메서드를 자동으로 호출하여 유효성 검사 수행
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.follower.username} → {self.following.username}"