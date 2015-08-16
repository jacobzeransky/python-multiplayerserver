#Python

import os, time
import threading, queue
import authenticatorModule

class authenticatorThread(threading.Thread):
    """ A worker thread that takes directory names from a queue, finds all
        files in them recursively and reports the result.

        Input is done by placing directory names (as strings) into the
        Queue passed in dir_q.

        Output is done by placing tuples into the Queue passed in result_q.
        Each tuple is (thread name, dirname, [list of files]).

        Ask the thread to stop by calling its join() method.
    """
    def __init__(self, auth_q, event_q):
        threading.Thread.__init__(self)
        self.authq = auth_q
        self.events = event_q
        self.authm = authenticatorModule.authenticatorModule('db.txt', 'admins.txt', event_q)
        self.stoprequest = threading.Event()
        self.events.put("AuthenticatorThread started")
        self.start()

    def run(self):
        # As long as we weren't asked to stop, try to take new tasks from the
        # queue. The tasks are taken with a blocking 'get', so no CPU
        # cycles are wasted while waiting.
        # Also, 'get' is given a timeout, so stoprequest is always checked,
        # even if there's nothing in the queue.
        while not self.stoprequest.isSet():
            try:
                client, mtype, msg = self.authq.get(True, 0.05)
                ulen = int(msg[0]) + 5
                plen = int(msg[1]) + 4
                uname = ''.join(msg[2:(ulen+2)])
                upass = ''.join(msg[(ulen+2):])
                if mtype == 0:
                    res = self.authm.authenicate(uname, upass)
                    if res == 'c':
                        if self.authm.checkadminstatus(uname):
                            self.events.put("{} with {} successful as admin".format(uname, upass))
                        else:
                            self.events.put("{} with {} successful".format(uname, upass))
                    elif res == 'i':
                        self.events.put("{} with {} unsuccessful".format(uname, upass))
                    else:
                        self.events.put("{} with {} not found".format(uname, upass))
                else:
                    res = self.authm.createnewuser(uname, upass)
                    if res == 'e':
                        self.events.put("{} with {} user already exists".format(uname, upass))
                    else:
                        self.events.put("{} with {} creation successful".format(uname, upass))
            except queue.Empty:
                continue

    def shutdown(self, timeout=None):
        self.authm.shutdown()
        self.stoprequest.set()
        self.events.put("AuthenticatorThread shutdown")
