from django.db import models


class CertificateFingerprintModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=150)
    value = models.CharField(max_length=150)

    class Meta:
        db_table = 'cert_fingerprint'
        ordering = ['created']
        verbose_name = 'certificate fingerprint'
        verbose_name_plural = 'certificate fingerprints'

    def __str__(self):
        return self.value
