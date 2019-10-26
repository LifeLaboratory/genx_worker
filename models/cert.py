from models.base import BaseModel
import time


class Cert(BaseModel):
    def __init__(self, cert):
        cert_parse = cert.split(';')
        self.time = cert_parse[0]
        self.common_name = cert_parse[1]
        self.hash = cert_parse[2]


    @staticmethod
    def check_expired_time(cert):
        now = int(time.time())
        if now >= cert.time:
            res = False
        else:
            res = True

        return res
