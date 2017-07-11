import os
import hashlib
from django.http import FileResponse
from rest_framework.response import Response
from rest_framework import status


HTTP_X_ESP8266_STA_MAC      = 'x-ESP8266-STA-MAC'       # WiFi.macAddress()
HTTP_X_ESP8266_AP_MAC       = 'x-ESP8266-AP-MAC'        # WiFi.softAPmacAddress()
HTTP_X_ESP8266_FREE_SPACE   = 'x-ESP8266-free-space'    # ESP.getFreeSketchSpace()
HTTP_X_ESP8266_SKETCH_SIZE  = 'x-ESP8266-sketch-size'   # ESP.getSketchSize()
HTTP_X_ESP8266_SKETCH_MD5   = 'x-ESP8266-sketch-md5'    # ESP.getSketchMD5()
HTTP_X_ESP8266_CHIP_SIZE    = 'x-ESP8266-chip-size'     # ESP.getFlashChipRealSize()
HTTP_X_ESP8266_SDK_VERSION  = 'x-ESP8266-sdk-version'   # ESP.getSdkVersion()
HTTP_X_ESP8266_MODE         = 'x-ESP8266-mode'          # 'sketch' or 'spiffs' update request
HTTP_X_ESP8266_VERSION      = 'x-ESP8266-version'       # custom current version
HTTP_USER_AGENT_ESP8266     = 'ESP8266-http-Update'

def md5(fileName):
    res = hashlib.md5()
    with open(fileName, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            res.update(chunk)
    return res.hexdigest()

def verifyHeaders(request):
    return (    'HTTP_USER_AGENT'               in request.META
#             and 'HTTP_X_ESP8266_STA_MAC'        in request.META
#             and 'HTTP_X_ESP8266_AP_MAC'         in request.META
#             and 'HTTP_X_ESP8266_FREE_SPACE'     in request.META
#             and 'HTTP_X_ESP8266_SKETCH_SIZE'    in request.META
#             and 'HTTP_X_ESP8266_SKETCH_MD5'     in request.META
#             and 'HTTP_X_ESP8266_CHIP_SIZE'      in request.META
#             and 'HTTP_X_ESP8266_SDK_VERSION'    in request.META
            )

def verifyUserAgent(value):
    return value == HTTP_USER_AGENT_ESP8266

def verifyVersion():
    return True

class Esp8266FirmwareUpdate:
    """ ESP8266 implementation """

    """ Verifies the User-Agent HTTP header value """
    @staticmethod
    def verifyRequest(request):
        return verifyHeaders(request) and verifyUserAgent(request.META['HTTP_USER_AGENT'])

    """ Provides the firmware if the update is required """
    @staticmethod
    def update(request):
        if verifyVersion():
            return Response(status=status.HTTP_304_NOT_MODIFIED)
        fileName = 'fwfile.bin'
        if 'HTTP_X_ESP8266_VERSION' in request.META:
            print(request.META['HTTP_X_ESP8266_VERSION'])
        #return Response(status=status.HTTP_304_NOT_MODIFIED)
        #return Response(status=status.HTTP_404_NOT_FOUND)
        response = FileResponse(open(fileName, 'rb'))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Length'] = os.path.getsize(fileName)
        response['Content-Disposition'] = "attachment; filename=%s" % fileName
        response['x-MD5'] = md5(fileName)
        return response


