
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
        "blacklist": set(),
        "offline_messages": []  # TODO: pop from this list as they're sent
    }
