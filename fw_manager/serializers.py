from django.contrib.auth import get_user_model
from rest_framework import serializers
from . import models as local_models


class FirmwareSerializer(serializers.ModelSerializer):
    class Meta:
        model = local_models.FirmwareModel
        fields = ('name', 'hardware', 'description', 'file',)


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

    def create(self, validated_data):
        if local_models.FirmwareAssignmentModel.objects.filter(
                user__username=validated_data['user']
        ).exists():
            raise serializers.ValidationError(
                'Another assignment already available for the [{}]'.format(validated_data['user'])
            )
        return super().create(validated_data)
