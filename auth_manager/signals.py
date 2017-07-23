from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from rest_framework.authtoken.models import Token
from . import models as local_models


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        local_models.UserProfileModel.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_token(sender, instance, created, **kwargs):
    if created:
        Token.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, created, **kwargs):
    if not created:
        instance.profile.save()
