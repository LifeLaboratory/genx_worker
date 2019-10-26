import json
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
from uuid import uuid4
generate_nodeid = lambda: str(uuid4())

from time import time

from twisted.internet.task import LoopingCall


class MyProtocol(Protocol):
    def __init__(self, factory):
        self.factory = factory
        self.state = "HELLO"
        self.remote_nodeid = None
        self.nodeid = self.factory.nodeid
        self.lc_ping = LoopingCall(self.send_ping)
        self.lastping = None

    def connectionMade(self):
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
            if self.state == "HELLO" or msgtype == "hello":
                self.handle_hello(line)
                self.state = "READY"
            elif msgtype == "ping":
                self.handle_ping()
            elif msgtype == "pong":
                self.handle_pong()

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

    def handle_ping(self):
        self.send_pong()


    def handle_pong(self):
        print("Got pong from", self.remote_nodeid)
        ###Update the timestamp
        self.lastping = time()


    def handle_hello(self, hello):
        hello = json.loads(hello)
        self.remote_nodeid = hello["nodeid"]
        if self.remote_nodeid == self.nodeid:
            print
            "Connected to myself."
            self.transport.loseConnection()
        else:
            self.factory.peers[self.remote_nodeid] = self
            self.lc_ping.start(60)


class MyFactory(Factory):
    def startFactory(self):
        self.peers = {}
        self.nodeid = generate_nodeid()

    def buildProtocol(self, addr):
        return MyProtocol(self)

print('wait...')
endpoint = TCP4ServerEndpoint(reactor, 5999)
endpoint.listen(MyFactory())
reactor.run()
