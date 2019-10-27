from flask import request, Blueprint
from db.task import Provider
import json
import config
import string
import random
import api
task = Blueprint('task', __name__)

@task.route('/task', methods=["POST"])
def submit_task():
    body = request.json
    answer = Provider.create_task(body)
    N = int(random.random()*100)
    genom = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))
    task = {'gemom':genom,'node_ip': config.host, 'task_id': answer['id']}
    api.p2p_create_task(task)
    return json.dumps(answer)

@task.route('/tasks', methods=["GET"])
def get_tasks():
    answer = Provider.get_tasks({})
    return json.dumps(answer)
