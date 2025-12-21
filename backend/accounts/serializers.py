from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import UserDetailsSerializer

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
