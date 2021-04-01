import random
import socket

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', 12000))

while True:
    rand = random.randint(0, 10)
    (client_socket, address) = server_socket.accept()
    data = client_socket.recvfrom(1024)
