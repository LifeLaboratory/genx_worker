from flask import request,  abort, Blueprint


cert = Blueprint('cert', __name__)

@cert.route('/cert', methods=["GET"])
def cert_request():
    from app import worker
    return worker.cert.json()