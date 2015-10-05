#Python

import os, time
import threading, queue
import authenticatorModule

# thread that handles authentication requests pulled from the authentication queue

class authenticatorThread(threading.Thread):
    
    def __init__(self, auth_q, event_q):
        threading.Thread.__init__(self)
        self.authq = auth_q
        self.events = event_q
        # initalize module used to check given authentication information from queue
        self.authm = authenticatorModule.authenticatorModule('db.txt', 'admins.txt', event_q)
        self.stoprequest = threading.Event()
        self.events.put("AuthenticatorThread started")
        self.start()

    def run(self):
        while not self.stoprequest.isSet():
            try:
                # get message from queue if available, format it
                client, mtype, msg = self.authq.get(True, 0.05)
                ulen = int(msg[0]) + 5
                plen = int(msg[1]) + 4
                uname = ''.join(msg[2:(ulen+2)])
                upass = ''.join(msg[(ulen+2):])

                # login request
                if mtype == 0:
                    res = self.authm.authenicate(uname, upass)
                    if res == 'c':
                        # authentication successful, check admin status
                        if self.authm.checkadminstatus(uname):
                            self.events.put("{} with {} successful as admin".format(uname, upass))
                        else:
                            self.events.put("{} with {} successful".format(uname, upass))
                    # invalid password
                    elif res == 'i':
                        self.events.put("{} with {} unsuccessful".format(uname, upass))
                    # user not found
                    else:
                        self.events.put("{} with {} not found".format(uname, upass))
                # create new user request
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
