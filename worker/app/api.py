import json
import socket
import requests as r

NODE_IP = "172.20.10.4"
NODE_PORT_API = 7000


def p2p_send_data(data):
    sock = socket.socket()
    sock.connect((NODE_IP, NODE_PORT_API))
    sock.send(data.encode())
    sock.close()

def p2p_create_task(body_json):
    body_json_new = {"msgtype": "p2p_create_task", "data": body_json}
    p2p_send_data(json.dumps(body_json_new))
#
# body_json = {
#   "task_id": 0,
#   "node_ip": NODE_IP,
#   "genom": "ghjksadjasdalksdakjs"
# }
#
# p2p_create_task(body_json)