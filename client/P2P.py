from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from helper import debug, server_message


def handle_disconnect(p2p_obj):
    server_message("Peer has disconnected!")
    p2p_obj.socket = None


def private_peer_message_handler(socket, p2p_obj):
    while True:
        try:
            data = socket.recv(1024)
            debug(data.decode())
            if data.decode() == "":
                handle_disconnect(p2p_obj)
                return

            print(f"{data.decode()}")
        except ConnectionResetError:
            handle_disconnect(p2p_obj)
            break

def send_message(peer_username, socket, message):
    if message == "":
        # TODO: disconnect?
        debug("P2P: Didn't get a message, returning - should I disconnect?")
        return
    message = f"[{peer_username}]: {message}"
    debug(f"sending {message}")
    try:
        socket.sendall(message.encode())
    except ConnectionResetError:
        server_message("Peer is disconnected")


class P2P_server(Thread):
    def __init__(self, server_address, peer_username):
        Thread.__init__(self)
        self.peer_username = peer_username
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind((server_address, 0))

        self.server_address = server_address
        self.server_port = self.server_socket.getsockname()[1]

        self.client_address = ""
        self.socket = None
        self.client_alive = True

    def run(self):
        self.server_socket.listen()
        self.socket, self.client_address = self.server_socket.accept()

        t = Thread(target=private_peer_message_handler, args=(self.socket, self))
        t.setDaemon(True)
        t.start()

    def send_message(self, message):
        send_message(self.peer_username, self.socket, message)

class P2P_client:
    def __init__(self, address, port, peer_username):
        # todo: check if i still need these
        self.peer_username = peer_username
        self.server_address = address
        self.port = port

        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect((address, port))

        t = Thread(target=private_peer_message_handler, args=(self.socket, self))
        t.setDaemon(True)
        t.start()

    def send_message(self, message):
        send_message(self.peer_username, self.socket, message)

class P2P:
    def __init__(self):

        """
        Need a way to create a "server"
        Need a way to create a "client"

        one peer == server, one == client

        peer1 sends request

        peer2 accepts and starts listening (server)
        peer1 sends request to join (client)



        """




        pass