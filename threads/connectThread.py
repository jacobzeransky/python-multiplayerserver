#Python

import os, time
import threading, queue
import socket

# thread handles all socket connection requests
# if successful, adds unauthenticated client to client list
class connectThread(threading.Thread):

    def __init__(self, client_l, event_q):
        threading.Thread.__init__(self)
        self.clients = client_l
        self.events = event_q
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = socket.gethostname()
        self.port = 10100
        self.stoprequest = threading.Event()

        # begin listening on socket
        self.serversocket.bind((self.host, self.port))
        self.serversocket.listen(5)
        self.events.put("ConnectThread started")
        self.start()

    def run(self):
        while not self.stoprequest.isSet():
            clientsocket, address = self.serversocket.accept()
            clientsocket.setblocking(0)

            # connection accepted, add client to list
            self.clients.append((clientsocket, address, None))
            self.events.put("{} connected".format(address[0]))

    def shutdown(self, timeout=None):
        self.stoprequest.set()
        self.events.put("ConnectThread shutdown")

    def __serveraddress():
        return ((self.host, self.port))
