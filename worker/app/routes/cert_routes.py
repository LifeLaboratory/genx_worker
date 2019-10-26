from flask import Blueprint


cert = Blueprint('cert', __name__)

@cert.route('/cert', methods=["GET"])
def cert_request():
    from worker.app.app import worker
    return worker.cert.json()