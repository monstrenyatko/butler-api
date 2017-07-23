from rest_framework import serializers
from . import models as local_models


class CertificateFingerprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = local_models.CertificateFingerprintModel
        fields = ('value',)
        extra_kwargs = {
            'value': {'read_only': True},
        }