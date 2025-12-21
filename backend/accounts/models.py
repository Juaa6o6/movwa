import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

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
        default='MovwaUser',
        verbose_name='닉네임'
    )

    # 5. 메타 정보
    updated_at = models.DateTimeField(auto_now=True)

    # 불필요한 필드 제거
    first_name = None
    last_name = None

    # --- 설정 변경 ---
    USERNAME_FIELD = 'email'    # 이메일로 로그인
    REQUIRED_FIELDS = ['username']      # createsuperuser 시 핸들만 추가 입력

    
    def __str__(self):
        # 닉네임이 있으면 '닉네임 (@핸들)', 없으면 '@핸들' 형태로 변환
        display_name = self.nickname if self.nickname else "NoName"
        return f"{display_name} (@{self.nickname})"
