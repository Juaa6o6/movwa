from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps
from .models import Review

@receiver(post_save, sender=Review)
def sync_rating_to_movie_log(sender, instance, created, **kwargs):
    """
    [평점 동기화 로직]
    Review -> UserMovieLog 방향
    """
    # 1. 리뷰에 평점이 있는 경우에만 동작
    if instance.rating is not None:

        # [수정] apps.get_model로 모델 가져오기 (순환 참조 원천 차단)
        UserMovieLog = apps.get_model('movies', 'UserMovieLog')

        # 2. UserMovieLog 가져오기 (없으면 생성)
        log, _ = UserMovieLog.objects.get_or_create(
            user=instance.user,
            movie=instance.movie
        )
        
        # 3. 평점 업데이트
        # 주의: 여기서 log.save() 호출 -> movies/signals.py 동작 -> 찜/좋아요 해제
        if log.rating != instance.rating:
            log.rating = instance.rating
            log.save() 
            # print(f"[Sync] Review {instance.id} rating updated -> Log synced.")