import json
from threading import Lock
from helper import debug, get_server_init_state, get_user_list
import time


# Class that handles all the commands the server needs to handle
def handle_blocked_login(message):
    message["message"] = "Blocked from logging in"
    message["blocked"] = True


class ServerHandler:
    def __init__(self, client_socket, clients, block_duration, thread):
        self.commands = {
            "username": self.handle_username,
            "password": self.handle_password,
            "block": self.handle_blacklist,
            "whoelse": self.handle_whoelse,
            "whoelsesince": self.handle_whoelsesince,
            "unblock": self.handle_unblock,
            "test": self.test
        }
        self.client_socket = client_socket
        self.username = ""
        self.password = ""
        self.attempts = 3
        self.clients = clients
        self.block_duration = int(block_duration)
        self.lock = Lock()
        self.thread = thread

    def update_clients(self, obj, user=None):
        if user is None:
            user = self.username

        with self.lock:
            if user not in self.clients:
                self.clients[user] = {}

            self.clients[user].update(obj)

    def is_blocked(self):
        return time.time() - self.clients[self.username]["block_time"] < self.block_duration

    def send_message(self, message, person=None):
        if person is None:
            person = self.client_socket
        person.sendall(json.dumps(message).encode())

    def broadcast_message(self, text, username=""):
        message = {
            "command": "broadcast",
            "message": text,
            "from": username
        }
        for user in get_user_list(self.clients, self.username):
            curr_socket = self.clients[user]["client_socket"]

            if curr_socket is not None and user != self.username:
                self.send_message(message, curr_socket)

    def broadcast_login(self):
        self.broadcast_message(f"{self.username} has logged in.")

    def login(self):

        self.update_clients({
                "block_time": 0,
                "client_socket": self.client_socket,
                "client_obj": self,
                "client_thread": self.thread,
                "log_on_time": time.time()
        })

        self.broadcast_login()

    def logout(self):
        self.update_clients({
            "client_socket": None,
            "client_obj": None,
            "client_thread": None,
        })

        self.broadcast_message(f"{self.username} has logged out.")

    def handle_username(self, username):
        self.username = username
        message = {
            "message": "",
            "blocked": False,
            "command": "username"
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
        if self.password == "" and self.username not in self.clients:
            self.password = password

            with open("credentials.txt", "a") as file:
                file.write(f"\n{self.username} {self.password}")

            self.update_clients(get_server_init_state())
            self.update_clients({
                "client_socket": self.client_socket,
                "client_obj": self,
                "client_thread": self.thread,
                "log_on_time": time.time(),
                "password": password,
            })

        message = {
            "blocked": False,
            "passwordMatch": password == self.password,
            "message": "",
            "command": "password"
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
                self.update_clients({"block_time": time.time()})

            else:
                message["message"] = f"Password did not match. Number of tries left: {self.attempts}"

        self.send_message(message)

    def handle_blacklist(self, username):
        message = {
            "command": "server",
            "message": "",
        }
        if username == self.username:
            message["message"] = "Cannot block yourself!"
        elif username in self.clients:
            self.clients[self.username]["blacklist"].add(username)
            debug(f"Added to blacklist. Set is now {self.clients[self.username]['blacklist']}")
            message["message"] = f"Blocked {username}."
        else:
            message["message"] = f"Could not find user {username}"

        self.send_message(message)

    # negative duration returns all active users
    def get_active_since(self, duration):
        users = []
        debug(f"dur: {duration}")
        # I want all users as of dur minutes ago
        for user in get_user_list(self.clients, self.username):

            if duration < 0 and self.clients[user]["client_thread"] is not None:
                debug("returning all users that are active")
                users.append(user)
            elif (time.time() - duration) <= self.clients[user]["log_on_time"]:

                debug(f"{time.time() - duration} vs {self.clients[user]['log_on_time']}")
                users.append(user)

        return users

    def handle_whoelsesince(self, duration):
        message = {
            "command": "server",
            "message": "",

        }
        try:
            duration = int(duration)
            active_users = f"Users logged within {duration} seconds ago:\n"
            active = self.get_active_since(duration)

            if not active:
                active_users = "Nobody else was online since then!"
            else:
                active_users += "\n".join(active)

            message["message"] = active_users

        except ValueError:
            message["message"] = "usage: whoelsesince <integer>"

        self.send_message(message)

    # Body will be given but ignored
    def handle_whoelse(self, body):
        active_users = "Active Users:\n"
        active = self.get_active_since(-1)

        if not active:
            active_users = "Nobody else is online!"
        else:
            active_users += "\n".join(active)

        message = {
            "command": "server",
            "message": active_users,

        }
        self.send_message(message)

    def handle_unblock(self, username):
        message = {
            "command": "server",
            "message": "",
        }
        if username == self.username:
            message["message"] = "Cannot unblock yourself!"
        elif username in self.clients and username in self.clients[self.username]["blacklist"]:
            self.clients[self.username]["blacklist"].remove(username)
            debug(f"Removed from blacklist. Set is now {self.clients[self.username]['blacklist']}")
            message["message"] = f"Unblocked {username}."
        else:
            message["message"] = f"Could not find user {username} in your blocked list"

        self.send_message(message)

    def test(self, body):

        message = {
            "message": "hello",
            "status": "OK",
            "body": body
        }

        msg = json.dumps(message)
        self.client_socket.send(msg.encode())
