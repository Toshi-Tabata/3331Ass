from helper import debug, server_message
import time
import json


def disconnect(quiet=False):
    if not quiet:
        print("CLIENT: Disconnecting")
    exit(1)


class ClientMethod:
    def __init__(self, client_socket):
        self.client_socket = client_socket

        self.response = {
            "username": self.username_response,
            "password": self.password_response,
            "broadcast": self.broadcast_response,
            "blacklist": self.blacklist_response,
            "server": self.server_response,
            "exit": self.exit_response
        }

        self.handle = {
            "logout": self.exit_response,
            "": self.exit_response,
        }

        self.getting_password = True
        self.response_pending = True
        self.blocked = False

    # def handle_whoelse(self, body):
    #     self.send_message("whoelse")

    # def handle_whoelsesince(self, body):
    #     try:
    #         self.send_message("whoelsesince", int(body))
    #     except ValueError:
    #         server_message("usage: whoelsesince <integer>")

    def await_reponse(self):
        while self.response_pending:
            time.sleep(0.5)  # prevent huge CPU usage

    # def handle_blacklist(self, body):
    #     self.send_message("blacklist", body)
    #
    # def handle_unblock(self, body):
    #     self.send_message("unblock", body)

    def broadcast_response(self, resp):
        if resp["from"] != "":
            print(f"<{resp['from']}>: {resp['message']}")
        else:
            server_message(resp["message"])

    def server_response(self, resp):
        server_message(resp["message"])

    def exit_response(self, resp=None, body=None):
        debug("Exiting")

        if resp is not None and resp != "":
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

