import json
from threading import Lock
from helper import debug
import time


# Class that handles all the commands the server needs to handle
def handle_blocked_login(message):
    message["message"] = "Blocked from logging in"
    message["blocked"] = True


class ServerHandler:
    def __init__(self, client_socket, clients, block_duration):
        self.commands = {
            "username": self.handle_username,
            "password": self.handle_password,
            "test": self.test
        }
        self.client_socket = client_socket
        self.userExists = False
        self.username = ""
        self.password = ""
        self.attempts = 3
        self.clients = clients
        self.block_duration = int(block_duration)

    def is_blocked(self):
        return time.time() - self.clients[self.username]["block_time"] < self.block_duration

    def send_message(self, message, person=None):
        if person is None:
            person = self.client_socket
        person.sendall(json.dumps(message).encode())

    def broadcast_message(self, text):
        message = {"message": text}
        for user in self.clients:
            curr_socket = self.clients[user]["client_socket"]
            if curr_socket is not None and user != self.username:
                self.send_message(message, curr_socket)

    def broadcast_login(self):
        # TODO: change this to a dict and set the backend to listen for a dict
        self.broadcast_message(f"{self.username} has logged in.")

    def login(self):
        lock = Lock()
        with lock:
            self.clients[self.username].update({
                "block_time": 0,
                "client_socket": self.client_socket,
                "client_obj": self
            })

        self.broadcast_login()

    def logout(self):
        self.clients[self.username].update({
            "client_socket": None,
            "client_obj": None,
        })

        # TODO: change this to a dict and set the backend to listen for a dict
        self.broadcast_message(f"{self.username} has logged out.")

    def handle_username(self, username):
        self.username = username
        message = {
            "message": "",
            "blocked": False
        }
        if username in self.clients and self.is_blocked():
            handle_blocked_login(message)
        elif username in self.clients:
            message["message"] = f"Hello {username}, what is your password?"
            self.password = self.clients[username]["password"]
        else:
            message["message"] = f"Creating a new account for {username}. Choose a password."

        self.send_message(message)

    def handle_password(self, password):
        debug(f"password received was {password}, matching against {self.password}")
        if self.password == "":
            self.password = password

            with open("credentials.txt", "a") as file:
                file.write(f"\n{self.username} {self.password}")

            self.clients[self.username] = {
                "block_time": 0,
                "client_socket": self.client_socket,
                "client_obj": self,
                "password": password,
            }

        message = {
            "blocked": False,
            "passwordMatch": password == self.password,
            "message": ""
        }

        if self.is_blocked():
            handle_blocked_login(message)

        elif message["passwordMatch"]:
            message["message"] = "You have successfully logged in!"
            self.login()

        else:
            self.attempts -= 1
            if self.attempts <= 0:
                handle_blocked_login(message)
                self.clients[self.username]["block_time"] = time.time()

            else:
                message["message"] = f"Password did not match. Number of tries left: {self.attempts}"

        self.send_message(message)

    def test(self, body):

        message = {
            "message": "hello",
            "status": "OK",
            "body": body
        }

        msg = json.dumps(message)
        self.client_socket.send(msg.encode())
