from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps
from .models import Review

# 시나리오 A: 리뷰(Review) 저장 시 로그(UserMovieLog) 업데이트
@receiver(post_save, sender=Review)
def sync_review_to_log(sender, instance, created, **kwargs):
    """
    [평점 동기화 로직]
    Review -> UserMovieLog 방향
    """
    # 1. 리뷰에 평점이 있는 경우에만 동작
    if instance.rating is not None:
        UserMovieLog = apps.get_model('movies', 'UserMovieLog')
        
        # 2. UserMovieLog 가져오기 (없으면 생성)
        log, _ = UserMovieLog.objects.get_or_create(
            user=instance.user,
            movie=instance.movie
        )
        
        # 평점 업데이트 - 값이 다를 때만 저장하여 무한 루프 방지
        if log.rating != instance.rating:
            log.rating = instance.rating
            log.save()

# 시나리오 B: 로그(UserMovieLog) 저장 시 리뷰(Review) 업데이트
@receiver(post_save, sender=apps.get_model('movies', 'UserMovieLog'))
def sync_log_to_review(sender, instance, created, **kwargs):
    """
    [반대 방향 동기화]
    UserMovieLog의 평점이 변경되면 -> 작성했던 Review의 평점도 같이 수정한다.
    (단, 리뷰가 이미 존재하는 경우에만)
    """
    if instance.rating is not None:
        Review = apps.get_model('reviews', 'Review')
        
        # 2. 해당 영화에 쓴 리뷰 찾기
        review = Review.objects.filter(user=instance.user, movie=instance.movie).first()
        
        # 리뷰가 존재하고 평점이 다를 때만 업데이트
        if review and review.rating != instance.rating:
            review.rating = instance.rating
            review.save()