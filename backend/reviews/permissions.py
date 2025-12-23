from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    - 조회(GET, HEAD, OPTIONS)는 누구나 가능
    - 쓰기(PUT, PATCH, DELETE)는 작성자(Owner)만 가능
    """
    def has_object_permission(self, request, view, obj):
        # 읽기 권한은 모두에게 허용
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 쓰기 권한은 작성자에게만 허용
        return obj.user == request.user