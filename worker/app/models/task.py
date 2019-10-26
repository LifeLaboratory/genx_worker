from models.base import BaseModel


class Task(BaseModel):
    def __init__(self, id, nodeId, status):
        self.id = id
        self.nodeId = nodeId
        self.status = status
        print('task created')

