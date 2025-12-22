"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    # 로그인, 로그아웃, 비밀번호 변경 등 (dj-rest-auth 라이브러리)
    path('api/v1/auth/', include('dj_rest_auth.urls')),

    # 회원가입 (dj-rest-auth + allauth 라이브러리)
    path('api/v1/auth/registration/', include('dj_rest_auth.registration.urls')),

    #  accounts 앱의 커스텀 기능 연결 - '프로필 조회', '정보 수정' 등은 이쪽으로 보냅니다.
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/movies/', include('movies.urls')),
    
    # 1. 스키마 다운로드 (YAML 파일)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # 2. Swagger UI (가장 많이 사용)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # 3. Redoc (다른 스타일의 문서)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]