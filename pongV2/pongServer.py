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

# Author: Roshan Shrestha
# Purpose: This function is to handle communication with client


def handleClient(client_socket):
    global paddlePos
    global noOfClients
    
    try:
        while True:
            # Receive data from the client.
            data = client_socket.recv(1024)
            if not data:
                break
            
            # Decode and parse the request from the client.
            decoded_data = data.decode('utf-8')
            client_request = json.loads(decoded_data)

            print(f"Received request from client: {client_request}")

            if client_request["request"] == "get_game_parameters":
                # Respond with game parameters like screen dimensions and paddle position.
                response = {
                    'screen_width': 600,
                    'screen_height': 400,
                    'paddle_position': 'right'
                }
                client_socket.sendall(json.dumps(response).encode('utf-8'))
            
            elif client_request["request"] == "paddleUpdate":
                paddlePos['firstPlayer']['y_position'] = int(client_request['y_position'])
                

            elif client_request["request"] == "getPaddleOpponent":
                response = {
                    'oppo_paddle_pos': paddlePos['secondPlayer']['y_position']
                }
                client_socket.sendall(json.dumps(response).encode('utf-8'))

            

        

    except Exception as e:
        print(f"Error in handling client: {e}")
    finally:
        client_socket.close()


# Initialize the game state to store paddle positions.
paddlePos = {
    'firstPlayer': {'y_position': 0},
    'secondPlayer': {'y_position': 30}
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
noOfClients = 0

# 
for _ in range(num_clients_expected):
    # Accept a new client connection.
    client_socket, client_address = server.accept()
    noOfClients += 1
    print(f"Connected: {client_address}")

    if noOfClients == num_clients_expected:
        # Send a start game message when the expected number of clients are connected.
        start_message = {'request': 'start_game'}
        for client in [client_socket]:
            client.sendall(json.dumps(start_message).encode('utf-8'))

    # Create a thread to handle communication with the client.
    client_thread = threading.Thread(target=handleClient, args=(client_socket,))
    client_thread.start()
