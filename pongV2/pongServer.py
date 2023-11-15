# =================================================================================================
# Contributing Authors:	    Roshan Shrestha
# Email Addresses:          rsh251@uky.edu
# Date:                     11/08/2023
# Purpose:                  Server side of the game
# =================================================================================================

import socket
import threading
import json

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games


# Function to handle communication with a single client.

noOfClients = 0

clients_configured = [0,0]

def handleClient(client_socket, cid):
    global paddlePos
    global noOfClients
    global score
    
    try:
        while True:
            # Receive data from the client.
            data = client_socket.recv(1024)
            if not data:
                break
            # Decode and parse the request from the client.
            decoded_data = data.decode('utf-8')
            print(decoded_data)
            client_request = json.loads(decoded_data)

            # print(f"Received request from client: {client_request}")

            if client_request["request"] == "get_game_parameters":
                # Respond with game parameters like screen dimensions and paddle position.
                response = {'command' : 'game_parameters'}
                response['screen_width'] = 600
                response['screen_heigh'] = 400
                if cid == 1:
                    response['paddle_position'] = 'right';
                    clients_configured[1] = 1
                else:
                    response['paddle_position'] = 'left';
                    clients_configured[0] = 1
                
                client_socket.sendall(json.dumps(response).encode('utf-8'))
            
            elif client_request["request"] == "paddleUpdate":
                # Update the y-position of player 1's paddle.
                if cid == 0:
                    paddlePos['firstPlayer']['y'] = int(client_request['y'])
                else:
                    paddlePos['secondPlayer']['y'] = int(client_request['y'])
            elif client_request["request"] == "getPaddleOpponent":
                # Respond with the y-position of player 2's paddle.
                response = {'command' : 'update_oppo_paddle'}
                if cid == 0:
                    response['oppo_paddle_pos'] = paddlePos['secondPlayer']['y']
                else:
                    response['oppo_paddle_pos'] = paddlePos['firstPlayer']['y']
                client_socket.sendall(json.dumps(response).encode('utf-8'))

    except Exception as e:
        print(f"Error in handling client: {e}")
    finally:
        client_socket.close()


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
start_message = {'command': 'start_game'}
client_socket1.sendall(json.dumps(start_message).encode('utf-8'))
client_socket2.sendall(json.dumps(start_message).encode('utf-8'))
threading.Thread(target=handleClient, args=(client_socket1,0)).start()

threading.Thread(target=handleClient, args=(client_socket1,1)).start()

# 
if 1 == 2:
    for cid in range(num_clients_expected):
        # Accept a new client connection.
        client_socket, client_address = server.accept()
        noOfClients += 1
        print(f"Connected: {client_address}")
        
        if noOfClients == num_clients_expected:
            # Send a start game message when the expected number of clients are connected.
            start_message = {'command': 'start_game'}
            for client in [client_socket]:
                client.sendall(json.dumps(start_message).encode('utf-8'))
            # Create a thread to handle communication with the client.
        client_thread = threading.Thread(target=handleClient, args=(client_socket,cid))
        client_thread.start()
        
        
        
