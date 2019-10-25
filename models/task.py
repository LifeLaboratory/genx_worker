from models.base import BaseModel


class Task(BaseModel):
    def __init__(self, json):
        print('task created')

