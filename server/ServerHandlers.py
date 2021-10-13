class ServerHandler:
    def __init__(self, client_socket):
        self.commands = {
            "username": self.handle_username,
            "password": self.handle_password
        }
        self.client_socket = client_socket
        self.userExists = False
        self.username = ""
        self.password = ""
        self.attempts = 3

    def handle_username(self, username):
        self.username = username
        with open("credentials.txt", "r+") as file:
            for line in file:
                user, pwd = line.split()

                if user == username:
                    self.userExists = True

            if self.userExists:
                message = f"Hello {username}, what is your password?"
                self.password = pwd
            else:
                message = f"Creating a new account for {username}. Choose a password."

        self.client_socket.send(message.encode())

    def handle_password(self, password):
        if self.password == "":
            self.password = password

        if password == self.password:
            message = "You have successfully logged in!"
        else:
            # TODO: handle non match
            self.attempts -= 1
            if self.attempts <= 0:
                message = "Blocked from logging in"

            else:
                message = f"Password did not match. Number of tries left: {self.attempts}"

            self.client_socket.send(message.encode())

            return

        # TODO: abstract message sending
        with open("credentials.txt", "a") as file:
            file.write(f"\n{self.username} {self.password}")

        self.client_socket.send(message.encode())