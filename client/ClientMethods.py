from threading import Thread

from helper import debug, server_message
import time
import json
from client.P2P import P2P_server, P2P_client


def disconnect(quiet=False):
    if not quiet:
        print("CLIENT: Disconnecting")
    exit(1)


class ClientMethod:
    def __init__(self, client_socket):
        self.client_socket = client_socket
        self.p2p_socket = None

        self.username = ""

        # Handle the server's response to these commands
        self.response = {
            "username": self.username_response,
            "password": self.password_response,
            "broadcast": self.broadcast_response,
            "blacklist": self.blacklist_response,
            "server": self.server_response,
            "startprivate_ans": self.startprivate_response,
            "startprivate_init": self.startprivate_init,
            "private": self.private_response,
            "exit": self.exit_response
        }

        # Handle the commands issued by the user
        self.handle = {
            "logout": self.exit_response,
            "private": self.handle_private,
            "y": self.handle_startprivate_accept,
            "n": self.handle_startprivate_decline,
            "": self.exit_response,
        }

        self.getting_password = True
        self.response_pending = True
        self.blocked = False

        # TODO: is this useless info?
        self.peer_username = ""
        self.peer_address = ""
        self.peer_port = ""

    def startprivate_response(self, resp):
        debug(f"RESPONSE WAS |{resp}|")

        if not all(key in resp for key in ("message", "username", "address", "port", "OK")):
            debug("Server sent a malformed message object")
            return

        self.broadcast_response(resp)

        if not resp["OK"]:
            return

        self.peer_username = resp["username"]
        self.peer_address = resp["address"]
        self.peer_port = resp["port"]
        debug(f"!!@!@@!@!@ peer: {self.peer_username}")


        debug(f"set {self.peer_username, self.peer_address, self.peer_port}")

    def startprivate_helper(self, did_accept):
        if not self.peer_username:
            server_message("You have no pending requests for private messages!")

        if self.p2p_socket is None:
            port = ""
            addr = ""
        else:
            port = self.p2p_socket.server_port
            addr = self.p2p_socket.server_address

        self.send_message("startprivate_resp", f"{did_accept} {self.peer_username} {port} {addr}")

        if not did_accept:
            self.peer_username = ""
            self.peer_address = ""
            self.peer_port = ""

    def handle_startprivate_accept(self, command, body=None):
        self.p2p_socket = P2P_server(self.peer_address, self.username)
        self.p2p_socket.setDaemon(True)
        self.p2p_socket.start()

        server_message(f"You have accepted a connection with {self.peer_username}!")
        debug(f"<><><><><> setting p2p socket: {self.p2p_socket} <><>><><>")

        self.startprivate_helper(True)

    def handle_startprivate_decline(self, command, body=None):
        self.startprivate_helper(False)

    def startprivate_init(self, resp):

        if not all(key in resp for key in ("message", "username", "address", "port", "OK")):
            debug("Server sent a malformed message object")
            return
        if not resp["OK"]:
            server_message(resp["message"])
            return

        self.peer_username = resp["username"]
        self.peer_address = resp["address"]
        self.peer_port = int(resp["port"])
        self.broadcast_response(resp)

        debug(f"!!@!@@!@!@ peer: {self.peer_username}")

        debug("connect to the peer's server")

        debug(f"FOR CLIENT: {self.peer_username}")
        self.p2p_socket = P2P_client(self.peer_address, self.peer_port, self.username)
        #TODO: create a thread that listens for messages

        debug(f"!<><><><><!> setting p2p socket: {self.p2p_socket} <><>><><>")


    def private_response(self, resp):

        # TODO parse the message received, reuse broadcast_response() - could probs just use this directly
        pass

    def handle_private(self, command, body=None):
        if self.p2p_socket is None or self.p2p_socket.socket is None:
            # TODO: did I need to reset this anywhere else?
            self.p2p_socket = None
            self.peer_port = ""
            self.peer_username = ""
            self.peer_address = ""
            server_message("You need to start a private session with a user first!")
            return
        if body is None or len(body.split(" ", 1)) != 2:
            server_message("Usage: private <recipient> <message>")
            return

        recipient, message = body.split(" ", 1)

        # TODO:
        # ping server if valid
        # check if user is still alive using socket.connect_ex((addr, port)) == 0
        self.p2p_socket.send_message(message)

    def await_reponse(self):
        while self.response_pending:
            time.sleep(0.5)  # prevent huge CPU usage

    def broadcast_response(self, resp):
        if resp["from"] != "":
            print(f"<{resp['from']}>: {resp['message']}")
        else:
            server_message(resp["message"])

    def server_response(self, resp):
        server_message(resp["message"])

    def exit_response(self, resp=None, body=None):
        debug("Exiting")
        self.response_pending = False
        self.blocked = True

        if resp is not None and resp != "" and resp != "logout":
            server_message(resp["message"])
        disconnect()

    # Returns received_message if message was sent successfully
    def send_message(self, command, body=None):
        message = f"{command} {body}"
        # TCP messages can't be empty since the client will just hang and never send anything
        if message == "" or command == "":
            disconnect()

        debug(f"Sending message: |{message}|")

        self.client_socket.sendall(message.encode())

    def handle_username(self):
        username = input("Username: ")
        self.username = username
        if username == "":
            disconnect()
        self.send_message("username", username)

    def username_response(self, resp):
        server_message(resp["message"])
        self.response_pending = False
        if resp["blocked"]:
            self.blocked = True
            disconnect()

    def handle_password(self):
        while self.getting_password:
            self.await_reponse()

            if self.blocked:
                disconnect(True)

            password = input("Password: ")
            if password == "":
                disconnect()
            self.response_pending = True
            self.send_message("password", password)
            self.await_reponse()

    def password_response(self, resp):
        self.getting_password = not resp["passwordMatch"]
        self.response_pending = False
        server_message(resp["message"])

        if resp["blocked"]:
            self.blocked = True
            disconnect()

    # def handle_blacklist(self, username):
    #     self.send_message("blacklist", username)

    def blacklist_response(self, resp):
        server_message(resp["message"])

    #
    # def handle_logout(self, body=None):
    #     # spec doesn't require second arg but send_message() will quit program without second arg
    #     return self.send_message("logout", "None")

