"""
    Python 3
    Usage: python3 client.py localhost 12000
    coding: utf-8

    Author: Toshi Tabata (z5280803)
"""

from socket import socket, AF_INET, SOCK_STREAM
import sys
from threading import Thread
from helper import debug, server_message
import json

from ClientMethods import ClientMethod, disconnect

if len(sys.argv) != 2:
    print(f"\n===== Error usage, python3 {sys.argv[0]} SERVER_PORT ======\n")
    exit(0)

SERVER_HOST = "localhost"
SERVER_PORT = int(sys.argv[1])
SERVER_ADDRESS = (SERVER_HOST, SERVER_PORT)
CLIENT_SOCKET = socket(AF_INET, SOCK_STREAM)
CLIENT_SOCKET.settimeout(3600)  # wait an hour with no communication from server before ending connection
CLIENT_SOCKET.connect(SERVER_ADDRESS)
helper = ClientMethod(CLIENT_SOCKET)


def print_server_info():
    while True:
        data = CLIENT_SOCKET.recv(1024)
        received_message = json.loads(data.decode())

        if "command" in received_message \
                and "message" in received_message \
                and received_message["command"] in helper.response:
            debug(received_message)
            command = received_message["command"]
            message = received_message["message"]
            server_message(message)

            if "exit" in received_message:
                debug("Exiting")
                server_message(received_message["message"])
                disconnect()

            helper.response[command](received_message)

        else:
            debug(f"Got invalid message: {received_message}")







        # TODO: this is where we parse what the server is sending us
        # e.g. user sends us message: here


t = Thread(target=print_server_info)
t.setDaemon(True)

def start_loop():
    t.start()
    helper.handle_username()

    helper.handle_password()


    while True:

        helper.send_message(input())





def main():

    start_loop()

    # close the socket
    CLIENT_SOCKET.close()


main()
