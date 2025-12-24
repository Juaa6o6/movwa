from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from movies.models import Movie  # 영화 정보 연결

class Review(models.Model):
    """
    영화 리뷰 모델
    - 사용자는 영화에 대해 텍스트 리뷰와 평점을 남길 수 있습니다.
    - 리뷰 작성 시 평점(rating)은 필수입니다.
    - 리뷰가 저장되면 Signal을 통해 UserMovieLog의 평점도 업데이트됩니다.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='reviews',
        verbose_name="작성자"
    )
    movie = models.ForeignKey(
        Movie, 
        on_delete=models.CASCADE, 
        related_name='reviews',
        verbose_name="영화"
    )
    content = models.TextField(verbose_name="리뷰 내용")
    
    # 평점: 0.5 ~ 5.0 범위 제한
    rating = models.FloatField(
        verbose_name="평점",
        null=False,   # DB에 NULL 저장 불가
        blank=False,  # 입력 폼에서도 필수
        validators=[
            MinValueValidator(0.5),
            MaxValueValidator(5.0)
        ],
        help_text="평점 (필수 항목, 0.5~5.0)"
    )
    
    is_spoiler = models.BooleanField(
        default=False, 
        verbose_name="스포일러 여부"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="작성일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']  # 최신순 기본 정렬
        verbose_name = '리뷰'
        verbose_name_plural = '리뷰 목록'

    def __str__(self):
        return f"{self.user} - {self.movie.title} Review"


class ReviewLike(models.Model):
    """
    리뷰 좋아요 모델 (Toggle 기능용)
    - 사용자가 특정 리뷰에 '좋아요'를 누른 기록
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='review_likes'
    )
    review = models.ForeignKey(
        Review, 
        on_delete=models.CASCADE, 
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_review_likes'
        unique_together = ('user', 'review')  # 한 리뷰에 중복 좋아요 방지
        verbose_name = '리뷰 좋아요'
        verbose_name_plural = '리뷰 좋아요 목록'
    
    def __str__(self):
        return f"{self.user} likes review {self.review.id}"