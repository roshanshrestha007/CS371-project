# =================================================================================================
# Contributing Authors:	    David MHS Webster
# Email Addresses:          dwe245@uky.edu
# Date:                     NYF
# Purpose:                  it's the server...
# =================================================================================================

import socket
import threading

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games


# TODO: implement pong simulation serverside, send updates clientside. Get paddle positions
# from clients. Don't care if they cheat. 


def startServer(port:str, errorLabel:tk.Label, app:tk.Tk) -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)





