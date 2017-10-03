import os
import shutil
import subprocess
import tempfile
import hashlib
import datetime
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from OpenSSL.crypto import load_certificate, FILETYPE_PEM
from .. import models as local_models


OPENSSL_CMD = 'openssl'
OPENSSL_KEY_SIZE = 2048
OPENSSL_CA_DIR_NAME = 'ca'
OPENSSL_CS_DIR_NAME = 'srv'
OPENSSL_CC_DIR_NAME = 'clt'
OPENSSL_C_RENEWED_DIR_NAME = 'next'
OPENSSL_CA_PRIVATE_DIR_NAME = OPENSSL_CA_DIR_NAME + '-private'
OPENSSL_CS_DEFAULT_HOSTNAME = 'butler'
OPENSSL_CA_DEFAULT_DAYS = 3650
OPENSSL_CS_DEFAULT_DAYS = 365
OPENSSL_CC_DEFAULT_DAYS = 14
OPENSSL_C_NAME_CRT = 'crt'
OPENSSL_C_NAME_KEY = 'key'
OPENSSL_C_NAME_CSR = 'csr'
OPENSSL_C_NAME_FGR = 'fgr'
OPENSSL_C_NAME_SRL = 'srl'
OPENSSL_C_FORM_PEM = 'pem'
OPENSSL_C_FORM_DER = 'der'
OPENSSL_CONFIG_TEMPLATE = """
prompt = no
distinguished_name = req_distinguished_name
req_extensions = v3_req

[ req_distinguished_name ]
O                      = Butler Self-Signed
CN                     = {hostname:s}

[ v3_ca ]
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid:always,issuer:always
basicConstraints = CA:true

[ v3_req ]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = {hostname:s}
DNS.2 = {hostname:s}.local
"""

def rm_files(path):
    for i in os.scandir(path):
        if i.is_file():
            os.unlink(i.path)

def mv_files(src, dst):
    for i in os.scandir(src):
        shutil.move(i.path, dst)

def open_cert_stream(path):
    if os.path.isfile(path):
        return open(path, 'rb')
    else:
        return None

def store_str_file(file_path, text):
    with open(file_path,'w') as file:
        file.write(text)

def read_str_file(file_path):
    res = ''
    if os.path.isfile(file_path):
        with open(file_path,'r') as file:
            res = file.read()
    return res

def set_cert_key_owner(file_path):
    os.chown(file_path,
        settings.APP_DATA_CERT_KEY_FILE_UID,
        settings.APP_DATA_CERT_KEY_FILE_GID
    )

def set_cert_key_mode(file_path):
    os.chmod(file_path, settings.APP_DATA_CERT_KEY_FILE_MODE)

def openssl(*args):
    cmdline = [OPENSSL_CMD] + list(args)
    subprocess.check_call(cmdline, stderr=subprocess.STDOUT)

def prepare_dir(path):
    os.makedirs(path, exist_ok=True)
    if not os.access(path, os.W_OK):
        raise Exception('The [{:s}] is not writable'.format(path))

def make_ca_dir_path(path):
    return os.path.join(path, OPENSSL_CA_DIR_NAME)

def make_ca_private_dir_path(path):
    return os.path.join(path, OPENSSL_CA_PRIVATE_DIR_NAME)

def make_ca_file_name(path, ext, form=OPENSSL_C_FORM_PEM):
    return os.path.join(make_ca_dir_path(path), 'ca.{:s}.{:s}'.format(ext, form))

def make_ca_private_file_name(path, ext, form=OPENSSL_C_FORM_PEM):
    return os.path.join(make_ca_private_dir_path(path), 'ca.{:s}.{:s}'.format(ext, form))

def make_ca_private_file_name_short(path, ext):
    return os.path.join(make_ca_private_dir_path(path), 'ca.{:s}'.format(ext))

def make_c_file_name(path, hostname, ext, form=OPENSSL_C_FORM_PEM):
    return os.path.join(path, '{:s}.{:s}.{:s}'.format(hostname, ext, form))

