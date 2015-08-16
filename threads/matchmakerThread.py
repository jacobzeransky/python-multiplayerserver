#Python

import os, time
import threading, queue
import gameThread

class matchmakerThread(threading.Thread):
    """ A worker thread that takes directory names from a queue, finds all
        files in them recursively and reports the result.

        Input is done by placing directory names (as strings) into the
        Queue passed in dir_q.

        Output is done by placing tuples into the Queue passed in result_q.
        Each tuple is (thread name, dirname, [list of files]).

        Ask the thread to stop by calling its join() method.
    """
    def __init__(self, lobby_q, gamethread_l, event_q):
        threading.Thread.__init__(self)
        self.lfgq = lobby_q
        self.gtl = gamethread_l
        self.events = event_q
        self.stoprequest = threading.Event()
        self.events.put("MatchmakerThread started")
        self.start()

    def run(self):
        # As long as we weren't asked to stop, try to take new tasks from the
        # queue. The tasks are taken with a blocking 'get', so no CPU
        # cycles are wasted while waiting.
        # Also, 'get' is given a timeout, so stoprequest is always checked,
        # even if there's nothing in the queue.
        currp = None
        while not self.stoprequest.isSet():
            try:
                conn, addr = self.lfgq.get(True, 0.05)
                if currp == None:
                    currp = (conn, addr)
                else:
                    temp_q = queue.Queue()
                    gt = gameThread.gameThread(len(self.gtl), temp_q, currp, (conn, addr), self.events)
                    self.gtl.append((temp_q, gt))
                    currp = None
            except queue.Empty:
                continue

    def shutdown(self, timeout=None):
        self.stoprequest.set()
        self.events.put("MatchmakerThread shutdown")
