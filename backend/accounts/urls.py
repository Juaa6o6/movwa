from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # U-08: 현재 로그인한 사용자 정보 조회
    path('me/', views.CurrentUserView.as_view(), name='current-user'),
    
    # U-09: 회원 탈퇴 (Soft Delete)
    path('me/delete/', views.UserDeleteView.as_view(), name='user-delete'),
    
    # U-10: 프로필 수정 (PATCH)
    path('me/update/', views.UserUpdateView.as_view(), name='user-update'),
    
    # U-11: 특정 사용자 프로필 조회
    path('<str:username>/', views.UserDetailView.as_view(), name='user-detail'),
    
    # U-12: 팔로우 토글
    path('<str:username>/follow/', views.follow_toggle, name='follow-toggle'),
    
    # U-13: 팔로워 목록 조회
    path('<str:username>/followers/', views.FollowersListView.as_view(), name='followers-list'),
    
    # U-14: 팔로잉 목록 조회
    path('<str:username>/followings/', views.FollowingsListView.as_view(), name='followings-list'),
]