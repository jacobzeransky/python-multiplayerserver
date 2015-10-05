#Python

import os, time
import threading, queue
import gameThread

# matches players waiting in lobby queue
# creates gamethread for both players, makes it available for delegator thread

class matchmakerThread(threading.Thread):

    def __init__(self, lobby_q, gamethread_l, event_q):
        threading.Thread.__init__(self)
        self.lfgq = lobby_q
        self.gtl = gamethread_l
        self.events = event_q
        self.stoprequest = threading.Event()
        self.events.put("MatchmakerThread started")
        self.start()

    def run(self):
        currp = None
        while not self.stoprequest.isSet():
            try:
                # get a player in lobby
                conn, addr = self.lfgq.get(True, 0.05)
                
                # if this player is the first pulled
                if currp == None:
                    currp = (conn, addr)
                    
                # this player is second pulled, enough to begin a game
                else:
                    # start gamethread for new game
                    temp_q = queue.Queue()
                    gt = gameThread.gameThread(len(self.gtl), temp_q, currp, (conn, addr), self.events)
                    self.gtl.append((temp_q, gt))
                    currp = None
            except queue.Empty:
                continue

    def shutdown(self, timeout=None):
        self.stoprequest.set()
        self.events.put("MatchmakerThread shutdown")
