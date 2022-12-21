import socket

class Socket:
    def __init__(self,port):
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(("0.0.0.0", self.port))
        self.s.listen(1)

    def wait_connect(self):
        self.conn, address = self.s.accept()
        print(f"Connection from {address}:{self.port}")
        self.conn.settimeout(10)
        return self.recieve()

    def recieve(self):
        req = self.conn.recv(4096)
        string_data = req.decode("utf-8")
        return string_data

    def send(self,data):
        self.conn.send(data.encode("utf-8"))
