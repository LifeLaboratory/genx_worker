from flask import request,  abort, Blueprint
from db.task import Provider
import json
task = Blueprint('task', __name__)

@task.route('/task', methods=["POST"])
def submit_task():
    body = request.json
    answer = Provider.create_task(body)
    return str(answer)

@task.route('/tasks', methods=["GET"])
def get_tasks():
    answer = Provider.get_tasks({})
    return json.dumps(answer)
