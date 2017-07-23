from rest_framework import generics
from rest_framework import exceptions
from . import serializers as local_serializers
from . import models as local_models

class CertificateFingerprintView(generics.ListAPIView):
    serializer_class = local_serializers.CertificateFingerprintSerializer
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        name = self.kwargs['name']
        res = local_models.CertificateFingerprintModel.objects.filter(name=name)
        if not len(res):
            raise exceptions.NotFound(detail='[{}] is not found'.format(name))
        return res
