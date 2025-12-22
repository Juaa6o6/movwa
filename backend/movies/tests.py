from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Movie, UserMovieLog

User = get_user_model()

class MovieInteractionTestCase(APITestCase):
    def setUp(self):
        # 1. 테스트용 유저 생성 (수정된 부분: username 추가)
        # 이메일 로그인을 쓰더라도 create_user 메서드는 username을 요구할 수 있습니다.
        self.user = User.objects.create_user(
            username='testuser',  # <--- 여기 추가!
            email='test@example.com', 
            password='password123'
        )
        
        # 2. 테스트용 영화 생성
        self.movie = Movie.objects.create(
            title="테스트 영화",
            original_title="Test Movie",
            release_date="2024-01-01",
            popularity=10.0,
            vote_average=8.5,
            vote_count=100
        )
        
        # 3. 강제 로그인 (토큰 발급 과정 생략하고 인증 상태로 만듦)
        self.client.force_authenticate(user=self.user)

        # URL 설정 (namespace: 'movies' 사용)
        self.like_url = reverse('movies:movie-like', kwargs={'pk': self.movie.pk})
        self.save_url = reverse('movies:movie-save', kwargs={'pk': self.movie.pk})
        self.rate_url = reverse('movies:movie-rate', kwargs={'pk': self.movie.pk})

    def test_like_movie(self):
        """좋아요 기능 테스트"""
        data = {'is_liked': True}
        response = self.client.post(self.like_url, data)
        
        # 1. 상태 코드가 200인지 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 2. DB에 진짜 저장됐는지 확인
        self.assertTrue(UserMovieLog.objects.get(user=self.user, movie=self.movie).is_liked)

    def test_save_movie(self):
        """찜하기 기능 테스트"""
        data = {'is_saved': True}
        response = self.client.post(self.save_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(UserMovieLog.objects.get(user=self.user, movie=self.movie).is_saved)

    def test_rate_movie_create_and_update(self):
        """평점 등록 및 수정 테스트"""
        # 1. 평점 등록 (4.5)
        data = {'rating': 4.5}
        response = self.client.post(self.rate_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UserMovieLog.objects.get(user=self.user, movie=self.movie).rating, 4.5)

        # 2. 평점 수정 (3.0) - 같은 API로 덮어쓰기 되는지 확인
        data_update = {'rating': 3.0}
        response = self.client.post(self.rate_url, data_update)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(UserMovieLog.objects.get(user=self.user, movie=self.movie).rating, 3.0)

    def test_rate_validation(self):
        """평점 0.5 단위 검증 테스트"""
        # 잘못된 데이터 (4.3점)
        data = {'rating': 4.3}
        response = self.client.post(self.rate_url, data)
        
        # 400 Bad Request가 떠야 함
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_rate(self):
        """평점 삭제(Soft Delete) 테스트"""
        # 먼저 평점 등록
        UserMovieLog.objects.create(user=self.user, movie=self.movie, rating=4.0)

        # 삭제 요청
        response = self.client.delete(self.rate_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # DB 확인: 레코드는 살아있되, rating만 None이어야 함
        log = UserMovieLog.objects.get(user=self.user, movie=self.movie)
        self.assertIsNone(log.rating)


class SpecBasedTodaysPickTestCase(APITestCase):
    def setUp(self):
        # 유저 및 기본 설정
        self.user = User.objects.create_user(username='tester', email='test@test.com', password='pw')
        self.client.force_authenticate(user=self.user)
        
        # 영화 2개 생성
        self.movie_old = Movie.objects.create(title="오래된 영화", original_title="Old", release_date="2000-01-01")
        self.movie_new = Movie.objects.create(title="최신 영화", original_title="New", release_date="2024-01-01")
        
        self.url = reverse('movies:todays-pick')

    def test_rec_09_24h_filtering_and_sorting(self):
        """
        [REC-09] 명세 검증
        1. 24시간 이내 좋아요 영화만 노출되는가?
        2. 최신순으로 정렬되는가?
        """
        now = timezone.now()

        # [상황 1] 25시간 전 좋아요 (명세서상 노출되면 안 됨)
        log_old = UserMovieLog.objects.create(user=self.user, movie=self.movie_old, is_liked=True)
        # 강제로 시간 조작 (DB 업데이트)
        UserMovieLog.objects.filter(pk=log_old.pk).update(updated_at=now - timedelta(hours=25))

        # [상황 2] 1시간 전 좋아요 (명세서상 노출되어야 함)
        log_new = UserMovieLog.objects.create(user=self.user, movie=self.movie_new, is_liked=True)
        UserMovieLog.objects.filter(pk=log_new.pk).update(updated_at=now - timedelta(hours=1))

        # [검증 실행]
        response = self.client.get(self.url)
        
        # 1. 상태 코드 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2. 개수 검증: 2개를 넣었지만, 24시간 이내인 '1개'만 나와야 함
        self.assertEqual(len(response.data), 1, "SRS [REC-09] 위반: 24시간 지난 영화가 조회됨")

        # 3. 데이터 검증: 조회된 영화가 '최신 영화'인가?
        self.assertEqual(response.data[0]['title'], "최신 영화")
        
        print("\n✅ [REC-09] 24시간 필터링 및 정렬 테스트 통과")