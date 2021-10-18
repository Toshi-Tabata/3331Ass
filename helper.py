import time
DEBUG = True


def debug(message):
    if DEBUG and message != "":

        print(f"DEBUG:      {message}")


def server_message(message):
    if message != "":
        print(f"SERVER: {message}")


def get_server_init_state():
    return {
        "block_time": 0,
        "client_socket": None,
        "client_obj": None,
        "client_thread": None,
        "password": "",
        "log_on_time": -1,
        "blacklist": set(),
        "offline_messages": []  # (msg, user)
    }


# Return a list of users that haven't blacklisted person
def get_user_list(clients, person):
    users = []
    for user in clients:
        if person not in clients[user]["blacklist"] and user != person:
            users.append(user)

    return users
