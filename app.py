from flask import Flask
from flask_cors import CORS
import config as cfg
from models.worker import Worker
def factory():
    app = Flask(__name__)
    CORS(app)
    return app

def create_worker(name):
    worker = Worker(name)
    return worker

if __name__ == '__main__':
    app = factory()
    worker = create_worker(name=cfg.name)
    app.run(host=cfg.host, port=cfg.port, threaded=True)
