import os
from django import http
from django.conf import settings
from rest_framework import generics
from rest_framework import exceptions
from rest_framework import permissions as rest_permissions
from auth_manager.utils import verify_secure
from .utils import openssl
from . import serializers as local_serializers
from . import models as local_models


class CertificateFingerprintView(generics.ListAPIView):
    """ Provides the server certificate fingerprint """
    permission_classes = (rest_permissions.AllowAny,)
    serializer_class = local_serializers.CertificateFingerprintSerializer

    def get_queryset(self):
        name = self.kwargs['name']
        res = local_models.CertificateFingerprintModel.objects.filter(name=name)
        if not len(res):
            raise exceptions.NotFound(detail='[{}] is not found'.format(name))
        return res


class ClientCertificateView(generics.GenericAPIView):
    """ Provides the client certificates """
    def get(self, request, *args, **kwargs):
        verify_secure(request)
        username = request.user.username
        name = kwargs['name'].lower()
        form = kwargs.get('form', 'pem').lower()
        stream = None
        try:
            stream = openssl.get_client_stream(settings.APP_DATA_CERT_DIR, username, name, form)
        except Exception as e:
            raise exceptions.NotFound(e)
        if not stream:
            raise exceptions.NotFound(detail='[{}:{}:{}] is not found'.format(username, name, form))
        response = http.FileResponse(stream)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Length'] = os.fstat(stream.fileno()).st_size
        response['Content-Disposition'] = "attachment; filename={}.{}".format(name, form)
        return response


class CaCertificateView(generics.GenericAPIView):
    permission_classes = (rest_permissions.AllowAny,)
    """ Provides the CA certificate """
    def get(self, request, *args, **kwargs):
        verify_secure(request)
        form = kwargs.get('form', 'pem').lower()
        stream = None
        try:
            stream = openssl.get_ca_crt_stream(settings.APP_DATA_CERT_DIR, form)
        except Exception as e:
            raise exceptions.NotFound(e)
        if not stream:
            raise exceptions.NotFound()
        response = http.FileResponse(stream)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Length'] = os.fstat(stream.fileno()).st_size
        response['Content-Disposition'] = "attachment; filename={}.{}".format('ca.crt', form)
        return response
