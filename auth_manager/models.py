from django.conf import settings
from django.db import models
from django.core.validators import RegexValidator


class UserLocationModel(models.Model):
    NameValidator = RegexValidator(
        r'^[0-9a-zA-Z\-_]*$',
        'Only Alphanumeric characters, Hyphen and Underscore symbols are allowed'
    )

    NAME_UNKNOWN = 'UNKNOWN'

    name = models.CharField(max_length=50, unique=True, validators=[NameValidator])

    class Meta:
        db_table = 'user_location'
        verbose_name = 'user location'
        verbose_name_plural = 'user locations'

    def __str__(self):
        return self.name


class UserProfileModel(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='profile',
        on_delete=models.CASCADE
    )
    is_device = models.BooleanField(default=False)
    is_auth_retrieved = models.BooleanField(default=False)
    location = models.ForeignKey(
        UserLocationModel,
        on_delete=models.PROTECT,
        to_field='name',
        default=UserLocationModel.NAME_UNKNOWN,
    )

    class Meta:
        db_table = 'user_profile'
        verbose_name = 'user profile'
        verbose_name_plural = 'user profiles'

    def __str__(self):
        return self.user.username


def mqtt_acl_template_to_topic(acl_template, user):
    topic = acl_template.replace('%u', user.username)
    return topic


class MqttAclTemplateModel(models.Model):
    NameValidator = RegexValidator(
        r'^[0-9a-zA-Z\-_]*$',
        'Only Alphanumeric characters, Hyphen and Underscore symbols are allowed'
    )
    TemplateValidator = RegexValidator(
        r'^([0-9a-zA-Z\-_\/]|(%u))*\/$',
        'Only Alphanumeric characters, Hyphen, Underscore, Forward-Slash symbols are allowed '
        'plus template arguments like: %u - user-name'
        ' and must end with Forward-Slash symbol'
    )

    NAME_USER_DEFAULT = 'USER_DEFAULT'
    NAME_USER_DATA = 'USER_DATA'
    NAME_USER_CONFIG = 'USER_CONFIG'
    NAME_CHOICES = (
        (NAME_USER_DEFAULT, 'USER DEFAULT'),
        (NAME_USER_DATA, 'USER DATA'),
        (NAME_USER_CONFIG, 'USER CONFIG'),
    )

    name = models.CharField(max_length=50, unique=True, choices=NAME_CHOICES, validators=[NameValidator])
    template = models.CharField(max_length=150, unique=True, validators=[TemplateValidator])

    class Meta:
        db_table = 'mqtt_acl_template'
        verbose_name = 'mqtt acl template'
        verbose_name_plural = 'mqtt acl templates'

    def __str__(self):
        return self.template


class MqttAclModel(models.Model):
    ACCESS_READ = 1
    ACCESS_WRITE = 2
    ACCESS_READ_WRITE = 3
    ACCESS_CHOICES = (
        (ACCESS_READ, 'READ'),
        (ACCESS_WRITE, 'WRITE'),
        (ACCESS_READ_WRITE, 'READ+WRITE'),
    )
    MqttAclTopicValidator = RegexValidator(
        r'^([0-9a-zA-Z\-_\/])*\/$',
        'Only Alphanumeric characters, Hyphen, Underscore, Forward-Slash symbols are allowed'
        ' and must end with Forward-Slash symbol'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mqtt_acl',
    )
    topic = models.CharField(max_length=150, validators=[MqttAclTopicValidator])
    access = models.PositiveSmallIntegerField(choices=ACCESS_CHOICES)

    class Meta:
        db_table = 'mqtt_acl'
        verbose_name = 'mqtt acl'
        verbose_name_plural = 'mqtt acl'

    def __str__(self):
        return self.topic
