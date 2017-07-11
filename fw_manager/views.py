from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from auth_manager.utils import verify_secure
from . import esp8266


class FirmwareUpdateView(APIView):

    """ Provides the firmware if the update is required """
    def get(self, request):
        verify_secure(request)
        if esp8266.Esp8266FirmwareUpdate.verifyRequest(request):
            return esp8266.Esp8266FirmwareUpdate.update(request)
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
