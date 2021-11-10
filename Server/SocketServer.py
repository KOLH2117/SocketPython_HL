import socket
import threading

HOST = "127.0.0.1"
PORT = 65432

class SocketServer:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_list = []
    
    def start_server(self):
        try:
            self.sock.bind((HOST, PORT))
            self.sock.listen(5) # 5 try to connect to the server
        except socket.error:
            self.sock.close()
    
    def accept_incoming_connections(self):
        """Luôn lặp lại"""
        while True:
            try:
                """Chấp nhận 1 kết nối từ client"""
                client, client_address = self.sock.accept()
            except socket.error:
                """Nếu client đó kết nối bị lỗi thì thử lại"""
                continue
            else:
                """Bắt đầu luồng để xử lí yêu cầu của client"""
                threading.Thread(target=self.handle_client, args=(client,)).start() 
    
    def handle_client(self, client_socket):
        return;