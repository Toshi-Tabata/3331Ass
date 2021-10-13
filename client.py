"""
    Python 3
    Usage: python3 client.py localhost 12000
    coding: utf-8

    Author: Toshi Tabata (z5280803)
"""

from socket import socket, AF_INET, SOCK_STREAM
import sys

from ClientMethods import ClientMethod

if len(sys.argv) != 2:
    print(f"\n===== Error usage, python3 {sys.argv[0]} SERVER_PORT ======\n")
    exit(0)

SERVER_HOST = "localhost"
SERVER_PORT = int(sys.argv[1])
SERVER_ADDRESS = (SERVER_HOST, SERVER_PORT)

# define a socket for the client side, it would be used to communicate with the server
CLIENT_SOCKET = socket(AF_INET, SOCK_STREAM)

# build connection with the server and send message to it
CLIENT_SOCKET.connect(SERVER_ADDRESS)
helper = ClientMethod(CLIENT_SOCKET)


def start_loop():
    isListening = True
    while isListening:
        username = input("Username: ")
        resp = helper.handle_username(username)
        if not resp:
            return

        password = input("Password: ")
        resp = helper.handle_password(password)

        isListening = isListening and resp







def main():

    start_loop()

    # close the socket
    CLIENT_SOCKET.close()


main()
