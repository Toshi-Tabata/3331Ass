"""
    Messaging Application's Server
    Python 3
    Usage: python3 server.py 12000
    coding: utf-8

    Author: Toshi Tabata (z5280803)

    Rewritten example of a python3 socket client. Original program from Wei Song.
"""

from socket import socket, AF_INET, SOCK_STREAM
from ClientThread import ClientThread
import sys

from helper import debug, get_server_init_state


# Runs the server
def main():
    if len(sys.argv) != 4:
        print(f"\n===== Usage: python3 {sys.argv[0]} <server port> <block_duration> <timeout> =====\n")
        exit(0)

    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = int(sys.argv[1])
    SERVER_ADDRESS = (SERVER_HOST, SERVER_PORT)

    # define socket for the server side and bind address
    SERVER_SOCKET = socket(AF_INET, SOCK_STREAM)
    SERVER_SOCKET.bind(SERVER_ADDRESS)

    debug("\n===== Server is running =====")

    # {is_blocked::bool, client_socket::socket, client_obj::ServerHandler}
    clients = {}

    with open("credentials.txt", "r") as file:
        for line in file:
            user, password = line.split()
            clients[user] = get_server_init_state()
            clients[user]["password"] = password

    while True:
        SERVER_SOCKET.listen()
        clientThread = ClientThread(*SERVER_SOCKET.accept(), sys.argv[2], sys.argv[3], clients)

        clientThread.start()


if __name__ == "__main__":
    main()
