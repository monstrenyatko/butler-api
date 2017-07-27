from django.conf import settings
from django.db import models
from django.core.validators import RegexValidator


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

    name = models.CharField(max_length=150, primary_key=True, validators=[NameValidator])
    hardware = models.CharField(max_length=50, choices=HW_CHOICES)
    description = models.TextField(max_length=250, blank=True)

    class Meta:
        db_table = 'firmware'

    def __str__(self):
        return '{} {}'.format(self.name, self.hardware)


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

    def __str__(self):
        return '{} {}'.format(self.user, self.value)
