import json


class BaseModel:

    def json(self):
        return json.dumps(self.__dict__)
