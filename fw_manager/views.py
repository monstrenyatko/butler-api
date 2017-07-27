import os
from django.conf import settings
from django.core.exceptions import ValidationError
from rest_framework import views
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework import permissions as rest_permissions
from rest_framework import exceptions as rest_exceptions
from rest_framework import parsers  as rest_parsers
from auth_manager.utils import verify_secure
from . import esp8266
from . import serializers as local_serializers
from . import models as local_models


class FirmwareUpdateView(views.APIView):
    """ Provides the firmware if the update is required """
    def get(self, request):
        verify_secure(request)
        if esp8266.Esp8266FirmwareUpdate.verifyRequest(request):
            return esp8266.Esp8266FirmwareUpdate.update(request)
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)


class FirmwareUploadView(views.APIView):
    permission_classes = (rest_permissions.IsAdminUser,)
    parser_classes = (rest_parsers.FileUploadParser,)

    """ Uploads the firmware file to the storage """
    def put(self, request, filename):
        verify_secure(request)
        try:
            local_models.FirmwareModel.NameValidator(filename)
        except ValidationError as e:
            raise rest_exceptions.ValidationError({filename:list(e)})
        out_dir = settings.APP_DATA_FW_DIR
        os.makedirs(out_dir, exist_ok=True)
        if not os.access(out_dir, os.W_OK):
            raise rest_exceptions.APIException('The [{:s}] is not writable'.format(out_dir))
        out_path = os.path.join(out_dir, filename)
        file_obj = request.data['file']
        with open(out_path, 'wb') as out_file:
            for chunk in file_obj.chunks():
                out_file.write(chunk)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FirmwareListView(generics.ListCreateAPIView):
    permission_classes = (rest_permissions.IsAdminUser,)
    queryset = local_models.FirmwareModel.objects.all()
    serializer_class = local_serializers.FirmwareSerializer

    """ Retrieves the list of firmwares """
    def get(self, request, *args, **kwargs):
        verify_secure(request)
        return super().get(request, args, kwargs)

    """ Creates the new firmware """
    def post(self, request, *args, **kwargs):
        verify_secure(request)
        return super().post(request, args, kwargs)

    def get_serializer_class(self):
        res = self.serializer_class
        if self.request.method == 'POST':
            res = local_serializers.FirmwareCreateSerializer
        return res


class FirmwareDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (rest_permissions.IsAdminUser,)
    queryset = local_models.FirmwareModel.objects.all()
    serializer_class = local_serializers.FirmwareSerializer
    lookup_field = 'name'

    """ Retrieves details about the specific firmware """
    def get(self, request, *args, **kwargs):
        verify_secure(request)
        return super().get(request, args, kwargs)

    """ Updating the specific firmware """
    def put(self, request, *args, **kwargs):
        verify_secure(request)
        return super().put(request, args, kwargs)

    """ Partially updating the specific firmware """
    def patch(self, request, *args, **kwargs):
        verify_secure(request)
        return super().patch(request, args, kwargs)

    """ Deletes the specific firmware """
    def delete(self, request, *args, **kwargs):
        verify_secure(request)
        return super().delete(request, args, kwargs)


class FirmwareAssignmentListView(generics.ListCreateAPIView):
    permission_classes = (rest_permissions.IsAdminUser,)
    queryset = local_models.FirmwareAssignmentModel.objects.all()
    serializer_class = local_serializers.FirmwareAssignmentSerializer

    """ Retrieves the list of firmware assignments """
    def get(self, request, *args, **kwargs):
        verify_secure(request)
        return super().get(request, args, kwargs)

    """ Creates the new firmware assignment """
    def post(self, request, *args, **kwargs):
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

    """ Retrieves details about the specific firmware assignment """
    def get(self, request, *args, **kwargs):
        verify_secure(request)
        return super().get(request, args, kwargs)

    """ Updating the specific firmware assignment """
    def put(self, request, *args, **kwargs):
        verify_secure(request)
        return super().put(request, args, kwargs)

    """ Partially updating the specific firmware assignment """
    def patch(self, request, *args, **kwargs):
        verify_secure(request)
        return super().patch(request, args, kwargs)

    """ Deletes the specific firmware assignment """
    def delete(self, request, *args, **kwargs):
        verify_secure(request)
        return super().delete(request, args, kwargs)

    def get_object(self):
        username = self.kwargs['username']
        try:
            return local_models.FirmwareAssignmentModel.objects.get(user__username=username)
        except local_models.FirmwareAssignmentModel.DoesNotExist:
            raise rest_exceptions.NotFound(detail='[{}] is not found'.format(username))
