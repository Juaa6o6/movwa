from rest_framework import serializers
from .models import Movie, Genre


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
            'vote_average', 
            'release_date', 
            'original_language',  # 국가/언어 정보 (예: 'en', 'ko')
            'genres',             # 장르 목록 (예: ['Action', 'Comedy'])
            'runtime',            # [추가] 상영 시간 (분 단위, 예: 120)
        ]