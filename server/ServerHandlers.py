import json
from threading import Lock
from helper import debug, get_server_init_state, get_user_list
import time


# Class that handles all the commands the server needs to handle
def handle_blocked_login(message):
    message["message"] = "Blocked from logging in"
    message["blocked"] = True


class ServerHandler:
    def __init__(self, client_socket, clients, block_duration, thread, address, port):
        self.commands = {
            "username": self.handle_username,
            "password": self.handle_password,
            "block": self.handle_blacklist,
            "whoelse": self.handle_whoelse,
            "whoelsesince": self.handle_whoelsesince,
            "broadcast": self.handle_broadcast,
            "unblock": self.handle_unblock,
            "message": self.handle_message,
            "startprivate": self.handle_startprivate,
            "startprivate_resp": self.handle_startprivate_resp,
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
        self.address = address
        self.port = port

    def handle_startprivate(self, username):
        message = {
            "command": "startprivate_ans",
            "message": f"{self.username} would like to start a private chat with you! y/n",
            "username": self.username,
            "address": self.address,
            "port": self.port,
            "OK": False,
            "from": ""
        }

        recipient = self.username

        if username == self.username:
            message["message"] = "Can't setup a connection with yourself!"

        elif username not in self.clients:
            message["message"] = "User could not be found"

        elif username not in get_user_list(self.clients, self.username):
            message["message"] = "This user has blocked you"

        elif self.clients[username]["client_thread"] is None or not self.clients[username]["client_thread"].is_active():
            message["message"] = "This user is offline"

        else:
            message["OK"] = True
            recipient = username

        self.send_message(message, self.clients[recipient]["client_socket"])

    def handle_startprivate_resp(self, message):
        didAccept, username, port, address = message.split(" ", 3)
        debug(f"Got response for startprivate: {didAccept == 'True'}")
        didAccept = didAccept == "True"

        debug(f"Got a response from peer that they have created a server\n"
              f"at address: {address}{port}")
        message = {
            "command": "startprivate_init",
            "message": f"{self.username} has {'accepted' if didAccept else 'declined'} the private message request!",
            "username": self.username,
            "address": address,
            "port": port,
            "OK": didAccept,
            "from": ""
        }
        self.send_message(message, self.clients[username]["client_socket"])

    def handle_broadcast(self, message):
        self.broadcast_message(message, self.username)

    def handle_message(self, body):
        message = {
            "command": "broadcast",
            "message": "",
            "offline": False,
            "from": ""
        }

        parts = body.split(" ", 1)
        if len(parts) < 2:
            message["message"] = "Usage: message <username> <message>"
            self.send_message(message)
            return

        user = parts[0]
        msg = parts[1]
        recipient = None

        debug(f"Sending message from {self.username} to {user}: {msg}")
        if user not in self.clients:
            message["message"] = "Could not find user"
        elif user == self.username:
            message["message"] = "Can't send yourself a message"
        elif self.username in self.clients[user]["blacklist"]:
            message["message"] = "This user has blocked you."
        elif self.clients[user]["client_socket"] is None:
            # user offline. add to buffer
            self.clients[user]["offline_messages"].append((msg, self.username))
            return
        else:
            message["message"] = msg
            message["from"] = self.username
            recipient = self.clients[user]["client_socket"]

        self.send_message(message, recipient)

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

        json_str = json.dumps(message) + "\r\n"
        person.sendall(json_str.encode())
        debug(f"Just send {message}")

    def broadcast_message(self, text, username=""):
        message = {
            "command": "broadcast",
            "message": text,
            "from": username
        }
        users = get_user_list(self.clients, self.username)
        if len(self.clients) != len(users) + 1:
            self.send_message({
                "command": "broadcast",
                "message": "Some users could not receive your message because they have blocked you.",
                "from": ""
            })

        for user in users:
            curr_socket = self.clients[user]["client_socket"]

            if curr_socket is not None and user != self.username:
                self.send_message(message, curr_socket)

    # Broadcast to anyone who isn't blocked by self.username
    def broadcast_to_unblocked(self, text):
        message = {
            "command": "broadcast",
            "message": text,
            "from": ""
        }

        my_blacklist = self.clients[self.username]["blacklist"]
        for user in self.clients:
            sock = self.clients[user]["client_socket"]
            if user not in my_blacklist and sock is not None and user != self.username:
                self.send_message(message, sock)

    def broadcast_login(self):
        self.broadcast_to_unblocked(f"{self.username} has logged in.")
        # self.broadcast_message(f"{self.username} has logged in.")

    def login(self):

        self.update_clients({
                "block_time": 0,
                "client_socket": self.client_socket,
                "client_obj": self,
                "client_thread": self.thread,
                "log_on_time": time.time()
        })

        for msg, user in self.clients[self.username]["offline_messages"]:
            message = {
                "command": "broadcast",
                "message": msg,
                "from": user
            }
            debug(f"{msg} {user}")
            self.send_message(message)

        self.update_clients({
            "offline_messages": []
        })
        self.broadcast_login()

    def logout(self):
        if self.username == "":
            return
        self.update_clients({
            "client_socket": None,
            "client_obj": None,
            "client_thread": None,
        })
        if self.username:
            self.broadcast_to_unblocked(f"{self.username} has logged out.")
            # self.broadcast_message(f"{self.username} has logged out.")

    def handle_username(self, username):

        message = {
            "message": "",
            "blocked": False,
            "command": "username"
        }
        if username in self.clients and self.clients[username]["client_socket"] is not None:
            message["message"] = "You are already logged in"
            message["command"] = "exit"
            message["blocked"] = True
            self.send_message(message)
            return

        self.username = username
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
            self.send_message(message)
            self.login()
            # Early return so we can send_message before login()
            return

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
