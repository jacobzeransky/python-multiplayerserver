#Python

import socket, threading
import connectThread, delegatorThread, gameThread, matchmakerThread, authenticatorThread
import queue
import time

# initalize lists/queues used for record keeping and communication
client_l = []
auth_q = queue.Queue()
event_q = queue.Queue()
lobby_q = queue.Queue()
gamethread_l = []
admin_q = queue.Queue()

# start all server threads
conn_t = connectThread.connectThread(client_l, event_q)
auth_t = authenticatorThread.authenticatorThread(auth_q, event_q)
dele_t = delegatorThread.delegatorThread(client_l, auth_q, lobby_q, gamethread_l, event_q, admin_q)
mm_t = matchmakerThread.matchmakerThread(lobby_q, gamethread_l, event_q)

# print event log to console, check for admin commands (for shutting down server)
try:
    while True:
        try:
            print (event_q.get(True, 0.05))
            ad, adc = admin_q.get(True, 0.05)
            msg = 'a'
            if adc == 'u':
                msg += str(len(client_l))
            elif adc == 'g':
                msg += str(len(gamethread_l))
            elif adc == 's':
                msg += 's'
                ad.send(msg.encode())
                break
            ad.send(msg.encode())
        except queue.Empty:
            continue
except KeyboardInterrupt:
    print ("Interrupted, shutting down")

# shutdown all server threads
conn_t.shutdown()
auth_t.shutdown()
dele_t.shutdown()
mm_t.shutdown()

# print remaining event log
for i in range(5):
    print (event_q.get())
r = input("end>")
