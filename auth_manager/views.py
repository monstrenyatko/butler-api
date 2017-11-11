import time
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from django import http
from rest_framework import generics
from rest_framework import renderers
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import exceptions
from rest_framework.authtoken import views as rest_view
from rest_framework.authtoken.models import Token
from rest_framework import permissions as rest_permissions
from jose import jwt
from . import serializers as local_serializers
from .utils import verify_secure


def get_device_serializer_context(serializer_context):
    serializer_context['is_device'] = True
    return serializer_context


class UserListView(generics.ListCreateAPIView):
    permission_classes = (rest_permissions.IsAdminUser,)
    queryset = get_user_model().objects.all()
    serializer_class = local_serializers.UserSerializer

    def get(self, request, *args, **kwargs):
        """ Retrieves the list of users """
        verify_secure(request)
        return super().get(request, args, kwargs)

    def post(self, request, *args, **kwargs):
        """ Creates the new user """
        verify_secure(request)
        return super().post(request, args, kwargs)

    def create(self, request, *args, **kwargs):
        response = super().create(request, args, kwargs)
        response.data = None
        return response


class UserDetailView(generics.RetrieveDestroyAPIView):
    permission_classes = (rest_permissions.IsAdminUser,)
    queryset = get_user_model().objects.all()
    serializer_class = local_serializers.UserSerializer
    lookup_field = 'username'

    def get(self, request, *args, **kwargs):
        """ Retrieves details about the specific user """
        verify_secure(request)
        return super().get(request, args, kwargs)

    def delete(self, request, *args, **kwargs):
        """ Deletes the specific user """
        verify_secure(request)
        return super().delete(request, args, kwargs)


class DeviceListView(UserListView):
    queryset = get_user_model().objects.filter(profile__is_device=True)
    serializer_class = local_serializers.DeviceSerializer

    def get(self, request, *args, **kwargs):
        """ Retrieves the list of devices """
        return super().get(request, args, kwargs)

    def post(self, request, *args, **kwargs):
        """ Creates the new device """
        return super().post(request, args, kwargs)

    def get_serializer_context(self):
        return get_device_serializer_context(super().get_serializer_context())


class DeviceDetailView(UserDetailView):
    queryset = get_user_model().objects.filter(profile__is_device=True)
    serializer_class = local_serializers.DeviceSerializer

    def get(self, request, *args, **kwargs):
        """ Retrieves details about the specific device """
        return super().get(request, args, kwargs)

    def delete(self, request, *args, **kwargs):
        """ Deletes the specific device """
        return super().delete(request, args, kwargs)

    def get_serializer_context(self):
        return get_device_serializer_context(super().get_serializer_context())


class EnableAuthView(GenericAPIView):
    permission_classes = (rest_permissions.IsAdminUser,)
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = local_serializers.EnableAuthSerializer

    def post(self, request):
        """ Enables the authentication """
        verify_secure(request)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        Token.objects.filter(user=user).delete()
        Token.objects.create(user=user)
        user.profile.is_auth_retrieved = False
        user.save()
        return Response(status=status.HTTP_200_OK)


class GetAuthTokenView(rest_view.ObtainAuthToken):

    def post(self, request):
        """ Returns the access token """
        verify_secure(request)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if not user.is_staff:
            now = timezone.now()
            if user.profile.is_auth_retrieved:
                raise exceptions.PermissionDenied(detail='Token has been already retrieved')
            if user.auth_token.created < now - settings.AUTH_TIME_INTERVAL:
                raise exceptions.PermissionDenied(detail='Token cannot be retrieved anymore')
        user.profile.is_auth_retrieved = True
        user.save()
        return Response({'token': user.auth_token.key})


class GetJwtView(GenericAPIView):

    def get(self, request):
        """ Returns the JWT access token """
        verify_secure(request)
        user = request.user
        content = jwt.encode(
            {
                'user': user.username,
                'exp': int(time.time()) + settings.AUTH_JWT_EXPIRE_AFTER_SEC,
            },
            settings.SECRET_KEY, algorithm='HS256'
        )
        response = http.HttpResponse(content_type='application/jwt')
        response.content = content
        return response
