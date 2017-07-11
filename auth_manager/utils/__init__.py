from rest_framework import exceptions

def verify_secure(request):
    if not request.is_secure():
        raise exceptions.PermissionDenied(detail='SSL required')