def make_c_file_name_short(path, hostname, ext):
    return os.path.join(path, '{:s}.{:s}'.format(hostname, ext))

def make_config_file(hostname):
    config = tempfile.NamedTemporaryFile('w')
    config.write(OPENSSL_CONFIG_TEMPLATE.format(
        hostname=hostname
    ))
    config.flush()
    return config

def make_fingerprint(crt_file_name):
    cert_file_data = open(crt_file_name, 'rb').read()
    cert = load_certificate(FILETYPE_PEM, cert_file_data)
    return cert.digest('sha1').decode()

def gen_c(path, path_out, hostname, days):
    prepare_dir(path_out)
    config = make_config_file(hostname)
    openssl('genpkey', '-algorithm', 'RSA',
            '-pkeyopt', 'rsa_keygen_bits:{}'.format(OPENSSL_KEY_SIZE),
            '-out', make_c_file_name(path_out, hostname, OPENSSL_C_NAME_KEY),
    )
    openssl('req', '-new',
            '-config', config.name,
            '-key', make_c_file_name(path_out, hostname, OPENSSL_C_NAME_KEY),
            '-out', make_c_file_name(path_out, hostname, OPENSSL_C_NAME_CSR),
    )
    openssl('x509', '-req', '-days', str(days),
            '-extensions', 'v3_req',
            '-extfile', config.name,
            '-CA', make_ca_file_name(path, OPENSSL_C_NAME_CRT),
            '-CAkey', make_ca_private_file_name(path, OPENSSL_C_NAME_KEY),
            '-CAserial', make_ca_private_file_name_short(path, OPENSSL_C_NAME_SRL),
            '-in', make_c_file_name(path_out, hostname, OPENSSL_C_NAME_CSR),
            '-out', make_c_file_name(path_out, hostname, OPENSSL_C_NAME_CRT),
    )
    config.close()
    # update permissions
    set_cert_key_mode(make_c_file_name(path_out, hostname, OPENSSL_C_NAME_KEY))
    set_cert_key_owner(make_c_file_name(path_out, hostname, OPENSSL_C_NAME_KEY))

def gen_ca(path, days=OPENSSL_CA_DEFAULT_DAYS):
    prepare_dir(make_ca_dir_path(path))
    prepare_dir(make_ca_private_dir_path(path))
    config = make_config_file('CA')
    openssl('req', '-nodes' ,'-new',
            '-newkey', 'rsa:{}'.format(OPENSSL_KEY_SIZE),
            '-x509', '-extensions', 'v3_ca', '-days', str(days),
            '-config', config.name,
            '-keyout', make_ca_private_file_name(path, OPENSSL_C_NAME_KEY),
            '-out', make_ca_file_name(path, OPENSSL_C_NAME_CRT),
    )
    config.close()
    serial = str(hashlib.md5(
            str(datetime.datetime.now()).encode()
    ).hexdigest())
    store_str_file(make_ca_private_file_name_short(path, OPENSSL_C_NAME_SRL), serial)
    openssl('x509', '-outform', 'DER',
            '-in', make_ca_file_name(path, OPENSSL_C_NAME_CRT),
            '-out', make_ca_file_name(path, OPENSSL_C_NAME_CRT, OPENSSL_C_FORM_DER),
    )
    # update permissions
    set_cert_key_mode(make_ca_private_file_name(path, OPENSSL_C_NAME_KEY))
    set_cert_key_owner(make_ca_private_file_name(path, OPENSSL_C_NAME_KEY))

def gen_server(path, hostname=OPENSSL_CS_DEFAULT_HOSTNAME, days=OPENSSL_CS_DEFAULT_DAYS):
    path_out = os.path.join(path, OPENSSL_CS_DIR_NAME, hostname, OPENSSL_C_RENEWED_DIR_NAME)
    gen_c(path, path_out, hostname, days)
    store_str_file(
            make_c_file_name_short(path_out, hostname, OPENSSL_C_NAME_FGR),
            make_fingerprint(make_c_file_name(path_out, hostname, OPENSSL_C_NAME_CRT))
    )

