import os
from django.conf import settings
from django.db import models
from django.core.validators import RegexValidator


def get_firmware_file_name(obj, filename):
    return os.path.join(settings.APP_DATA_FW_SUBDIR, str(obj.pk))


class FirmwareModel(models.Model):
    AlphaNumericHyphenMinusUnderscoreValidator = RegexValidator(
            r'^[0-9a-zA-Z\-_]*$',
            'Only Alphanumeric characters, Hyphen and Underscore symbols are allowed'
    )
    NameValidator = AlphaNumericHyphenMinusUnderscoreValidator

    HW_ESP8266_4MB = 'ESP8266-4MB'
    HW_CHOICES = (
        (HW_ESP8266_4MB, 'ESP8266 with 4MB flash'),
    )

    name = models.CharField(max_length=50, unique=True, validators=[NameValidator])
    hardware = models.CharField(max_length=50, choices=HW_CHOICES)
    description = models.TextField(max_length=250, blank=True)
    file = models.FileField(upload_to=get_firmware_file_name)
    upload_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'firmware'
        verbose_name = 'firmware'
        verbose_name_plural = 'firmwares'

    def __str__(self):
        return '{}<{}>'.format(self.name, self.hardware)


class FirmwareAssignmentModel(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='firmware',
        primary_key=True,
        limit_choices_to={'profile__is_device': True},
    )
    value = models.ForeignKey(
        FirmwareModel,
        on_delete=models.PROTECT,
        related_name='assignments',
    )

    class Meta:
        db_table = 'firmware_assignment'
        verbose_name = 'firmware assignment'
        verbose_name_plural = 'firmware assignments'

    def __str__(self):
        return '{}<->{}'.format(self.user, self.value)
