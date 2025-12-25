from rest_framework import serializers
from django.contrib.auth import get_user_model
from accounts.serializers import ProfileImageMixin
from .models import Review
from movies.models import Movie

User = get_user_model()

class ReviewUserSerializer(ProfileImageMixin, serializers.ModelSerializer):
    """
    리뷰 작성자 정보 (닉네임, 프사 등)
    """
    class Meta:
        model = User
        fields = ('id', 'nickname', 'profile_image_url')     # 'profile_image_url' 

class ReviewSerializer(serializers.ModelSerializer):
    """
    [기본 리뷰 시리얼라이저]
    - R-01, R-02, R-04, R-06
    - like_count 필드명 사용
    - 스포일러 리뷰는 content 마스킹 처리
    """
    user = ReviewUserSerializer(read_only=True)
    
    # [입력] movie_id로 매핑
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(),
        source='movie',
        write_only=True
    )
    
    # [출력] 좋아요 정보 (요청하신 like_count로 적용)
    like_count = serializers.IntegerField(source='likes.count', read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = (
            'id', 
            'user', 
            'movie_id', 
            'content', 
            'rating', 
            'is_spoiler', 
            'like_count',
            'is_liked', 
            'created_at', 
            'updated_at'
        )
        read_only_fields = ('user', 'like_count', 'is_liked', 'created_at', 'updated_at')

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def to_representation(self, instance):
        """
        [R-02 Logic 준수]
        - 스포일러가 true인 경우, content를 마스킹 처리하여 반환합니다.
        """
        ret = super().to_representation(instance)
        
        # 스포일러 체크되어 있으면 내용 가림
        if instance.is_spoiler:
            ret['content'] = '스포일러가 포함된 리뷰입니다. (클릭하여 보기)'
            
        return ret
    
    def validate(self, data):
        """
        [유효성 검사]
        - R-01: 한 유저는 한 영화당 하나의 리뷰만 작성 가능
        """
        # 생성(Create)일 때만 검사 (수정 시에는 본인 글이니까 통과)
        if self.instance is None:
            user = self.context['request'].user
            movie = data.get('movie') # source='movie'로 인해 id가 아닌 객체가 들어옴
            
            if Review.objects.filter(user=user, movie=movie).exists():
                raise serializers.ValidationError("이미 이 영화에 대한 리뷰를 작성했습니다.")
        
        return data


class MovieTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ('id', 'title', 'poster_path', 'release_date')

class MyReviewSerializer(ReviewSerializer):
    """
    [내 리뷰 모아보기용 - R-07]
    - 영화 정보 포함
    - 내가 쓴 글이므로 스포일러라도 내용은 보이게 처리 (Override)
    """
    movie = MovieTitleSerializer(read_only=True)

    class Meta(ReviewSerializer.Meta):
        fields = ReviewSerializer.Meta.fields + ('movie',)

    def to_representation(self, instance):
        """
        내 리뷰 목록(R-07)에서는 내가 쓴 글이니 스포일러 마스킹 없이 
        원본 내용을 그대로 보여줍니다.
        """
        ret = super().to_representation(instance)
        
        # 내가 쓴 글은 마스킹 해제 (원본 덮어쓰기)
        if instance.is_spoiler:
            ret['content'] = instance.content
            
        return ret
