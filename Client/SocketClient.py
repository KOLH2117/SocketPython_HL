import socket

HOST = socket.gethostname()
PORT_SEND = 65432

PORT_RECEIVE = 65432

class Client:
    def __init__(self):
         self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)