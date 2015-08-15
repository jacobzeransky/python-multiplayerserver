#Python

import os, time
import threading, queue
import socket

class connectThread(threading.Thread):
    """ A worker thread that takes directory names from a queue, finds all
        files in them recursively and reports the result.

        Input is done by placing directory names (as strings) into the
        Queue passed in dir_q.

        Output is done by placing tuples into the Queue passed in result_q.
        Each tuple is (thread name, dirname, [list of files]).

        Ask the thread to stop by calling its join() method.
    """
    def __init__(self, client_l, event_q):
        threading.Thread.__init__(self)
        self.clients = client_l
        self.events = event_q
        self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = socket.gethostname()
        self.port = 10100
        self.stoprequest = threading.Event()
        self.serversocket.bind((self.host, self.port))
        self.serversocket.listen(5)
        self.events.put("ConnectThread started")
        self.start()

    def run(self):
        # As long as we weren't asked to stop, try to take new tasks from the
        # queue. The tasks are taken with a blocking 'get', so no CPU
        # cycles are wasted while waiting.
        # Also, 'get' is given a timeout, so stoprequest is always checked,
        # even if there's nothing in the queue.
        while not self.stoprequest.isSet():
            clientsocket, address = self.serversocket.accept()
            clientsocket.setblocking(0)
            self.clients.append((clientsocket, address, None))
            self.events.put("{} connected".format(address[0]))

    def shutdown(self, timeout=None):
        self.stoprequest.set()
        self.events.put("ConnectThread shutdown")
        #super(WorkerThread, self).join(timeout)

    def __serveraddress():
        return ((self.host, self.port))
