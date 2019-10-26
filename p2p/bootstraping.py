import json
from twisted.internet.endpoints import TCP4ServerEndpoint, connectProtocol, TCP4ClientEndpoint
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
from uuid import uuid4
from time import time
from twisted.internet.task import LoopingCall

BOOTSTRAP_IP = "127.0.0.1"
BOOTSTRAP_PORT = 5999
genom = "123"
status = True
generate_nodeid = lambda: str(uuid4())

def gotProtocol(p):
    """The callback to start the protocol exchange. We let connecting
    nodes start the hello handshake"""
    p.send_hello()

class MyProtocol(Protocol):
    def __init__(self, factory):
        self.factory = factory
        self.remote_nodeid = None
        self.nodeid = self.factory.nodeid
        self.lc_ping = LoopingCall(self.send_ping)
        self.lastping = None

    def connectionMade(self):
        self.remote_ip = self.transport.getPeer()
        print("Connection from", self.transport.getPeer())

    def connectionLost(self, reason):
        if self.remote_nodeid in self.factory.peers:
            self.factory.peers.pop(self.remote_nodeid)
            self.lc_ping.stop()
        print(self.nodeid, "disconnected")

    def dataReceived(self, data):
        for line in data.splitlines():
            line = line.strip()
            msgtype = json.loads(line)['msgtype']
            if msgtype == "hello":
                self.handle_hello(line)
            elif msgtype == "ping":
                self.handle_ping()
            elif msgtype == "pong":
                self.handle_pong()
            elif msgtype == "get_list_request":
                self.handle_get_list_request()
            elif msgtype == "get_list_response":
                self.handle_get_list_response(json.loads(line)['peers'])

    def send_hello(self):
        hello = json.dumps({'nodeid': self.nodeid, 'msgtype': 'hello'}).encode('utf-8')
        self.transport.write(hello + b"\n")

    def send_ping(self):
        ping = json.dumps({'msgtype': 'ping'}).encode('utf-8')
        print("Pinging", self.remote_nodeid)
        self.transport.write(ping + b"\n")

    def send_pong(self):
        pong = json.dumps({'msgtype': 'pong'}).encode('utf-8')
        self.transport.write(pong + b"\n")

    def send_get_list_request(self):
        pong = json.dumps({'msgtype': 'get_list'}).encode('utf-8')
        self.transport.write(pong + b"\n")

    def send_get_list_response(self, peers):
        pong = json.dumps({'msgtype': 'get_list_response', 'peers':peers}).encode('utf-8')
        self.transport.write(pong + b"\n")

    def send_task_request(self):
        pong = json.dumps({'msgtype': 'task_request','data':genom}).encode('utf-8')
        self.transport.write(pong + b"\n")

    def send_task_response(self):
        pong = json.dumps({'msgtype': 'task_response','status':status}).encode('utf-8')
        self.transport.write(pong + b"\n")

    def handle_ping(self):
        self.send_pong()

    def handle_pong(self):
        print("Got pong from", self.remote_nodeid)
        ###Update the timestamp
        self.lastping = time()

    def handle_get_list_request(self):
        print("Got get_list request", self.remote_nodeid)
        print("Peers", self.factory.peers)
        self.send_get_list_response(self.factory.peers)

    def handle_get_list_response(self, peers):
        print("Got get_list response", self.remote_nodeid)
        print("Peers", peers)

    def handle_hello(self, hello):
        hello = json.loads(hello)
        self.remote_nodeid = hello["nodeid"]
        if self.remote_nodeid == self.nodeid:
            print("Connected to myself.")
            self.transport.loseConnection()
        else:
            self.factory.peers[self.remote_nodeid] = (self.remote_ip.host,self.remote_ip.port)
            self.lc_ping.start(60)

    def handle_task_request(self,status):
        print("Task request status", status)

    def handle_task_response(self,status):
        print("Task response status", status)

class MyFactory(Factory):
    def startFactory(self):
        self.peers = {}
        self.nodeid = generate_nodeid()

    def buildProtocol(self, addr):
        return MyProtocol(self)

print('Bootstraping Node run ...')
endpoint = TCP4ServerEndpoint(reactor, BOOTSTRAP_PORT)
endpoint.listen(MyFactory())
reactor.run()
