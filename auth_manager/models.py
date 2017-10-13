from django.conf import settings
from django.db import models


class UserProfileModel(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='profile',
        on_delete=models.CASCADE
    )
    is_device = models.BooleanField(default=False)
    is_auth_retrieved = models.BooleanField(default=False)

    class Meta:
        db_table = 'user_profile'
        verbose_name = 'user profile'
        verbose_name_plural = 'user profiles'

    def __str__(self):
        return self.user.username
