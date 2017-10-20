import os
import hashlib
from django.conf import settings
from django.http import FileResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework import exceptions as rest_exceptions

# HTTP_USER_AGENT                 = 'User-Agent'
# HTTP_X_ESP8266_STA_MAC          = 'x-ESP8266-STA-MAC'       # WiFi.macAddress()
# HTTP_X_ESP8266_AP_MAC           = 'x-ESP8266-AP-MAC'        # WiFi.softAPmacAddress()
# HTTP_X_ESP8266_FREE_SPACE       = 'x-ESP8266-free-space'    # ESP.getFreeSketchSpace()
# HTTP_X_ESP8266_SKETCH_SIZE      = 'x-ESP8266-sketch-size'   # ESP.getSketchSize()
# HTTP_X_ESP8266_SKETCH_MD5       = 'x-ESP8266-sketch-md5'    # ESP.getSketchMD5()
# HTTP_X_ESP8266_CHIP_SIZE        = 'x-ESP8266-chip-size'     # ESP.getFlashChipRealSize()
# HTTP_X_ESP8266_SDK_VERSION      = 'x-ESP8266-sdk-version'   # ESP.getSdkVersion()
# HTTP_X_ESP8266_MODE             = 'x-ESP8266-mode'          # 'sketch' or 'spiffs' update request
# HTTP_X_ESP8266_VERSION          = 'x-ESP8266-version'       # custom current version

HTTP_USER_AGENT_VALUE_ESP8266   = 'ESP8266-http-Update'

def md5(file_path):
    res = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            res.update(chunk)
    return res.hexdigest()

def formatMacAddress(mac_hex):
    return ':'.join([mac_hex[i:i+2] for i,_ in enumerate(mac_hex) if not (i%2)])

def verifyHeaderAvailable(request, header):
    if not header in request.META:
        raise rest_exceptions.ValidationError({header: 'Is not available'})

def verifyHeaderValue(request, header, expected_value):
    verifyHeaderAvailable(request, header)
    if not expected_value.lower() == request.META[header].lower():
        raise rest_exceptions.ValidationError({header: 'Expected value is [{}]'.format(expected_value)})

def verifyRequest(request, assignment):
    verifyHeaderValue(request, 'HTTP_USER_AGENT', HTTP_USER_AGENT_VALUE_ESP8266)
    verifyHeaderValue(request, 'HTTP_X_ESP8266_STA_MAC', formatMacAddress(assignment.user.username))
    verifyHeaderAvailable(request, 'HTTP_X_ESP8266_SKETCH_MD5')

def update(request, assignment):
    """ Provides the ESP8266 firmware if the update is required """
    verifyRequest(request, assignment)
    file_name_rel = assignment.value.file.name
    file_path = os.path.join(settings.APP_DATA_FW_ROOT, file_name_rel)
    file_name = os.path.basename(file_name_rel)
    if not os.path.isfile(file_path):
        raise rest_exceptions.NotFound({'file': 'The [{:s}] is not found'.format(file_name_rel)})
    # Verifying that update is required
    file_md5 = md5(file_path)
    if request.META['HTTP_X_ESP8266_SKETCH_MD5'] == file_md5:
        return Response(status=status.HTTP_304_NOT_MODIFIED)
    # Deliver update
    file_size = os.path.getsize(file_path)
    response = FileResponse(open(file_path, 'rb'))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Length'] = file_size
    response['Content-Disposition'] = "attachment; filename={}".format(file_name)
    response['x-MD5'] = file_md5
    return response
