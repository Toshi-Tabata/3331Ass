"""
    Sample code for Multi-Threaded Server
    Python 3
    Usage: python3 exampleServer.py 12000
    coding: utf-8

    Author: Toshi Tabata (z5280803)

    Rewritten example of a python3 socket client. Original program from Wei Song.
"""

from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import sys

# acquire server host and port from command line parameter
if len(sys.argv) != 2:
    print(f"\n===== Usage: python3 {sys.argv[0]} <server port> =====\n")
    exit(0)

SERVER_HOST = "127.0.0.1"
SERVER_PORT = int(sys.argv[1])
SERVER_ADDRESS = (SERVER_HOST, SERVER_PORT)

# define socket for the server side and bind address
SERVER_SOCKET = socket(AF_INET, SOCK_STREAM)
SERVER_SOCKET.bind(SERVER_ADDRESS)


# Multi-thread class for client
# - Create a separate class instance for each client connecting
# - Each class instance will be its own thread
class ClientThread(Thread):
    def __init__(self, client_socket, client_address):
        Thread.__init__(self)
        self.client_address = client_address
        self.client_socket = client_socket

        print(f"===== New connection created for: {client_address}")
        self.client_alive = True

    def run(self):
        while self.client_alive:
            data = self.client_socket.recv(1024)
            message = data.decode()
            print(f"Received message {message}")

            # Empty message from client indicates that the client has disconnected
            if message == "":
                self.client_alive = False
                print(f"User disconnected: {self.client_address}")

            # handle message from the client
            if message == "login":
                print("[recv] New login request")
                self.process_login()
            else:
                print(f"[recv] Echoing: {message}")
                self.client_socket.send(message.encode())

    def process_login(self):
        message = "You sent a login request!"
        print(f"[sending] {message}")
        self.client_socket.send(message.encode())


print("\n===== Server is running =====")
print("===== Waiting for connection request from clients...=====")

while True:
    SERVER_SOCKET.listen()
    clientThread = ClientThread(*SERVER_SOCKET.accept())
    clientThread.start()
