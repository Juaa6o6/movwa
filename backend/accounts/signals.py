from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """User 생성 시 자동으로 Profile 생성"""

    if created:  # 새로 생성된 경우만
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """User 저장 시 Profile도 함께 저장"""

    # hasattr -> User 객체가 profile 속성을 가지고 있는지 검사
    if hasattr(instance, 'profile'):
        instance.profile.save()