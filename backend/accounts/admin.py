from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, Follow


# Profile Inline: User 페이지에서 Profile을 함께 편집
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = '프로필'
    fields = ('bio', 'profile_image', 'updated_at')
    readonly_fields = ('updated_at',)


class CustomUserAdmin(UserAdmin):
    # Profile Inline 추가
    inlines = [ProfileInline]
    
    # 1. 목록 화면에서 보여줄 컬럼 지정
    list_display = ('username', 'email', 'nickname', 'is_staff', 'is_active', 'deleted_at', 'date_joined')

    # 2. 목록 필터 우측 사이드바 설정
    list_filter = ('is_staff', 'is_active', ('deleted_at', admin.EmptyFieldListFilter), 'groups')

    # 3. 검색창에서 검색할 필드 설정 (핸들, 이메일, 닉네임으로 검색 가능)
    search_fields = ('username', 'email', 'nickname')

    # 4. 정렬 기준 (최신 가입순)
    ordering = ('-date_joined',)

    # 5. 상세 수정 화면(Detail) 구성 재정의
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('개인 정보', {'fields': ('email', 'nickname')}),
        ('권한', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Soft Delete', {'fields': ('deleted_at',)}),
        ('중요 일자', {'fields': ('last_login', 'date_joined', 'updated_at')}),
    )
    
    # 6. 읽기 전용 필드 설정
    readonly_fields = ('date_joined', 'last_login', 'updated_at')

    # 7. 유저 생성 화면(Add User) 구성 재정의
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'nickname', 'password1', 'password2'),
        }),
    )
    
    # 8. Admin 액션: Soft Delete
    @admin.action(description='선택한 사용자 탈퇴 처리')
    def soft_delete_users(self, request, queryset):
        count = 0
        for user in queryset.filter(is_active=True):
            user.soft_delete()
            count += 1
        self.message_user(request, f'{count}명의 사용자를 탈퇴 처리했습니다.')
    
    # 9. Admin 액션: 복구
    @admin.action(description='선택한 사용자 복구')
    def restore_users(self, request, queryset):
        count = 0
        for user in queryset.filter(is_active=False):
            user.restore()
            count += 1
        self.message_user(request, f'{count}명의 사용자를 복구했습니다.')
    
    actions = ['soft_delete_users', 'restore_users']


# Profile Admin: Profile 독립 관리
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio_preview', 'profile_image', 'updated_at')
    search_fields = ('user__username', 'user__email', 'bio')
    readonly_fields = ('updated_at',)
    
    @admin.display(description='자기소개')
    def bio_preview(self, obj):
        if obj.bio:
            return obj.bio[:50] + '...' if len(obj.bio) > 50 else obj.bio
        return '-'


# Follow Admin: 팔로우 관계 관리
@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'following', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'following__username', 'follower__email', 'following__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    # 필드 그룹화
    fieldsets = (
        ('팔로우 관계', {
            'fields': ('follower', 'following')
        }),
        ('메타 정보', {
            'fields': ('created_at',)
        }),
    )


# User 등록
admin.site.register(User, CustomUserAdmin)