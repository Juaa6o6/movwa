from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import UserMovieLog

@receiver(pre_save, sender=UserMovieLog)
def manage_movie_interaction_hierarchy(sender, instance, **kwargs):
    """
    [기능 설명]
    UserMovieLog 데이터가 저장(save)되기 직전(pre_save)에 실행됩니다.
    사용자가 '평점(rating)'을 입력하거나 수정하면, 
    '보고싶어요(saved)'와 '좋아요(liked)' 상태를 자동으로 해제합니다.
    """
    
    # 1. rating 값 확인
    # 평점이 None이 아니라는 것은, 유저가 별점을 매겼다는 뜻입니다(시청 완료).
    if instance.rating is not None:
        
        # 2. 상태 자동 변경
        # 이미 봤으므로 '보고싶어요' 목록에서 제거
        if instance.is_saved:
            instance.is_saved = False
            
        # 이미 봤으므로 '오늘의 픽(좋아요)' 목록에서 제거
        if instance.is_liked:
            instance.is_liked = False
            
        # (참고) pre_save 시그널이므로 여기서 instance 값을 바꾸면, 
        # 별도의 save() 호출 없이도 변경된 값이 DB에 저장됩니다.