from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.apps import apps
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


@receiver(post_save, sender=UserMovieLog)
def sync_movie_log_to_review(sender, instance, created, **kwargs):
    """
    [반대 방향 동기화]
    UserMovieLog의 평점이 변경되면 -> 작성했던 Review의 평점도 같이 수정한다.
    (단, 리뷰가 이미 존재하는 경우에만)
    """
    # 1. 평점이 있는 경우에만 로직 수행
    if instance.rating is not None:
        
        # [Import 주의] 순환 참조 방지를 위해 함수 내부에서 import
        Review = apps.get_model('reviews', 'Review')
        
        # 2. 해당 영화에 쓴 리뷰 찾기
        review = Review.objects.filter(user=instance.user, movie=instance.movie).first()
        
        # review가 존재하면 (None이 아니면) 실행
        # 3. 평점이 다를 때만 업데이트 (무한 루프 방지 핵심!)
        # Review가 업데이트되면 -> Review Signal 발동 -> Log 업데이트 -> Log Signal 발동...
        # 이 고리를 끊기 위해 '값이 다를 때만' 저장하도록 합니다.
        if review:
            if review.rating != instance.rating:
                review.rating = instance.rating
                review.save()
            # print(f"[Sync] Log updated -> Review {review.id} rating synced.")