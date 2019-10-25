from flask import request,  abort
from models.task_result import TaskResult
from app import app


@app.route('/ReceiveTaskResult', methods=["POST"])
def receive_task():
    task = TaskResult(request.json)
    return "RECEIVE"