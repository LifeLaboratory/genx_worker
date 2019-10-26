import json
from twisted.internet.endpoints import TCP4ServerEndpoint, connectProtocol, TCP4ClientEndpoint
from twisted.internet.protocol import Protocol, Factory,ClientCreator
from twisted.internet import reactor
from uuid import uuid4
from time import time
from twisted.internet.task import LoopingCall

BOOTSTRAP_IP = "127.0.0.1"
BOOTSTRAP_PORT = 5999

genom = "asdasdasdas"
status = True
generate_nodeid = lambda: str(uuid4())

def gotPeerTask(p):
    p.send_task_request()

def gotProtocol(p):
    """The callback to start the protocol exchange. We let connecting
    nodes start the hello handshake"""
    p.send_hello()
    p.send_get_list_request()

class MyProtocol(Protocol):
    def __init__(self):
        self.state = "HELLO"
        self.nodeid = generate_nodeid()

    def connectionMade(self):
        self.remote_nodeid = self.transport.getPeer()
        print("Connection from", self.transport.getPeer())

    def connectionLost(self, reason):
        print(self.nodeid, "disconnected", reason)

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
                self.handle_get_list_response([json.loads(line)['peers']])
            elif msgtype == "send_task_request":
                self.handle_task_request(json.loads(line)['task'])
            elif msgtype == "send_task_response":
                self.handle_task_response(json.loads(line)['status'])
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
        pong = json.dumps({'msgtype': 'get_list_request'}).encode('utf-8')
        self.transport.write(pong + b"\n")

    def send_get_list_response(self, peers):
        pong = json.dumps({'msgtype': 'get_list_request', 'peers': peers}).encode('utf-8')
        self.transport.write(pong + b"\n")

    def send_task_request(self):
        print("Send task",genom)
        str = json.dumps({'msgtype': 'send_task_request', 'task': genom}).encode('utf-8')
        self.transport.write(str + b"\n")

    def send_task_response(self):
        print("Task response", genom)
        str = json.dumps({'msgtype': 'send_task_response', 'status':status}).encode('utf-8')
        self.transport.write(str + b"\n")

    def handle_ping(self):
        self.send_pong()

    def handle_pong(self):
        print("Got pong from", self.remote_nodeid)
        ###Update the timestamp
        self.lastping = time()

    def handle_get_list_response(self, peers):
        print("Got get_list response", self.remote_nodeid)
        print("Peers", peers)
        for peer in peers:
            if list(peer.keys())[0] == self.nodeid:
                continue
            c = ClientCreator(reactor, MyProtocol)
            c.connectTCP(list(peer.values())[0][0], 6000).addCallback(gotPeerTask)

    def handle_hello(self, hello):
        hello = json.loads(hello)
        self.remote_nodeid = hello["nodeid"]
        if self.remote_nodeid == self.nodeid:
            print("Connected to myself.")
            self.transport.loseConnection()
        else:
            self.lc_ping.start(60)

    def handle_task_request(self, task):
        print("Task request", task)
        self.send_task_response()

    def handle_task_response(self, status):
        print("Task response status", status)

class MyFactory(Factory):
    def startFactory(self):
        self.peers = {}
        self.nodeid = generate_nodeid()

    def buildProtocol(self, addr):
        return MyProtocol(self)

print('Node run ...')
endpoint = TCP4ServerEndpoint(reactor, 6000, interface="172.20.10.4")
endpoint.listen(MyFactory())
c = ClientCreator(reactor, MyProtocol)
c.connectTCP(BOOTSTRAP_IP, BOOTSTRAP_PORT, bindAddress="172.20.10.4").addCallback(gotProtocol)
reactor.run()