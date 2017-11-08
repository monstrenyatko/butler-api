import os
from django import http
from django.conf import settings
from rest_framework import generics
from rest_framework import exceptions
from rest_framework import permissions as rest_permissions
from rest_framework import status as rest_status
from rest_framework.response import Response
from auth_manager.utils import verify_secure
from .utils import openssl
from . import serializers as local_serializers
from . import models as local_models


class CertificateFingerprintView(generics.ListAPIView):
    """ Provides the server certificate fingerprint """
    permission_classes = (rest_permissions.AllowAny,)
    serializer_class = local_serializers.CertificateFingerprintSerializer

    def get_queryset(self):
        name = self.kwargs['host']
        res = local_models.CertificateFingerprintModel.objects.filter(name=name)
        if not len(res):
            raise exceptions.NotFound(detail='[{}] is not found'.format(name))
        return res


class ClientCertificateView(generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        """ Provides the client certificates """
        verify_secure(request)
        username = request.user.username
        ext = kwargs['type'].lower()
        form = kwargs.get('form', 'pem').lower()
        # Get MD5 value from request if available
        req_md5 = None
        if 'HTTP_X_MD5' in request.META:
            req_md5 = request.META['HTTP_X_MD5']
        # Calculate MD5 value
        file_md5 = None
        try:
            file_md5 = openssl.get_client_md5(settings.APP_DATA_CERT_DIR, username, ext, form)
        except Exception as e:
            raise exceptions.NotFound(e)
        # If MD5 value is provided in request => Verify that update is required
        if req_md5 and req_md5 == file_md5:
            return Response(status=rest_status.HTTP_304_NOT_MODIFIED)
        # Deliver update
        stream = None
        try:
            stream = openssl.get_client_stream(settings.APP_DATA_CERT_DIR, username, ext, form)
        except Exception as e:
            raise exceptions.NotFound(e)
        if (not stream) or (not file_md5):
            raise exceptions.NotFound(detail='[{}:{}:{}] is not found'.format(username, ext, form))
        response = http.FileResponse(stream)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Length'] = os.fstat(stream.fileno()).st_size
        response['Content-Disposition'] = "attachment; filename={}.{}".format(ext, form)
        response['x-MD5'] = file_md5
        return response


class CaCertificateView(generics.GenericAPIView):
    permission_classes = (rest_permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        """ Provides the CA certificate """
        verify_secure(request)
        form = kwargs.get('form', 'pem').lower()
        # Get MD5 value from request if available
        req_md5 = None
        if 'HTTP_X_MD5' in request.META:
            req_md5 = request.META['HTTP_X_MD5']
        # Calculate MD5 value
        file_md5 = None
        try:
            file_md5 = openssl.get_ca_crt_md5(settings.APP_DATA_CERT_DIR, form)
        except Exception as e:
            raise exceptions.NotFound(e)
        # If MD5 value is provided in request => Verify that update is required
        if req_md5 and req_md5 == file_md5:
            return Response(status=rest_status.HTTP_304_NOT_MODIFIED)
        # Deliver update
        stream = None
        try:
            stream = openssl.get_ca_crt_stream(settings.APP_DATA_CERT_DIR, form)
        except Exception as e:
            raise exceptions.NotFound(e)
        if (not stream) or (not file_md5):
            raise exceptions.NotFound()
        response = http.FileResponse(stream)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Length'] = os.fstat(stream.fileno()).st_size
        response['Content-Disposition'] = "attachment; filename={}.{}".format('ca.crt', form)
        response['x-MD5'] = file_md5
        return response
