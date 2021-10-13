from helper import debug


class ClientMethod:
    def __init__(self, client_socket):
        self.client_socket = client_socket

    # Returns received_message if message was sent successfully
    def send_message(self, command, body):
        message = f"{command} {body}"
        # TCP messages can't be empty since the client will just hang and never send anything
        if message == "" or command == "" or body == "":
            debug("Disconnecting")
            return False

        debug(f"Sending message: {message}")

        self.client_socket.sendall(message.encode())

        data = self.client_socket.recv(1024)
        received_message = data.decode()

        debug(f"Got message |{received_message}|")

        return received_message

    def handle_username(self, username):
        # TODO: handle what happens based on response from server
        return self.send_message("username", username)

    def handle_password(self, password):
        # TODO: handle what should happen
        return self.send_message("password", password)

    def handle_logout(self):

        # spec doesn't require second arg but send_message() will quit program without second arg
        return self.send_message("logout", "user")