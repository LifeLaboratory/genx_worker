from flask import Flask
from flask_cors import CORS


def factory():
    app = Flask(__name__)
    CORS(app)
    return app


if __name__ == '__main__':
    app = factory()
    app.run(host='0.0.0.0', port=8080, threaded=True)
