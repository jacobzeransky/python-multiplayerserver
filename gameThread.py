#Python

import os, time
import threading, queue

class gameThread(threading.Thread):
    """ A worker thread that takes directory names from a queue, finds all
        files in them recursively and reports the result.

        Input is done by placing directory names (as strings) into the
        Queue passed in dir_q.

        Output is done by placing tuples into the Queue passed in result_q.
        Each tuple is (thread name, dirname, [list of files]).

        Ask the thread to stop by calling its join() method.
    """
    def __init__(self, game_id, game_q, player1, player2, event_q):
        threading.Thread.__init__(self)
        self.id = game_id
        self.gq = game_q
        self.p1 = player1
        self.p2 = player2
        self.events = event_q
        self.stoprequest = threading.Event()
        self.events.put("Game starting between {} and {}".format(player1[1], player2[1]))

        self.curp = 1
        self.board = "000000000"
        self.p1[0].send(str(self.id).encode())
        self.p2[0].send(str(self.id).encode())

        msg = 'g' + str(self.board)
        self.p1[0].send(msg.encode())
        msg = 'w' + str(self.board)
        self.p2[0].send(msg.encode())
        
        self.start()
        
    def run(self):
        # As long as we weren't asked to stop, try to take new tasks from the
        # queue. The tasks are taken with a blocking 'get', so no CPU
        # cycles are wasted while waiting.
        # Also, 'get' is given a timeout, so stoprequest is always checked,
        # even if there's nothing in the queue.
        while not self.stoprequest.isSet():
            try:
                pmove = self.gq.get(True, 0.05)
                self.board = list(self.board)
                self.board[int(pmove)] = str(self.curp)
                self.board = ''.join(self.board)
                self.events.put("Game {}: player {} performed move on position {}".format(self.id, self.curp, pmove))
                if self.gameover():
                    self.events.put("Game {}: player {} won".format(self.id, self.curp))
                    msg = 'o' + str(self.curp) + str(self.board)
                    self.p1[0].send(msg.encode())
                    self.p2[0].send(msg.encode())
                    self.join()
                else:
                    msg = 'g' + str(self.board)
                    if self.curp == 1:
                      #  self.p1[0].send('w'.join(self.board).encode())
                        self.p2[0].send(msg.encode())
                        self.curp = 2
                    else:
                        self.p1[0].send(msg.encode())
                       # self.p2[0].send('w'.join(self.board).encode())
                        self.curp = 1
                    
            except queue.Empty:
                continue

    def join(self, timeout=None):
        self.stoprequest.set()

    def gameover(self):
        gb = list(self.board)
        if gb.count('0') > 0:
            if (gb[0] == gb[1] == gb[2] != '0' or
                gb[0] == gb[3] == gb[6] != '0' or
                gb[0] == gb[4] == gb[8] != '0' or
                gb[1] == gb[4] == gb[7] != '0' or
                gb[3] == gb[4] == gb[5] != '0' or
                gb[8] == gb[7] == gb[6] != '0' or
                gb[8] == gb[5] == gb[2] != '0' or
                gb[2] == gb[4] == gb[6] != '0'):
                    return True
            else:
                return False
        else:
            return True
