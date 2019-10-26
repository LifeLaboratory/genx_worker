from model.base import BaseModel


class TaskResult(BaseModel):
    def __init__(self, taskId, data):
        self.taskId = taskId
        self.data = data
