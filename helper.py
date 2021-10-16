
DEBUG = True


def debug(message):
    if DEBUG and message != "":

        print(f"DEBUG:      {message}")


def server_message(message):
    if message != "":
        print(f"SERVER: {message}")

