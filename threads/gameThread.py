#Python

import os, time
import threading, queue

# new instance created for each game
# handles game state and communcation between players for its own game
# receives messages from delegator thread
class gameThread(threading.Thread):

    def __init__(self, game_id, game_q, player1, player2, event_q):
        threading.Thread.__init__(self)
        self.id = game_id
        self.gq = game_q
        self.p1 = player1
        self.p2 = player2
        self.events = event_q
        self.stoprequest = threading.Event()
        self.events.put("Game starting between {} and {}".format(player1[1], player2[1]))

        # initialize gamestate, determine player 1 and 2
        self.curp = 1
        self.board = "000000000"
        self.p1[0].send(str(self.id).encode())
        self.p2[0].send(str(self.id).encode())

        # begin play
        msg = 'g' + str(self.board)
        self.p1[0].send(msg.encode())
        msg = 'w' + str(self.board)
        self.p2[0].send(msg.encode())
        
        self.start()
        
    def run(self):
        while not self.stoprequest.isSet():
            try:
                # attempts to get most recent move message
                pmove = self.gq.get(True, 0.05)
                self.board = list(self.board)
                self.board[int(pmove)] = str(self.curp)
                self.board = ''.join(self.board)
                self.events.put("Game {}: player {} performed move on position {}".format(self.id, self.curp, pmove))

                # check if move puts board into gameover state
                if self.gameover():
                    self.events.put("Game {}: player {} won".format(self.id, self.curp))
                    msg = 'o' + str(self.curp) + str(self.board)
                    self.p1[0].send(msg.encode())
                    self.p2[0].send(msg.encode())
                    self.join()
                    
                # continue play
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

    # check if gameboard is in game over state
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
