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


from client.ClientMethods import ClientMethod

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


def handle_server_messages():
    while True:
        data = CLIENT_SOCKET.recv(1024)
        data = data.decode().split("\r\n")
        debug(data)
        for datum in data:
            if datum == "":
                continue
            received_message = json.loads(datum)

            if "command" in received_message \
                    and "message" in received_message \
                    and received_message["command"] in helper.response:
                debug(received_message)
                command = received_message["command"]
                helper.response[command](received_message)

            else:
                debug(f"Got invalid message: {received_message}")


t = Thread(target=handle_server_messages)
t.setDaemon(True)


def start_loop():
    t.start()
    helper.handle_username()
    helper.handle_password()

    while True:
        command = input().split(" ", 1)
        body = ""
        debug(command)
        if len(command) == 2:
            command, body = command
        else:
            command = command[0]

        helper.handle.get(command, helper.send_message)(command, body)


def main():

    start_loop()

    # close the socket
    CLIENT_SOCKET.close()


main()
