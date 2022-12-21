import socket
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect(("127.0.0.1",2009))

s.send("hello".encode("utf-8"))

req = s.recv(4096)
string_data = req.decode("utf-8")

print(string_data)

time.sleep(11)

s.send("hello".encode("utf-8"))
