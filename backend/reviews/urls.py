from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'reviews'

router = DefaultRouter()
router.register(r'', views.ReviewViewSet) # /api/v1/reviews/ 로 매핑됨

urlpatterns = [
    path('', include(router.urls)),
]