from models.base import BaseModel
import time
from models.cert import Cert
import hashlib


class Worker(BaseModel):
    def __init__(self, common_name):
        expired_time = str(int(time.time()))
        _hash = str(hashlib.md5((';'.join([common_name, expired_time])).encode()))
        _cert = ';'.join([expired_time, common_name, _hash])
        self.cert = Cert(_cert)
        self.queue_tasks = []
        self.finished_tasks = []