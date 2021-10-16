from helper import debug, server_message
import json


def disconnect():
    print("CLIENT: Disconnecting")
    exit(1)


class ClientMethod:
    def __init__(self, client_socket):
        self.client_socket = client_socket

        self.response = {
            "username": self.username_response,
            "password": self.password_response,
            "broadcast": self.broadcast_response,
        }
        self.getting_password = True
        self.response_pending = False

    def broadcast_response(self, resp):
        debug("I don't know what to do with broadcast_response")

    # Returns received_message if message was sent successfully
    def send_message(self, command, body=""):
        message = f"{command} {body}"
        # TCP messages can't be empty since the client will just hang and never send anything
        if message == "" or command == "":
            disconnect()

        debug(f"Sending message: {message}")

        self.client_socket.sendall(message.encode())

        # data = self.client_socket.recv(1024)
        #
        # debug(data)
        # received_message = json.loads(data.decode())
        # debug(f"Got message |{received_message}|")
        #
        # if "exit" in received_message:
        #     print("exiting!!!!!")
        #     server_message(received_message["message"])
        #     disconnect()
        received_message = ""
        return received_message

    def handle_username(self):
        self.send_message("username", input("Username: "))

    def username_response(self, resp):
        server_message(resp["message"])
        if resp["blocked"]:
            disconnect()

    def handle_password(self):
        while self.getting_password:
            password = input("Password: ")
            self.response_pending = True
            self.send_message("password", password)

            while self.response_pending:
                pass

    def password_response(self, resp):
        self.getting_password = not resp["passwordMatch"]
        self.response_pending = False
        server_message(resp["message"])

        if resp["blocked"]:
            disconnect()

    def handle_logout(self):

        # spec doesn't require second arg but send_message() will quit program without second arg
        return self.send_message("logout", " ")

