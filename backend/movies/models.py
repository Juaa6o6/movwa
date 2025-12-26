import uuid
from django.db import models
from django.conf import settings

class Genre(models.Model):
    # [DB 명세] TMDB의 장르 ID를 그대로 PK로 사용 (Auto Inc 아님)
    id = models.IntegerField(primary_key=True) 
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Movie(models.Model):
    # [DB 명세] 식별자
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # 내부 식별용 UUID
    tmdb_id = models.BigIntegerField(unique=True, null=True, blank=True) # 외부 API ID (Sync용)
    
    # [DB 명세] 기본 정보
    title = models.CharField(max_length=200) # 한국어 제목
    original_title = models.CharField(max_length=200, null=True, blank=True) # 원제
    overview = models.TextField(null=True, blank=True) # 줄거리
    release_date = models.DateField(null=True, blank=True) # 개봉일
    runtime = models.IntegerField(null=True, blank=True) # 상영 시간 (분)
    status = models.CharField(max_length=50, default='Released') # 개봉 상태
    tagline = models.CharField(max_length=300, null=True, blank=True) # 한줄 카피
    
    # [DB 명세] 미디어 및 메타데이터
    poster_path = models.CharField(max_length=200, null=True, blank=True) # 포스터 경로
    backdrop_path = models.CharField(max_length=200, null=True, blank=True) # 배경 경로
    youtube_key = models.CharField(max_length=100, null=True, blank=True) # 예고편 키
    
    # [DB 명세] 지표 및 필터링
    popularity = models.FloatField(default=0.0) # 인기도 (정렬 기준)
    vote_average = models.FloatField(default=0.0) # 평점 (TMDB 기준)
    vote_count = models.IntegerField(default=0) # 평점 수
    adult = models.BooleanField(default=False) # 성인 여부
    original_language = models.CharField(max_length=10, default='en') # 원어 코드

    # [DB 명세] 출연진 (JSON)
    credits = models.JSONField(null=True, blank=True) # 감독/출연진 데이터 통째로 저장

    # 관계 설정
    genres = models.ManyToManyField(Genre, related_name='movies') # movie_genres 테이블 자동 생성됨

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# [DB 명세] 유저 활동 로그 (좋아요, 찜, 평점 통합 테이블)
class UserMovieLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='movie_logs')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='user_logs')
    
    # 틴더 스타일 Swipe (Like/Pass)
    is_liked = models.BooleanField(null=True, blank=True) # True: Like, False: Pass, Null: 무응답
    
    # 북마크 (나중에 볼 영화)
    is_saved = models.BooleanField(default=False) # True: 찜함
    
    # 평점 (Review)
    rating = models.FloatField(null=True, blank=True) # 0.5 ~ 5.0 -> 시리얼라이즈에서 검증 처리

    created_at = models.DateTimeField(auto_now_add=True) # 최초 생성 (장기 취향)
    updated_at = models.DateTimeField(auto_now=True) # 최근 수정 (단기 추천 가중치)

    class Meta:
        constraints = [
            # 유저당 영화 하나에는 하나의 로그만 존재해야 함
            models.UniqueConstraint(fields=['user', 'movie'], name='unique_user_movie_log')
        ]

# [DB 명세] AI 추천 결과 저장
class UserMovieRecommend(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='movie_recommends')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='recommended_users')
    
    score = models.FloatField() # AI 예측 점수
    rank = models.IntegerField() # 노출 순위
    algo_type = models.CharField(max_length=50, default='default') # 추천 알고리즘 버전 (A/B 테스트용)
    
    created_at = models.DateTimeField(auto_now_add=True) # 생성 시간 (유효기간 체크)

    class Meta:
        ordering = ['rank'] # 순위 순 정렬
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'movie', 'algo_type'],
                name='unique_user_movie_algo_recommend'
            )
        ]


# [DB 명세] 박스오피스 순위 (KOBIS API 연동)


class MovieEmbedding(models.Model):
    movie = models.OneToOneField(
        Movie,
        on_delete=models.CASCADE,
        related_name='embedding',
        primary_key=True,
    )
    vector = models.JSONField()
    model_version = models.CharField(max_length=50, default='text-embedding-3-small')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Embedding for {self.movie.title}"


class BoxOfficeRank(models.Model):
    RANK_TYPE_CHOICES = [
        ('daily', '일간'),
        ('weekly', '주간'),
    ]
    
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='boxoffice_ranks')
    rank = models.IntegerField() # 순위 (1, 2, 3, ...)
    rank_type = models.CharField(max_length=20, choices=RANK_TYPE_CHOICES, default='daily') # 순위 타입
    date = models.DateField() # 기준일 (일간: 해당일, 주간: 주 시작일)
    
    # KOBIS 추가 정보
    audience_count = models.IntegerField(default=0) # 관객 수
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'rank'] # 날짜, 순위 순 정렬
        constraints = [
            models.UniqueConstraint(
                fields=['movie', 'rank_type', 'date'],
                name='unique_movie_rank_type_date'
            )
        ]
        indexes = [
            models.Index(fields=['rank_type', 'date', 'rank']), # 조회 최적화
        ]
    
    def __str__(self):
        return f"{self.date} {self.get_rank_type_display()} {self.rank}위 - {self.movie.title}"