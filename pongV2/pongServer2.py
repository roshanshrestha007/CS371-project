# =================================================================================================
# Contributing Authors:	    Roshan Shrestha, David Webster & Nnaemeka Okafor
# Email Addresses:          rsh251@uky.edu dwe245@uky.edu
# Date:                     11/08/2023
# Purpose:                  Server side of the game
# =================================================================================================

import socket
import threading
import json
import tkinter as tk


# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games

app = tk.Tk()
app.title("Server Code")

# Function to handle communication with a single client.

noOfClients = 0


def receiveAck(client: socket.socket):
    received = client.recv(1024)
    data = received.decode('utf-8')
    jsonData = json.loads(data)
    if jsonData.get("ack", None) is None:
        raise Exception("THIS CLIENT IS DISOBEDIENT. IT DID NOT ACK ME")
    return


# global state
clients_configured = [0, 0]
scores = [0, 0]
paddle_positions = [0, 0]
ball_pos = [0, 0]
somebody_has_won = False

# Initialize the game state to store paddle positions.
paddlePos = {
    'firstPlayer': {'y': 0},
    'secondPlayer': {'y': 0}
}

# Create a socket to listen for incoming connections.
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(("localhost", 9999))
server.listen(5)
actual_server_address = server.getsockname()
print(f"Server is listening at {actual_server_address[0]} and port: {actual_server_address[1]}")

# Define the number of clients you expect to connect.
num_clients_expected = 2

# Track the number of connected clients.

# handle each client...


client_socket1, client_address1 = server.accept()
client_socket2, client_address2 = server.accept()

# spectator_clients = []
# client_socket3, client_address3 = server.accept()

cmd = {'command': 'game_parameters', 'screen_width': 600, 'screen_height': 400, 'whoami': "l"}
client_socket1.sendall(json.dumps(cmd).encode('utf-8'))

cmd['whoami'] = "r"
client_socket2.sendall(json.dumps(cmd).encode('utf-8'))
# retrieve an ACK from player 1....
receiveAck(client_socket1)
receiveAck(client_socket2)

cmd = {'command': 'start_game'}

client_socket1.sendall(json.dumps(cmd).encode('utf-8'))
client_socket2.sendall(json.dumps(cmd).encode('utf-8'))

# we need to get acks for start_game...
receiveAck(client_socket1)
receiveAck(client_socket2)

# We are now playing the game...


def update_game_state(somebody_has_won):
    # Ask for paddle data...
    cmd = {'command': 'send_me_paddle_data'}
    client_socket1.sendall(json.dumps(cmd).encode('utf-8'))
    client_socket2.sendall(json.dumps(cmd).encode('utf-8'))

    # Update paddle variables...
    data = client_socket1.recv(1024)
    stuff = json.loads(data.decode('utf-8'))
    # for 1
    paddle_positions[0] = stuff['y']
    ball_pos = stuff['ball']
    scores = stuff['score']

    # for 2
    data = client_socket2.recv(1024)
    stuff = json.loads(data.decode('utf-8'))

    paddle_positions[1] = stuff['y']

    # make each player see the other person...
    cmd = {'command': 'UPDATE_TIME', 'score': scores, 'ball': ball_pos, 'enemys_y': paddle_positions[1]}
    client_socket1.sendall(json.dumps(cmd).encode('utf-8'))
    cmd['enemys_y'] = paddle_positions[0]
    client_socket2.sendall(json.dumps(cmd).encode('utf-8'))
    receiveAck(client_socket1)
    receiveAck(client_socket2)

    # let them play...
    cmd = {'command': 'justgo'}
    client_socket1.sendall(json.dumps(cmd).encode('utf-8'))
    client_socket2.sendall(json.dumps(cmd).encode('utf-8'))
    receiveAck(client_socket1)
    receiveAck(client_socket2)

    winning_score = 10

    if scores[0] > winning_score or scores[1] > winning_score: #Todo change back to 4
        somebody_has_won = True

    if scores[0] > winning_score:
        cmd = {'command': 'youwin'}
        client_socket1.sendall(json.dumps(cmd).encode('utf-8'))
        cmd = {'command': 'youlose'}
        client_socket2.sendall(json.dumps(cmd).encode('utf-8'))
        #break

    if scores[1] > winning_score:
        cmd = {'command': 'youlose'}
        client_socket1.sendall(json.dumps(cmd).encode('utf-8'))
        cmd = {'command': 'youwin'}
        client_socket2.sendall(json.dumps(cmd).encode('utf-8'))
        #break


    if not somebody_has_won:
        app.after(10, update_game_state, somebody_has_won)


app.after(10, update_game_state, somebody_has_won)
app.mainloop()






