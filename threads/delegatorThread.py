#Python

import os, time
import threading, queue
import socket

# receives messages from client sockets, does some formatting
# places new message into appropriate input queue for other threads

class delegatorThread(threading.Thread):

    def __init__(self, client_l, auth_q, lobby_q, gamethread_l, event_q, admin_q):
        threading.Thread.__init__(self)
        self.clients = client_l
        self.authq = auth_q
        self.lfgq = lobby_q
        self.gtl = gamethread_l
        self.events = event_q
        self.adminq = admin_q
        self.stoprequest = threading.Event()
        self.events.put("DelegatorThread started")
        self.start()

    def run(self):
        while not self.stoprequest.isSet():
            # for each client socket in list
            for cl in self.clients:
                try:
                    # receive is non-blocking, so move to next client if no message available
                    msg = list(cl[0].recv(1024).decode())
                    if len(msg) > 0:
                        self.events.put("{}".format(msg))
                        if msg[0] == 'l': #join lobby
                            self.lfgq.put(cl)
                            self.events.put("{} joined lobby".format(cl[1][0]))
                        elif msg[0] == 'g': #perform game move
                            self.gtl[int(msg[1])][0].put(msg[2]) # msg[2] = gamestate
                            #self.events.put("{} performed move in game {}".format(addr, msg[1]))
                        elif msg[0] == 'a': #login/authenticate
                            self.authq.put((cl, 0, msg[1:]))
                            self.events.put("{} is attempting to login".format(cl[1][0]))
                        elif msg[0] == 'n': #new user
                            self.authq.put((cl, 1, msg[1:]))
                            self.events.put("{} is attempting to create new user".format(cl[1][0]))
                        elif msg[0] == 'd': #admin command
                            self.adminq.put((cl, msg[1:]))
                except socket.error:
                    continue

    def shutdown(self, timeout=None):
        self.stoprequest.set()
        self.events.put("DelegatorThread shutdown")
