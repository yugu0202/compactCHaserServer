import socket
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

args = sys.argv
s.connect(("127.0.0.1",int(args[1])))

s.send(args[2].encode("utf-8"))

while True:
    req = s.recv(4096)
    string_data = req.decode("utf-8")

    print(string_data)

    s.send("gr\r\n".encode("utf-8"))

