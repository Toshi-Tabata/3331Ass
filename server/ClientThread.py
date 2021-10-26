from threading import Thread
from helper import debug
from ServerHandlers import ServerHandler
import time
import json


# Creates thread for each client that joins`
class ClientThread(Thread):
    def __init__(self, client_socket, client_address, block_duration, timeout, clients):
        Thread.__init__(self)
        self.client_address = client_address
        self.client_socket = client_socket

        debug(f"===== New connection created for: {client_address}")

        self.handler = ServerHandler(client_socket, clients, block_duration, self, *client_address)

        self.timeout = int(timeout)
        self.lastActive = time.time()
        self.logged_in_time = time.time()
        self.clients = clients

    def is_active(self):
        return time.time() - self.lastActive < self.timeout

    def run(self):
        while self.is_active():
            try:
                data = self.client_socket.recv(1024)
            except ConnectionResetError:
                self.handler.logout()
                return
            message = data.decode()
            debug(f"Received message |{message}|")

            # Empty message from client indicates that the client has disconnected
            if message == "" or not self.is_active():
                debug(f"User disconnected: {self.client_address}")
                break

            debug(f"|{message}|")
            command, body = message.split(" ", 1)
            debug(f"|{command}|{body}|")
            if command in self.handler.commands:
                self.handler.commands[command](body)
                self.lastActive = time.time()

            else:
                message = {
                    "command": "server",
                    "message": "That command doesn't exist!"
                }
                self.client_socket.sendall(json.dumps(message).encode())

        self.client_socket.sendall(json.dumps({"command": "exit", "message": "User timed out or disconnected"}).encode())
        self.handler.logout()

