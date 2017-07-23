from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from rest_framework import generics
from rest_framework import renderers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import exceptions
from rest_framework.authtoken import views as rest_view
from rest_framework.authtoken.models import Token
from . import serializers as local_serializers
from .utils import verify_secure


def get_device_serializer_context(serializer_context):
    serializer_context['is_device'] = True
    return serializer_context


class UserListView(generics.ListCreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = local_serializers.UserSerializer

    """ Retrieves the list of users """
    def get(self, request, *args, **kwargs):
        verify_secure(request)
        return super().get(request, args, kwargs)

    """ Creates the new user """
    def post(self, request, *args, **kwargs):
        verify_secure(request)
        return super().post(request, args, kwargs)

    def create(self, request, *args, **kwargs):
        response = super().create(request, args, kwargs)
        response.data = None
        return response


class UserDetailView(generics.RetrieveDestroyAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = local_serializers.UserSerializer
    lookup_field = 'username'

    """ Retrieves details about the specific user """
    def get(self, request, *args, **kwargs):
        verify_secure(request)
        return super().get(request, args, kwargs)

    """ Deletes the specific user """
    def delete(self, request, *args, **kwargs):
        verify_secure(request)
        return super().delete(request, args, kwargs)


class DeviceListView(UserListView):
    queryset = get_user_model().objects.filter(profile__is_device=True)

    def get_serializer_context(self):
        return get_device_serializer_context(super().get_serializer_context())


class DeviceDetailView(UserDetailView):
    queryset = get_user_model().objects.filter(profile__is_device=True)

    def get_serializer_context(self):
        return get_device_serializer_context(super().get_serializer_context())


class EnableAuthView(APIView):
    renderer_classes = (renderers.JSONRenderer,)
    serializer_class = local_serializers.EnableAuthSerializer

    """ Enables the authentication """
    def post(self, request):
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

    """ Returns the access token """
    def post(self, request):
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
