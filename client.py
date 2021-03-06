#Python

import socket
from threading import *

# display board in console
def formatboard(gb):
    print ("{}|{}|{}\n-----\n{}|{}|{}\n-----\n{}|{}|{}".format(gb[0],gb[1],gb[2],gb[3],gb[4],gb[5],gb[6],gb[7],gb[8]))

# setup and connect socket, to server running on same machine
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 10100
clientsocket.connect((host, port))

# authenticate user
x = input("Login(0) or Create(1): ")
if x == '0':
    un = input("Username: ")
    up = input("Password: ")
    # format inputs into message to be sent to server
    msg = 'a' + str(len(un)-5) + str(len(up)-4) + un + up  
elif x == '1':
    un = input("New Username: ")
    up = input("Password: ")
    up2 = input("Repeat Password: ")
    if up != up2:
        print ("Error password match")
    # format inputs into message to be sent to server
    msg = 'n' + str(len(un)-5) + str(len(up)-4) + un + up    
else:
    input("error")

# send authentication info to server
clientsocket.send(msg.encode()) 
input("crash>")
input("crash>")

# get server response
gid = clientsocket.recv(1024).decode()

while True:
    # attempt to receive a message from server, format it
    msg = list(clientsocket.recv(4096).decode())
    if len(msg) > 0:
        
        # player turn
        if msg[0] == 'g':
            formatboard(msg[1:10])
            p = input("Enter move: ")
            msg = 'g' + str(gid) + str(p)
            clientsocket.send(msg.encode())
            
        # other players turn
        elif msg[0] == 'w':
            print ("Waiting on other player...")
            
        # gameover
        elif msg[0] == 'o':
            formatboard(msg[2:11])
            print ("Game over, player {} wins".format(msg[1]))
            break
        
        else:
            print ("msg error : {}".format(msg))
            break


r = input("end>")

"""
b = clientsocket.recv(1024).decode()
player = clientsocket.recv(1024).decode()
if player == '1':
    formatboard(b)
else:
    print ("Waiting for player 1")
while 1:
    response = clientsocket.recv(1024).decode()
    if response == 'g':
        while 1:
           ins = input("Enter position ({}): ".format(player))
           clientsocket.send(ins.encode())
           resp2 = clientsocket.recv(1024).decode()
           if resp2 == 'c':
               break
           else:
               print ("Server says move is invalid")
    elif response == 'o':
        print ("Game over")
        break
    else:
        formatboard(response)

clientsocket.close()
"""
