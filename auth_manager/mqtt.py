from . import models as local_models


def verifyUserAccess(user):
    return user != None

def verifySuperuserAccess(user):
    return (user and user.is_superuser)

def verifyAcl(user, topic, access):
    result = False
    for acl in local_models.MqttAclModel.objects.filter(user=user):
        result = topic.startswith(acl.topic) and (
            (access == 1 and (
                acl.access == local_models.MqttAclModel.ACCESS_READ or acl.access == local_models.MqttAclModel.ACCESS_READ_WRITE
            )) or
            (access == 2 and (
                acl.access == local_models.MqttAclModel.ACCESS_WRITE or acl.access == local_models.MqttAclModel.ACCESS_READ_WRITE
            ))
        )
        if result:
            break
    return result
