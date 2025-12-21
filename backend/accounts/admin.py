from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    # 1. 목록 화면에서 보여줄 컬럼 지정
    # (기존 first_name, last_name 제거 / nickname 추가)
    list_display = ('username', 'email', 'nickname', 'is_staff', 'is_active', 'date_joined')

    # 2. 목록 필터 우측 사이드바 설정
    list_filter = ('is_staff', 'is_active', 'groups')

    # 3. 검색창에서 검색할 필드 설정 (핸들, 이메일, 닉네임으로 검색 가능)
    search_fields = ('username', 'email', 'nickname')

    # 4. 정렬 기준 (최신 가입순)
    ordering = ('-date_joined',)

    # 5. 상세 수정 화면(Detail) 구성 재정의
    # 주의: 이걸 설정하지 않으면 수정 화면 진입 시 first_name을 찾다가 에러가 납니다.
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('개인 정보', {'fields': ('email', 'nickname')}),  # nickname 추가
        ('권한', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('중요 일자', {'fields': ('last_login', 'date_joined')}),
    )

    # 6. 유저 생성 화면(Add User) 구성 재정의
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'nickname', 'password', 'password_2'),
        }),
    )

# 만든 설정 클래스로 등록
admin.site.register(User, CustomUserAdmin)