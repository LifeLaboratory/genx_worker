import json
import requests as r
import decimal
from twisted.internet.endpoints import TCP4ServerEndpoint, connectProtocol, TCP4ClientEndpoint
from twisted.internet.protocol import Protocol, Factory,ClientCreator
from twisted.internet import reactor
from uuid import uuid4
from time import time
import config as cfg
from twisted.internet.task import LoopingCall

BOOTSTRAP_IP = cfg.controller_host
BOOTSTRAP_PORT = cfg.controller_port
NODE_PORT_API = cfg.port
HOST_IP = cfg.host

def pi():
    """
    Compute Pi to the current precision.

    Examples
    --------
    >>> print(pi())
    3.141592653589793238462643383

    Notes
    -----
    Taken from https://docs.python.org/3/library/decimal.html#recipes
    """
    decimal.getcontext().prec += 2  # extra digits for intermediate steps
    three = decimal.Decimal(3)      # substitute "three=3.0" for regular floats
    lasts, t, s, n, na, d, da = 0, three, 3, 1, 0, 0, 24
    while s != lasts:
        lasts = s
        n, na = n + na, na + 8
        d, da = d + da, da + 32
        t = (t * n) / d
        s += t
    decimal.getcontext().prec -= 2
    return +s

genom = "asdasdasdas"
status = True
generate_nodeid = lambda: str(uuid4())

def gotListRequest(p,data):
    p.send_get_list_request(data)

def gotPeerTask(p,data):
    p.send_task_request(data)

def gotProtocol(p):
    """The callback to start the protocol exchange. We let connecting
    nodes start the hello handshake"""
    p.send_hello()

class APIProtocol(Protocol):
    def __init__(self, factory):
        self.factory = factory

    def connectionMade(self):
        self.remote_ip = self.transport.getPeer()
        print("API Connection from", self.transport.getPeer())

    def connectionLost(self, reason):
        print(self.remote_ip, "API disconnected")

    def dataReceived(self, data):
        for line in data.splitlines():
            line = line.strip()
            msgtype = json.loads(line)['msgtype']
            if msgtype == "p2p_create_task":
                self.handle_p2p_create_task(json.loads(line)['data'])

    def handle_p2p_create_task(self,data):
        print("handle_p2p_create_task")
        c = ClientCreator(reactor, ClientProtocol)
        c.connectTCP(BOOTSTRAP_IP, BOOTSTRAP_PORT).addCallback(gotListRequest,data=data)

    def send_get_list_request(self,data):
        str = json.dumps({'msgtype': 'get_list_request', 'data':data}).encode('utf-8')
        self.transport.write(str + b"\n")

class ServerProtocol(Protocol):
    def __init__(self, factory):
        self.factory = factory
        self.remote_nodeid = None
        self.nodeid = self.factory.nodeid

    def connectionMade(self):
        self.remote_ip = self.transport.getPeer()
        print("Connection from", self.transport.getPeer())

    def connectionLost(self, reason):
        print(self.nodeid, "disconnected")

    def dataReceived(self, data):
        for line in data.splitlines():
            line = line.strip()
            msgtype = json.loads(line)['msgtype']
            if msgtype == "get_list_request":
                self.handle_get_list_request()
            elif msgtype == "get_list_response":
                self.handle_get_list_response(json.loads(line)['peers'])
            elif msgtype == "send_task_request":
                self.handle_task_request(json.loads(line)['data'])
            elif msgtype == "send_task_response":
                self.handle_task_response(json.loads(line)['status'])

    def send_hello(self):
        hello = json.dumps({'nodeid': self.nodeid, 'msgtype': 'hello'}).encode('utf-8')
        self.transport.write(hello + b"\n")

    def send_get_list_request(self,data):
        str = json.dumps({'msgtype': 'get_list_request', 'data':data}).encode('utf-8')
        self.transport.write(str + b"\n")

    def send_get_list_response(self, peers):
        pong = json.dumps({'msgtype': 'get_list_response', 'peers':peers}).encode('utf-8')
        self.transport.write(pong + b"\n")

    def send_task_request(self):
        pong = json.dumps({'msgtype': 'send_task_request','data':genom}).encode('utf-8')
        self.transport.write(pong + b"\n")

    def send_task_response(self,data):
        print("Send task response status", status)
        r.post('http://' + data["node_ip"]+"/task/result", data=json.dumps({"task_id":data["task_id"], "status": status}))

    def handle_get_list_request(self):
        print("Got get_list request", self.remote_nodeid)
        print("Peers", self.factory.peers)
        self.send_get_list_response(self.factory.peers)

    def handle_get_list_response(self, peers, data):
        print("Got get_list response", self.remote_nodeid)
        print("Peers", peers)

    def handle_hello(self, hello):
        hello = json.loads(hello)
        self.remote_nodeid = hello["nodeid"]
        if self.remote_nodeid == HOST_IP:
            print("Connected to myself.")
            self.transport.loseConnection()
        else:
            self.factory.peers[self.remote_nodeid] = (self.remote_ip.host,self.remote_ip.port)
            self.lc_ping.start(60)

    def handle_task_request(self, data):
        print("Task request", data)
        pin = pi()
        self.send_task_response(data)

    def handle_task_response(self, status):
        print("Task response status", status)

class ClientProtocol(Protocol):
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
                self.handle_get_list_response(json.loads(line)['peers'], json.loads(line)['data'])
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

    def send_get_list_request(self,data):
        print("send_get_list_request")
        str = json.dumps({'msgtype': 'get_list_request', 'data':data}).encode('utf-8')
        self.transport.write(str + b"\n")

    def send_get_list_response(self, peers):
        pong = json.dumps({'msgtype': 'get_list_request', 'peers': peers}).encode('utf-8')
        self.transport.write(pong + b"\n")

    def send_task_request(self, data):
        print("Send task",data['genom'])
        str = json.dumps({'msgtype': 'send_task_request', 'data': data}).encode('utf-8')
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

    def handle_get_list_response(self, peers, data):
        print("Got get_list response", self.remote_nodeid)
        print("Peers", peers)
        for peer in peers:
            if list(peer.keys())[0] == HOST_IP:
                continue
            c = ClientCreator(reactor, ClientProtocol)
            c.connectTCP(list(peer.values())[0], 6000).addCallback(gotPeerTask,data=data)

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

    def handle_api_get_task(self, data):
        self.send_get_list_request()

class MyFactory(Factory):
    def startFactory(self):
        self.peers = {}
        self.nodeid = generate_nodeid()

    def buildProtocol(self, addr):
        return ServerProtocol(self)

class APIFactory(Factory):
    def startFactory(self):
        self.peers = {}

    def buildProtocol(self, addr):
        return APIProtocol(self)

def node_run():
    print('Node run ...')
    endpoint = TCP4ServerEndpoint(reactor, 6000, interface=cfg.host)
    endpoint.listen(MyFactory())

    endpoint_2 = TCP4ServerEndpoint(reactor, 7000, interface=cfg.host)
    endpoint_2.listen(APIFactory())

    c = ClientCreator(reactor, ClientProtocol)
    c.connectTCP(BOOTSTRAP_IP, BOOTSTRAP_PORT).addCallback(gotProtocol)
    reactor.run()