#Python

import os, time
import threading, queue
import socket

class delegatorThread(threading.Thread):
    """ A worker thread that takes directory names from a queue, finds all
        files in them recursively and reports the result.

        Input is done by placing directory names (as strings) into the
        Queue passed in dir_q.

        Output is done by placing tuples into the Queue passed in result_q.
        Each tuple is (thread name, dirname, [list of files]).

        Ask the thread to stop by calling its join() method.
    """
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
        # As long as we weren't asked to stop, try to take new tasks from the
        # queue. The tasks are taken with a blocking 'get', so no CPU
        # cycles are wasted while waiting.
        # Also, 'get' is given a timeout, so stoprequest is always checked,
        # even if there's nothing in the queue.
        while not self.stoprequest.isSet():
            for cl in self.clients:
                try:
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
