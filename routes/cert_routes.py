from flask import request,  abort
from models.task import Task
from app import app

@app.route('/SubmitTask', methods=["POST"])
def submit_task():
    task = Task(request.json)
    return "SUBMIT"

@app.route('/ReceiveTask', methods=["POST"])
def receive_task():
    task = Task(request.json)
    return "RECEIVE"