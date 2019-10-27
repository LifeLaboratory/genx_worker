from flask import request, Blueprint
from db.task_result import Provider
task_result = Blueprint('task_result', __name__)

@task_result.route('/task/result', methods=["POST"])
def create_task_result():
    body = request.json
    answer = Provider.create_task_result(body)
    return str(answer)

