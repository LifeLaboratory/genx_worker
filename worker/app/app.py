from flask import Flask
from flask_cors import CORS
import config as cfg
from models.worker import Worker
from routes.task_routes import task
from routes.task_result_routes import task_result
from routes.cert_routes import cert
import threading
import node
def factory():
    app = Flask(__name__)
    CORS(app)
    register_api(app)
    return app


def register_api(app):
    app.register_blueprint(task)
    app.register_blueprint(cert)
    app.register_blueprint(task_result)


def create_worker(name):
    worker = Worker(name)
    return worker

def flask_run():
    app.run(host=cfg.host, port=cfg.port, threaded=True)

worker = create_worker(cfg.name)


if __name__ == '__main__':
    app = factory()
    threading.Thread(target=flask_run).start()
    node.node_run()

