from models.base import BaseModel
import time


class Cert(BaseModel):
    def __init__(self, cert):
        cert_parse = cert.split(';')
        self.expired_time = str(int(cert_parse[0]))
        self.common_name = cert_parse[1]
        self.hash = cert_parse[2]


    @staticmethod
    def check_expired_time(cert):
        now = int(time.time())
        if now >= cert.expired_time:
            res = False
        else:
            res = True

        return res

    def json(self):
        return ';'.join([self.expired_time, self.common_name, self.hash])
