from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from django.contrib.auth import get_user_model
from .models import Movie, UserMovieLog
from django.test import TestCase

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


class MovieInteractionSignalTest(TestCase):
    def setUp(self):
        # 1. 테스트를 위한 기초 데이터 생성 (유저, 영화)
        self.user = User.objects.create_user(username='testuser', password='password')
        self.movie = Movie.objects.create(
            tmdb_id=12345,
            title="테스트 영화",
            original_title="Test Movie",
            # 필요한 필수 필드가 더 있다면 여기에 추가하세요
        )

    def test_rate_existing_saved_movie(self):
        """
        시나리오 1: 이미 '보고싶어요(Saved)' 상태인 영화에 
        나중에 평점을 매기면, Saved가 자동으로 False로 변해야 한다.
        """
        # Given: 유저가 영화를 찜해둠
        log = UserMovieLog.objects.create(
            user=self.user, 
            movie=self.movie, 
            is_saved=True, 
            rating=None
        )
        self.assertTrue(log.is_saved)  # 저장 잘 됐는지 확인

        # When: 평점 4.5점을 부여 (Update)
        log.rating = 4.5
        log.save() 

        # Then: 다시 DB에서 불러왔을 때 is_saved가 꺼져있어야 함
        log.refresh_from_db() # DB의 최신 값을 다시 가져옴 (필수!)
        self.assertEqual(log.rating, 4.5)
        self.assertFalse(log.is_saved, "평점을 매겼는데 is_saved가 꺼지지 않았습니다.")

    def test_rate_existing_liked_movie(self):
        """
        시나리오 2: '좋아요(Liked)' 상태인 영화에
        평점을 매기면, Liked가 자동으로 False로 변해야 한다.
        """
        # Given: 유저가 좋아요를 누름
        log = UserMovieLog.objects.create(
            user=self.user, 
            movie=self.movie, 
            is_liked=True, 
            rating=None
        )

        # When: 평점 등록
        log.rating = 3.0
        log.save()

        # Then: Liked 해제 확인
        log.refresh_from_db()
        self.assertFalse(log.is_liked, "평점을 매겼는데 is_liked가 꺼지지 않았습니다.")

    def test_create_log_with_rating_immediately(self):
        """
        시나리오 3: 로그를 처음 생성할 때부터 평점과 찜을 동시에 넣으려 하면
        (로직상 그럴 일은 적겠지만) 저장은 평점만 되고 찜은 꺼져야 한다.
        """
        # When: 생성 시점에 is_saved=True, rating=5.0을 동시에 줌
        log = UserMovieLog.objects.create(
            user=self.user,
            movie=self.movie,
            is_saved=True,  # 찜 시도
            is_liked=True,  # 좋아요 시도
            rating=5.0      # 평점
        )

        # Then: Signal에 의해 저장 직전에 False로 바뀌어 있어야 함
        log.refresh_from_db()
        self.assertFalse(log.is_saved)
        self.assertFalse(log.is_liked)
        self.assertEqual(log.rating, 5.0)

    def test_undo_rating_does_not_restore_saved(self):
        """
        시나리오 4: 평점을 줬다가 취소(None)했을 때,
        과거의 찜 상태(True)가 되살아나지 않고 둘 다 False(초기화) 상태여야 한다.
        """
        # 1. 찜 상태로 시작
        log = UserMovieLog.objects.create(user=self.user, movie=self.movie, is_saved=True)
        
        # 2. 평점 부여 -> 찜 해제됨
        log.rating = 4.0
        log.save()
        log.refresh_from_db()
        self.assertFalse(log.is_saved) # 확인 사살

        # 3. 평점 취소 (실수였다!)
        log.rating = None
        log.save()
        
        # 4. 결과 확인: 찜이 되살아나지 않고 깔끔한 상태여야 함
        log.refresh_from_db()
        self.assertIsNone(log.rating)
        self.assertFalse(log.is_saved, "평점을 지웠는데 찜이 되살아났습니다(의도치 않은 동작).")