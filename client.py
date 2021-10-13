"""
    Python 3
    Usage: python3 exampleClient.py localhost 12000
    coding: utf-8

    Author: Toshi Tabata (z5280803)

    Rewritten example of a python3 socket client. Original program from Wei Song.
"""

from socket import socket, AF_INET, SOCK_STREAM
import sys


# Server would be running on the same host as Client
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

while True:
    message = input("\n===== Enter your message to send to the server, or hit enter to exit: =====\n")

    # TCP messages can't be empty since the client will just hang and never send anything
    if message == "":
        print("Disconnecting")
        break

    print(f"Sending message: {message}")

    CLIENT_SOCKET.sendall(message.encode())

    data = CLIENT_SOCKET.recv(1024)
    received_message = data.decode()

    # parse the message received from server and take corresponding actions
    print(f"Message from server: {received_message}")


# close the socket
CLIENT_SOCKET.close()
