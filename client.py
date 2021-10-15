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

from ClientMethods import ClientMethod

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

# class SendMessage(Thread):
#     def __init__(self, text):
#         Thread.__init__(self)
#
#         self.ans = input(text)
#
#     def get_ans(self):
#         return self.ans


def print_server_info():
    while True:
        data = CLIENT_SOCKET.recv(1024)
        received_message = json.loads(data.decode())
        print(received_message)
        message = received_message["message"]
        server_message(message)

        # TODO: this is where we parse what the server is sending us
        # e.g. user sends us message: here



t = Thread(target=print_server_info)
t.setDaemon(True)


def start_loop():

    helper.handle_username()

    helper.handle_password()

    t.start()

    while True:
        print("oy")
        helper.send_message(input())
        print("yo")




def main():

    start_loop()

    # close the socket
    CLIENT_SOCKET.close()


main()
