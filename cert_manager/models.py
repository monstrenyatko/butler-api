from django.db import models


class CertificateFingerprintModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=150)
    value = models.CharField(max_length=150)

    class Meta:
        db_table = 'cert_fingerprint'
        ordering = ['created']
 
    def __str__(self):
        return '{} {} {}'.format(self.name, self.value, self.created)