def gen_client(path, hostname, days=OPENSSL_CC_DEFAULT_DAYS):
    path_out = os.path.join(path, OPENSSL_CC_DIR_NAME, hostname)
    gen_c(path, path_out, hostname, days)
    openssl('x509', '-outform', 'DER',
            '-in', make_c_file_name(path_out, hostname, OPENSSL_C_NAME_CRT),
            '-out', make_c_file_name(path_out, hostname, OPENSSL_C_NAME_CRT, OPENSSL_C_FORM_DER),
    )
    openssl('pkey', '-outform', 'DER',
            '-in', make_c_file_name(path_out, hostname, OPENSSL_C_NAME_KEY),
            '-out', make_c_file_name(path_out, hostname, OPENSSL_C_NAME_KEY, OPENSSL_C_FORM_DER),
    )

def rotate_server(path, hostname=OPENSSL_CS_DEFAULT_HOSTNAME):
    path_in = os.path.join(path, OPENSSL_CS_DIR_NAME, hostname, OPENSSL_C_RENEWED_DIR_NAME)
    path_out = os.path.join(path, OPENSSL_CS_DIR_NAME, hostname)
    if not os.path.isdir(path_in) or len(os.listdir(path_in)) == 0:
        raise Exception('The [{:s}] is empty or not exists or not a directory'.format(path_in))
    rm_files(path_out)
    mv_files(path_in, path_out)
    os.rmdir(path_in)

@transaction.atomic
def update_server_fingerprint(path, hostname=OPENSSL_CS_DEFAULT_HOSTNAME):
    path_current = os.path.join(path, OPENSSL_CS_DIR_NAME, hostname)
    path_next = os.path.join(path, OPENSSL_CS_DIR_NAME, hostname, OPENSSL_C_RENEWED_DIR_NAME)
    fp_current = read_str_file(make_c_file_name_short(path_current, hostname, OPENSSL_C_NAME_FGR)).replace('\n', '').strip()
    fp_next = read_str_file(make_c_file_name_short(path_next, hostname, OPENSSL_C_NAME_FGR)).replace('\n', '').strip()
    # Add current value if not exists
    if fp_current:
        local_models.CertificateFingerprintModel.objects.get_or_create(name=hostname, value=fp_current)
    # Add next value if not exists
    if fp_next:
        local_models.CertificateFingerprintModel.objects.get_or_create(name=hostname, value=fp_next)
    # Cleanup old values
    local_models.CertificateFingerprintModel.objects.filter(
        (Q(name = hostname) & ~Q(value = fp_current) & ~Q(value = fp_next))
    ).delete()

def get_client_stream(path, hostname, name, form=OPENSSL_C_FORM_PEM):
    # verify name value
    if not name in [OPENSSL_C_NAME_CRT, OPENSSL_C_NAME_KEY]:
        raise Exception('The [{:s}] is not supported'.format(name))
    # verify form value
    if not form in [OPENSSL_C_FORM_PEM, OPENSSL_C_FORM_DER]:
        raise Exception('The [{:s}] is not supported'.format(form))
    # prepare file path/name
    path_dir = os.path.join(path, OPENSSL_CC_DIR_NAME, hostname)
    path_file = make_c_file_name(path_dir, hostname, name, form)
    return open_cert_stream(path_file)

def get_ca_crt_stream(path, form=OPENSSL_C_FORM_PEM):
    # verify form value
    if not form in [OPENSSL_C_FORM_PEM, OPENSSL_C_FORM_DER]:
        raise Exception('The [{:s}] is not supported'.format(form))
    path_file = make_ca_file_name(path, OPENSSL_C_NAME_CRT, form)
    return open_cert_stream(path_file)
