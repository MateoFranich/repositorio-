import certifi
import os
import ssl

def update_certificates():
    cafile = certifi.where()

    os.environ['SSL_CERT_FILE'] = cafile
    os.environ['SSL_CERT_DIR'] = os.path.dirname(cafile)

    ssl._create_default_https_context = ssl.create_default_context

update_certificates()
