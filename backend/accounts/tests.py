from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from .models import Profile, Follow

User = get_user_model()


class UserModelTest(TestCase):
    """User 모델 테스트"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            username='user1',
            nickname='테스트유저1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@test.com',
            username='user2',
            nickname='테스트유저2',
            password='testpass123'
        )
    
    def test_user_creation(self):
        """사용자 생성 테스트"""
        self.assertEqual(self.user1.email, 'user1@test.com')
        self.assertEqual(self.user1.username, 'user1')
        self.assertEqual(self.user1.nickname, '테스트유저1')
        self.assertTrue(self.user1.is_active)
    
    def test_profile_auto_creation(self):
        """User 생성 시 Profile 자동 생성 테스트 (Signal)"""
        self.assertTrue(hasattr(self.user1, 'profile'))
        self.assertIsInstance(self.user1.profile, Profile)
    
    def test_soft_delete(self):
        """Soft Delete 테스트"""
        self.user1.soft_delete()
        self.assertFalse(self.user1.is_active)
        self.assertIsNotNone(self.user1.deleted_at)
    
    def test_restore(self):
        """탈퇴 복구 테스트"""
        self.user1.soft_delete()
        self.user1.restore()
        self.assertTrue(self.user1.is_active)
        self.assertIsNone(self.user1.deleted_at)


class FollowModelTest(TestCase):
    """Follow 모델 및 팔로우 기능 테스트"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@test.com',
            username='user2',
            password='testpass123'
        )
    
    def test_follow(self):
        """팔로우 테스트"""
        self.user1.follow(self.user2)
        self.assertTrue(self.user1.is_following(self.user2))
        self.assertEqual(self.user1.followings.count(), 1)
        self.assertEqual(self.user2.followers.count(), 1)
    
    def test_unfollow(self):
        """언팔로우 테스트"""
        self.user1.follow(self.user2)
        self.user1.unfollow(self.user2)
        self.assertFalse(self.user1.is_following(self.user2))
        self.assertEqual(self.user1.followings.count(), 0)
    
    def test_toggle_follow(self):
        """팔로우 토글 테스트"""
        # 팔로우
        result = self.user1.toggle_follow(self.user2)
        self.assertTrue(result)
        self.assertTrue(self.user1.is_following(self.user2))
        
        # 언팔로우
        result = self.user1.toggle_follow(self.user2)
        self.assertFalse(result)
        self.assertFalse(self.user1.is_following(self.user2))
    
    def test_self_follow_prevention(self):
        """자기 자신 팔로우 방지 테스트"""
        from django.core.exceptions import ValidationError
        with self.assertRaises(ValidationError):
            self.user1.follow(self.user1)
    
    def test_follow_uniqueness(self):
        """중복 팔로우 방지 테스트"""
        self.user1.follow(self.user2)
        self.user1.follow(self.user2)  # 중복 팔로우 시도
        # get_or_create 사용으로 중복 생성 안됨
        self.assertEqual(Follow.objects.filter(follower=self.user1, following=self.user2).count(), 1)


class ProfileAPITest(APITestCase):
    """프로필 API 테스트"""
    
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            username='user1',
            nickname='테스트유저1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@test.com',
            username='user2',
            nickname='테스트유저2',
            password='testpass123'
        )
    
    def test_current_user_view_authenticated(self):
        """로그인한 사용자 정보 조회 테스트"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('accounts:current-user')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'user1')
        self.assertEqual(response.data['nickname'], '테스트유저1')
    
    def test_current_user_view_unauthenticated(self):
        """비로그인 사용자 정보 조회 실패 테스트"""
        url = reverse('accounts:current-user')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_detail_view(self):
        """타 사용자 프로필 조회 테스트"""
        url = reverse('accounts:user-detail', kwargs={'username': 'user2'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'user2')
        self.assertIn('followers_count', response.data)
        self.assertIn('following_count', response.data)
    
    def test_user_update(self):
        """프로필 수정 테스트"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('accounts:user-update')
        data = {
            'nickname': '변경된닉네임',
            'bio': '자기소개입니다.'
        }
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.nickname, '변경된닉네임')
        self.assertEqual(self.user1.profile.bio, '자기소개입니다.')
    
    def test_user_update_unauthenticated(self):
        """비로그인 프로필 수정 실패 테스트"""
        url = reverse('accounts:user-update')
        data = {'nickname': '변경시도'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_delete(self):
        """회원 탈퇴 테스트"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('accounts:user-delete')
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertFalse(self.user1.is_active)
        self.assertIsNotNone(self.user1.deleted_at)


class FollowAPITest(APITestCase):
    """팔로우 API 테스트"""
    
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email='user1@test.com',
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            email='user2@test.com',
            username='user2',
            password='testpass123'
        )
        self.user3 = User.objects.create_user(
            email='user3@test.com',
            username='user3',
            password='testpass123'
        )
    
    def test_follow_toggle_follow(self):
        """팔로우 토글 - 팔로우 테스트"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('accounts:follow-toggle', kwargs={'username': 'user2'})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_following'])
        self.assertEqual(response.data['followers_count'], 1)
    
    def test_follow_toggle_unfollow(self):
        """팔로우 토글 - 언팔로우 테스트"""
        self.client.force_authenticate(user=self.user1)
        self.user1.follow(self.user2)
        
        url = reverse('accounts:follow-toggle', kwargs={'username': 'user2'})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_following'])
        self.assertEqual(response.data['followers_count'], 0)
    
    def test_follow_self_prevention(self):
        """자기 자신 팔로우 방지 테스트"""
        self.client.force_authenticate(user=self.user1)
        url = reverse('accounts:follow-toggle', kwargs={'username': 'user1'})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('본인을 팔로우할 수 없습니다', response.data['detail'])
    
    def test_follow_unauthenticated(self):
        """비로그인 팔로우 실패 테스트"""
        url = reverse('accounts:follow-toggle', kwargs={'username': 'user2'})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_followers_list(self):
        """팔로워 목록 조회 테스트"""
        self.user1.follow(self.user2)
        self.user3.follow(self.user2)
        
        url = reverse('accounts:followers-list', kwargs={'username': 'user2'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_followings_list(self):
        """팔로잉 목록 조회 테스트"""
        self.user1.follow(self.user2)
        self.user1.follow(self.user3)
        
        url = reverse('accounts:followings-list', kwargs={'username': 'user1'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_is_following_field(self):
        """is_following 필드 정확성 테스트"""
        self.client.force_authenticate(user=self.user1)
        self.user1.follow(self.user2)
        
        # user2 프로필 조회 시 is_following=True
        url = reverse('accounts:user-detail', kwargs={'username': 'user2'})
        response = self.client.get(url)
        self.assertTrue(response.data['is_following'])
        
        # user3 프로필 조회 시 is_following=False
        url = reverse('accounts:user-detail', kwargs={'username': 'user3'})
        response = self.client.get(url)
        self.assertFalse(response.data['is_following'])
