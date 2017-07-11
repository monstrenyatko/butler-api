from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance=None, created=False, **kwargs):
    if not created:
        instance.profile.save()
