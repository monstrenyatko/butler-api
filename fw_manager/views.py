from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework import permissions as rest_permissions
from rest_framework import exceptions as rest_exceptions
from rest_framework import parsers  as rest_parsers
from auth_manager.utils import verify_secure
from . import esp8266
from . import serializers as local_serializers
from . import models as local_models


class FirmwareUpdateView(generics.GenericAPIView):

    def get(self, request):
        """ Provides the firmware if the update is required """
        verify_secure(request)
        if not request.user.profile.is_device:
            raise rest_exceptions.NotAcceptable('Only for devices')
        assignment = None
        try:
            assignment = request.user.firmware
        except local_models.FirmwareAssignmentModel.DoesNotExist:
            raise rest_exceptions.NotFound({'firmware': 'Not available'})
        if assignment.value.hardware == local_models.FirmwareModel.HW_ESP8266_4MB:
            return esp8266.update(request, assignment)
        else:
            raise rest_exceptions.NotAcceptable('The [{:s}] is not supported'.format(assignment.value.hardware))


class FirmwareUpdateAnonymousView(generics.GenericAPIView):
    permission_classes = (rest_permissions.AllowAny,)

    def get(self, request, **kwargs):
        """ Provides the firmware if the update is required for not secure connection """
        username = kwargs['username']
        user = None
        try:
            user = get_user_model().objects.get(username=username)
        except get_user_model().DoesNotExist:
            raise rest_exceptions.NotFound({username: 'Not found'})
        if not user.profile.is_device:
            raise rest_exceptions.NotAcceptable('Only for devices')
        assignment = None
        try:
            assignment = user.firmware
        except local_models.FirmwareAssignmentModel.DoesNotExist:
            raise rest_exceptions.NotFound({'firmware': 'Not available'})
        if assignment.value.hardware == local_models.FirmwareModel.HW_ESP8266_4MB:
            return esp8266.update(request, assignment)
        else:
            raise rest_exceptions.NotAcceptable('The [{:s}] is not supported'.format(assignment.value.hardware))


class FirmwareListView(generics.ListCreateAPIView):
    permission_classes = (rest_permissions.IsAdminUser,)
    queryset = local_models.FirmwareModel.objects.all()
    parser_classes = (rest_parsers.MultiPartParser, rest_parsers.FormParser,)
    serializer_class = local_serializers.FirmwareSerializer

    def get(self, request, *args, **kwargs):
        """ Retrieves the list of firmwares """
        verify_secure(request)
        return super().get(request, args, kwargs)

    def post(self, request, *args, **kwargs):
        """ Creates the new firmware """
        verify_secure(request)
        return super().post(request, args, kwargs)


class FirmwareDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (rest_permissions.IsAdminUser,)
    queryset = local_models.FirmwareModel.objects.all()
    parser_classes = (rest_parsers.MultiPartParser, rest_parsers.FormParser,)
    serializer_class = local_serializers.FirmwareSerializer
    lookup_field = 'name'

    def get(self, request, *args, **kwargs):
        """ Retrieves details about the specific firmware """
        verify_secure(request)
        return super().get(request, args, kwargs)

    def put(self, request, *args, **kwargs):
        """ Updating the specific firmware """
        verify_secure(request)
        return super().put(request, args, kwargs)

    def patch(self, request, *args, **kwargs):
        """ Partially updating the specific firmware """
        verify_secure(request)
        return super().patch(request, args, kwargs)

    def delete(self, request, *args, **kwargs):
        """ Deletes the specific firmware """
        verify_secure(request)
        return super().delete(request, args, kwargs)


class FirmwareAssignmentListView(generics.ListCreateAPIView):
    permission_classes = (rest_permissions.IsAdminUser,)
    queryset = local_models.FirmwareAssignmentModel.objects.all()
    serializer_class = local_serializers.FirmwareAssignmentSerializer

    def get(self, request, *args, **kwargs):
        """ Retrieves the list of firmware assignments """
        verify_secure(request)
        return super().get(request, args, kwargs)

    def post(self, request, *args, **kwargs):
        """ Creates the new firmware assignment """
        verify_secure(request)
        return super().post(request, args, kwargs)

    def get_serializer_class(self):
        res = self.serializer_class
        if self.request.method == 'POST':
            res = local_serializers.FirmwareAssignmentCreateSerializer
        return res


class FirmwareAssignmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (rest_permissions.IsAdminUser,)
    serializer_class = local_serializers.FirmwareAssignmentSerializer

    def get(self, request, *args, **kwargs):
        """ Retrieves details about the specific firmware assignment """
        verify_secure(request)
        return super().get(request, args, kwargs)

    def put(self, request, *args, **kwargs):
        """ Updating the specific firmware assignment """
        verify_secure(request)
        return super().put(request, args, kwargs)

    def patch(self, request, *args, **kwargs):
        """ Partially updating the specific firmware assignment """
        verify_secure(request)
        return super().patch(request, args, kwargs)

    def delete(self, request, *args, **kwargs):
        """ Deletes the specific firmware assignment """
        verify_secure(request)
        return super().delete(request, args, kwargs)

    def get_object(self):
        username = self.kwargs['username']
        try:
            return local_models.FirmwareAssignmentModel.objects.get(user__username=username)
        except local_models.FirmwareAssignmentModel.DoesNotExist:
            raise rest_exceptions.NotFound(detail='[{}] is not found'.format(username))
