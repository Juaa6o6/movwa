from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from movies.models import Movie
from .models import Review, ReviewLike

User = get_user_model()

class ReviewAppTestCase(APITestCase):
    def setUp(self):
        """테스트 전 사전 데이터 생성"""
        # 1. 유저 2명 생성 (작성자, 타인)
        self.user = User.objects.create_user(
            username='tester', 
            email='tester@test.com', 
            password='password123'
        )
        self.other_user = User.objects.create_user(
            username='other', 
            email='other@test.com', 
            password='password123'
        )
        
        # 2. 영화 생성
        self.movie = Movie.objects.create(
            title="테스트 무비",
            release_date="2025-01-01",
            overview="재밌는 영화",
            poster_path="path/to/poster.jpg"
        )
        
        # 3. URL 별칭 정의
        self.list_url = reverse('reviews:review-list')  # /api/v1/reviews/
        
        # 기본적으로 user로 로그인
        self.client.force_authenticate(user=self.user)

    # ----------------------------------------------------------------
    # R-01: 리뷰 작성 (Create)
    # ----------------------------------------------------------------
    def test_create_review_success(self):
        """[R-01] 리뷰 작성 성공 및 데이터 검증"""
        data = {
            "movie_id": self.movie.id,
            "content": "최고의 영화!",
            "rating": 5.0,
            "is_spoiler": False
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.get().user, self.user)

    def test_create_duplicate_review_fail(self):
        """[R-01 예외] 1인 1영화 1리뷰 제한 검증"""
        # 1. 첫 번째 리뷰 작성
        Review.objects.create(user=self.user, movie=self.movie, content="1", rating=5.0)
        
        # 2. 같은 영화에 두 번째 리뷰 시도
        data = {
            "movie_id": self.movie.id,
            "content": "중복 작성 시도",
            "rating": 1.0,
            "is_spoiler": False
        }
        response = self.client.post(self.list_url, data)
        
        # 3. 400 Bad Request 확인
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("이미 이 영화에 대한 리뷰를 작성했습니다", str(response.data))

    # ----------------------------------------------------------------
    # R-02: 리뷰 목록 조회 (List) - 정렬 & 마스킹
    # ----------------------------------------------------------------
    def test_list_default_ordering_best(self):
        """[R-02] 기본 정렬이 인기순(좋아요순)인지 검증"""
        # 리뷰 2개 생성
        review1 = Review.objects.create(user=self.user, movie=self.movie, content="1", rating=1.0)
        review2 = Review.objects.create(user=self.other_user, movie=self.movie, content="2", rating=5.0)
        
        # review2에 좋아요 1개 추가
        ReviewLike.objects.create(user=self.user, review=review2)

        # 조회
        response = self.client.get(self.list_url)
        
        # 검증: 좋아요가 많은 review2가 첫 번째로 나와야 함
        # [수정] 페이징 여부에 따른 데이터 추출 로직 적용
        if isinstance(response.data, dict) and 'results' in response.data:
            data = response.data['results']
        else:
            data = response.data
        
        # 검증: 좋아요가 많은 review2가 첫 번째, 최신인 review1이 두 번째 (또는 좋아요 0개 중 최신순)
        self.assertEqual(data[0]['id'], review2.id)
        self.assertEqual(data[1]['id'], review1.id)

    def test_spoiler_masking_in_list(self):
        """[R-02] 스포일러 리뷰 목록 조회 시 마스킹 처리 검증"""
        Review.objects.create(
            user=self.other_user, 
            movie=self.movie, 
            content="범인은 절름발이", 
            rating=5.0, 
            is_spoiler=True
        )
        
        response = self.client.get(self.list_url)
        # [수정] 페이징 여부에 따른 데이터 추출 로직
        if isinstance(response.data, dict) and 'results' in response.data:
            content = response.data['results'][0]['content']
        else:
            content = response.data[0]['content']
        
        # 원본 내용이 아니라 안내 문구가 나와야 함
        self.assertNotEqual(content, "범인은 절름발이")
        self.assertIn("스포일러가 포함된 리뷰입니다", content)

    # ----------------------------------------------------------------
    # R-04: 리뷰 수정 (Update) - PATCH Only
    # ----------------------------------------------------------------
    def test_update_patch_success(self):
        """[R-04] 본인 리뷰 PATCH 수정 성공"""
        review = Review.objects.create(user=self.user, movie=self.movie, content="구림", rating=1.0)
        url = reverse('reviews:review-detail', args=[review.id])
        
        data = {"content": "생각해보니 좋음", "rating": 4.0}
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        review.refresh_from_db()
        self.assertEqual(review.content, "생각해보니 좋음")
        self.assertEqual(review.rating, 4.0)

    def test_update_put_not_allowed(self):
        """[R-04 예외] PUT 메서드 차단 확인 (405 Error)"""
        review = Review.objects.create(user=self.user, movie=self.movie, content="A", rating=1.0)
        url = reverse('reviews:review-detail', args=[review.id])
        
        data = {"movie_id": self.movie.id, "content": "B", "rating": 2.0, "is_spoiler": False}
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_permission_denied(self):
        """[R-04 예외] 남의 리뷰 수정 시도 시 차단"""
        # other_user가 쓴 리뷰
        review = Review.objects.create(user=self.other_user, movie=self.movie, content="A", rating=1.0)
        url = reverse('reviews:review-detail', args=[review.id])
        
        # 현재 self.user(tester)로 로그인 중
        response = self.client.patch(url, {"content": "해킹"})
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ----------------------------------------------------------------
    # R-05: 리뷰 삭제 (Delete)
    # ----------------------------------------------------------------
    def test_delete_success(self):
        """[R-05] 본인 리뷰 삭제 성공"""
        review = Review.objects.create(user=self.user, movie=self.movie, content="삭제할거", rating=1.0)
        url = reverse('reviews:review-detail', args=[review.id])
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=review.id).exists())

    # ----------------------------------------------------------------
    # R-06: 좋아요 (Like)
    # ----------------------------------------------------------------
    def test_like_toggle(self):
        """[R-06] 좋아요 토글 기능 (생성 -> 삭제)"""
        review = Review.objects.create(user=self.other_user, movie=self.movie, content="굿", rating=5.0)
        url = reverse('reviews:review-like', args=[review.id])

        # 1. 좋아요 누름 (생성)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_liked'])
        self.assertEqual(response.data['like_count'], 1)

        # 2. 다시 누름 (취소)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_liked'])
        self.assertEqual(response.data['like_count'], 0)

    # ----------------------------------------------------------------
    # R-07: 내 리뷰 (Me)
    # ----------------------------------------------------------------
    def test_my_review_list_structure(self):
        """[R-07] 내 리뷰 조회 시 영화 정보 포함 및 마스킹 해제 확인"""
        # 스포일러 리뷰 작성
        Review.objects.create(
            user=self.user, 
            movie=self.movie, 
            content="내 스포일러", 
            rating=5.0, 
            is_spoiler=True
        )
        
        url = reverse('reviews:review-me') # /api/v1/reviews/me/
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        if isinstance(response.data, dict) and 'results' in response.data:
            result = response.data['results'][0]
        else:
            result = response.data[0]
        
        # 1. 영화 정보가 객체(dict)로 들어있는지 확인
        self.assertIsInstance(result['movie'], dict)
        self.assertEqual(result['movie']['title'], "테스트 무비")
        
        # 2. 내가 쓴 글은 스포일러여도 원본이 보여야 함
        self.assertEqual(result['content'], "내 스포일러")

    # ----------------------------------------------------------------
    # R-08: 스포일러 내용 조회 (Content)
    # ----------------------------------------------------------------
    def test_spoiler_content_detail(self):
        """[R-08] 스포일러 원본 내용 조회 Action 확인"""
        review = Review.objects.create(
            user=self.other_user, 
            movie=self.movie, 
            content="진짜 내용", 
            rating=5.0, 
            is_spoiler=True
        )
        
        url = reverse('reviews:review-content', args=[review.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], "진짜 내용")