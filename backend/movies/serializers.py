from rest_framework import serializers
from .models import Movie, Genre, UserMovieLog, BoxOfficeRank


# YouTube 관련 영상 Serializer
class YouTubeVideoSerializer(serializers.Serializer):
    """
    YouTube 영상 데이터 직렬화
    
    youtube_api.py의 fetch_youtube_videos() 반환값을 API 응답으로 변환
    """
    video_id = serializers.CharField()
    title = serializers.CharField()
    thumbnail = serializers.URLField()
    url = serializers.SerializerMethodField()  # video_id → YouTube URL 변환
    channel_title = serializers.CharField()
    published_at = serializers.CharField()
    description = serializers.CharField()
    query_type = serializers.CharField()  # review, trailer
    
    def get_url(self, obj):
        """
        video_id를 YouTube URL로 변환
        예: 'abc123' → 'https://www.youtube.com/watch?v=abc123'
        """
        video_id = obj.get('video_id')
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"
        return None


class MovieListSerializer(serializers.ModelSerializer):
    # 장르: ID 대신 ["Action", "Romance"] 형태로 변환
    genres = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = Movie
        fields = [
            'id', 
            'title', 
            'poster_path', 
            'backdrop_path',
            'youtube_key',
            'vote_average', 
            'release_date', 
            'original_language',  # 국가/언어 정보 (예: 'en', 'ko')
            'genres',             # 장르 목록 (예: ['Action', 'Comedy'])
            'runtime',            # [추가] 상영 시간 (분 단위, 예: 120)
        ]


class MovieDetailSerializer(serializers.ModelSerializer):
    # 장르: ID 대신 ["Action", "Romance"] 형태로 변환
    genres = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = Movie
        fields = '__all__'      # 모든 필드 포함 (줄거리, 크레딧, 예고편 등 포함)

# Like/Pass (Action)
class MovieLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMovieLog
        fields = ['is_liked']

# 나중에 볼 영화(SAVE)
class MovieSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMovieLog
        fields = ['is_saved']

# 평점 등록/수정 (Rate)
class MovieRateSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField(min_value=0.5, max_value=5.0)

    class Meta:
        model = UserMovieLog
        fields = ['rating']

    # 0.5 단위 검증 로직
    def validate_rating(self, value):
        # 2를 곱했을 때 정수가 아니면 0.5 단위가 아님 (예: 4.3 -> 8.6)
        if (value * 2) % 1 != 0:
            raise serializers.ValidationError("평점은 0.5 단위로 입력해야 합니다.")
        return value

# 공통 Response용 (필요 시 전체 로그 반환)
class UserMovieLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMovieLog
        fields = ['id', 'user', 'movie', 'is_liked', 'is_saved', 'rating', 'updated_at', 'created_at']
        read_only_fields = ['user', 'movie']

class UserMovieLogBriefSerializer(serializers.ModelSerializer):
    movie_id = serializers.UUIDField(source='movie.id')

    class Meta:
        model = UserMovieLog
        fields = ['movie_id', 'is_liked', 'is_saved', 'rating']

class UserMovieLogCalendarSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)

    class Meta:
        model = UserMovieLog
        fields = ['movie', 'rating', 'updated_at']


# 박스오피스 순위 (영화 정보 포함)
class BoxOfficeRankSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)  # 영화 상세 정보 포함
    rank_type_display = serializers.CharField(source='get_rank_type_display', read_only=True)  # '일간' or '주간'
    
    class Meta:
        model = BoxOfficeRank
        fields = [
            'id',
            'movie',
            'rank',
            'rank_type',
            'rank_type_display',
            'date',
            'audience_count',
        ]
