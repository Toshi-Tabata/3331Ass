from helper import debug, server_message
import json


def disconnect():
    print("CLIENT: Disconnecting")
    exit(1)


class ClientMethod:
    def __init__(self, client_socket):
        self.client_socket = client_socket

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
        username = input("Username: ")
        resp = self.send_message("username", username)
        server_message(resp["message"])

        if resp["blocked"]:
            disconnect()

    def handle_password(self):
        gettingPassword = True
        while gettingPassword:

            password = input("Password: ")

            resp = self.send_message("password", password)
            server_message(resp["message"])

            gettingPassword = not resp["passwordMatch"]
            if resp["blocked"]:
                disconnect()

    def handle_logout(self):

        # spec doesn't require second arg but send_message() will quit program without second arg
        return self.send_message("logout", "user")

