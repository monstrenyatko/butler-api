from django.contrib.auth import get_user_model
from rest_framework import serializers
from . import models as local_models


class FirmwareSerializer(serializers.ModelSerializer):
    class Meta:
        model = local_models.FirmwareModel
        fields = ('name', 'hardware', 'description')
        extra_kwargs = {
            'name': {'read_only': True},
        }


class FirmwareCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = local_models.FirmwareModel
        fields = ('name', 'hardware', 'description')


class FirmwareAssignmentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = local_models.FirmwareAssignmentModel
        fields = ('user', 'value')
        extra_kwargs = {
            'user': {'read_only': True},
        }


class FirmwareAssignmentCreateSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=get_user_model().objects.all().prefetch_related('profile'),
     )

    class Meta:
        model = local_models.FirmwareAssignmentModel
        fields = ('user', 'value')

    def validate_user(self, value):
        u = get_user_model().objects.get(username=value)
        if not u.profile.is_device:
            raise serializers.ValidationError('Is not the device')
        return u
