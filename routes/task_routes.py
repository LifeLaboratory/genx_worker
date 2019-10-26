from flask import request,  abort
from models.cert import Cert
from app import app

@app.route('/CertRequest', methods=["GET"])
def cert_request():
    return "SUBMIT"
