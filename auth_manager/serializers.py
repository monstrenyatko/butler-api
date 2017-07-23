from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from . import models as local_models


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ('key', 'created')
        extra_kwargs = {
            'key': {'write_only': True},
            'created': {'read_only': True},
        }


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = local_models.UserProfileModel
        fields = ('is_device', 'is_auth_retrieved')
        extra_kwargs = {
            'is_device': {'read_only': True},
            'is_auth_retrieved': {'read_only': True},
        }


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)
    auth_token = TokenSerializer(read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('username', 'password', 'date_joined', 'auth_token', 'profile', 'is_staff')
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'date_joined': {'read_only': True},
        }


    @transaction.atomic
    def create(self, validated_data):
        # Pop UserProfile data
        profile_data = validated_data.pop('profile', {})
        # Create User
        instance = get_user_model().objects.create_user(**validated_data)
        # Update UserProfile
        for attr, value in profile_data.items():
            setattr(instance.profile, attr, value)
        instance.profile.is_device = self.context.get('is_device', False)
        # Check password availability if required
        if (not instance.profile.is_device) and (not 'password' in validated_data):
            raise serializers.ValidationError({'password': [
                self.fields['password'].error_messages['required']
            ]})
        # Set password == user-name if required
        if instance.profile.is_device:
            instance.set_password(instance.username)
        # Done
        instance.save()
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        # Update User
        super().update(instance, validated_data)
        # Update UserProfile
        for attr, value in profile_data.items():
            setattr(instance.profile, attr, value)
        instance.save()
        return instance


class DeviceSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ('username', 'password', 'date_joined', 'auth_token', 'profile',)

class EnableAuthSerializer(serializers.Serializer):
    username = serializers.CharField(label=_("Username"))

    def validate(self, attrs):
        username = attrs.get('username')

        if username:
            try:
                user = get_user_model().objects.get(username=username)
                attrs['user'] = user
            except get_user_model().DoesNotExist:
                raise serializers.ValidationError('Unable to find the provided account.')
        else:
            raise serializers.ValidationError({'username': [
                self.fields['username'].error_messages['required']
            ]})
        return attrs
