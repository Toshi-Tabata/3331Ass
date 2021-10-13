from threading import Thread
from helper import debug
from ServerHandlers import ServerHandler


class ClientThread(Thread):
    def __init__(self, client_socket, client_address):
        Thread.__init__(self)
        self.client_address = client_address
        self.client_socket = client_socket

        debug(f"===== New connection created for: {client_address}")
        self.client_alive = True

        self.handler = ServerHandler(client_socket)

    def run(self):
        while self.client_alive:
            data = self.client_socket.recv(1024)
            message = data.decode()
            debug(f"Received message {message}")

            # Empty message from client indicates that the client has disconnected
            if message == "":
                self.client_alive = False
                debug(f"User disconnected: {self.client_address}")
                continue

            command, body = message.split(" ", 1)

            if command in self.handler.commands:
                self.handler.commands[command](body)

            else:
                debug(f"[recv] Echoing: {message}")
                self.client_socket.send(message.encode())


