# =================================================================================================
# Contributing Authors:	    Roshan Shrestha, David Webster & Nnaemeka Okafor
# Email Addresses:          rsh251@uky.edu dwe245@uky.edu
# Date:                     11/08/2023
# Purpose:                  Server side of the game
# =================================================================================================
import queue
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
client_queue = queue.Queue()
spectator_queue = queue.Queue()

# global state
clients_configured = [0, 0]
scores = [0, 0]
paddle_positions = [0, 0]
ball_pos = [0, 0]
somebody_has_won = False  # todo
winning_score = 10

# Initialize the game state to store paddle positions.
paddlePos = {
    'firstPlayer': {'y': 0},
    'secondPlayer': {'y': 0}
}


def handle_client(client_socket: socket.socket, client_address: socket.socket) -> None:
    global scores
    global paddle_positions
    global ball_pos

    if client_queue.qsize() == 1:
        print("client 1 connected, now waiting for 2")
        return
    elif client_queue.qsize() == 2:
        print("client 2 connected")
        handle_players(client_queue.queue[0], client_queue.queue[1])
    else:
        print("New spectator joined")
        spectator_queue.put(client_socket)

        thread_spect = threading.Thread(target=handle_spectator, args=(client_socket,))
        thread_spect.start()


# Todo run this in a thread?
def handle_spectator(client_socket: socket.socket) -> None:
    cmd = {'command': 'game_parameters'}
    cmd['screen_width'] = 600
    cmd['screen_height'] = 400
    cmd['whoami'] = "s"
    client_socket.sendall(json.dumps(cmd).encode('utf-8'))
    receiveAck(client_socket)

    cmd = {'command': 'start_game'}
    client_socket.sendall(json.dumps(cmd).encode('utf-8'))
    receiveAck(client_socket) #todo


    while True:
        # make each player see the other person...
        cmd = {'command': 'UPDATE_TIME'}
        cmd['score'] = scores
        cmd['ball'] = ball_pos
        # cmd['enemys_y'] = paddle_positions[1] #todo p1 and p2 y
        cmd['left_y'] = paddle_positions[0]
        cmd['right_y'] = paddle_positions[1]
        client_socket.sendall(json.dumps(cmd).encode('utf-8'))
        receiveAck(client_socket)

        # let them play...
        cmd = {'command': 'justgo'}
        client_socket.sendall(json.dumps(cmd).encode('utf-8'))
        receiveAck(client_socket)

        if scores[0] == winning_score or scores[1] == winning_score:
            somebody_has_won = True

        if scores[0] == winning_score:
            cmd = {'command': 'leftwin'}
            client_socket.sendall(json.dumps(cmd).encode('utf-8'))
            break

        if scores[1] == winning_score:
            cmd = {'command': 'rightwin'}
            client_socket.sendall(json.dumps(cmd).encode('utf-8'))
            break



def handle_players(client_socket1: socket.socket, client_socket2: socket.socket) -> None:
    global scores
    global paddle_positions
    global ball_pos

    cmd = {'command': 'game_parameters'}
    cmd['screen_width'] = 600
    cmd['screen_height'] = 400
    cmd['whoami'] = "l"
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
    while True:
        # Ask for paddle data...
        cmd = {'command': 'send_me_paddle_data'}
        client_socket1.sendall(json.dumps(cmd).encode('utf-8'))
        client_socket2.sendall(json.dumps(cmd).encode('utf-8'))

        # Update paddle variables...
        data = client_socket1.recv(1024)
        stuff = json.loads(data.decode('utf-8'))

        # new_positions = [0, 0]

        # for 1
        paddle_positions[0] = stuff['y']
        # new_positions[0] = stuff['y']
        ball_pos = stuff['ball']
        scores = stuff['score']

        # for 2
        data = client_socket2.recv(1024)
        stuff = json.loads(data.decode('utf-8'))

        paddle_positions[1] = stuff['y']

        # make each player see the other person...
        cmd = {'command': 'UPDATE_TIME'}
        cmd['score'] = scores
        cmd['ball'] = ball_pos
        cmd['enemys_y'] = paddle_positions[1]
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

        if scores[0] == winning_score or scores[1] == winning_score:
            somebody_has_won = True

        if scores[0] == winning_score:
            cmd = {'command': 'youwin'}
            client_socket1.sendall(json.dumps(cmd).encode('utf-8'))
            cmd = {'command': 'youlose'}
            client_socket2.sendall(json.dumps(cmd).encode('utf-8'))
            break

        if scores[1] == winning_score:
            cmd = {'command': 'youlose'}
            client_socket1.sendall(json.dumps(cmd).encode('utf-8'))
            cmd = {'command': 'youwin'}
            client_socket2.sendall(json.dumps(cmd).encode('utf-8'))
            break
    start_server()
def receiveAck(client:socket.socket) -> None:
    received = client.recv(1024)
    data = received.decode('utf-8')
    jsonData = json.loads(data)
    if jsonData.get("ack", None) is None:
        raise Exception("THIS CLIENT IS DISOBEDIENT. IT DID NOT ACK ME")
    return

def start_server() -> None:
    global noOfClients
    global client_queue
    global spectator_queue

    # global state
    global clients_configured
    global scores
    global paddle_positions
    global ball_pos
    global somebody_has_won
    global winning_score

    # Initialize the game state to store paddle positions.
    global paddlePos

    noOfClients = 0
    client_queue = queue.Queue()
    spectator_queue = queue.Queue()

    # global state
    clients_configured = [0, 0]
    scores = [0, 0]
    paddle_positions = [0, 0]
    ball_pos = [0, 0]
    somebody_has_won = False  # todo
    winning_score = 20

    # Initialize the game state to store paddle positions.
    paddlePos = {
        'firstPlayer': {'y': 0},
        'secondPlayer': {'y': 0}
    }

    # Create a socket to listen for incoming connections.
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 9999))
    server.listen(5)  # todo
    actual_server_address = server.getsockname()
    print(f"Server is listening at {actual_server_address[0]} and port: {actual_server_address[1]}")

    while True:
        client_socket, client_address = server.accept()
        client_queue.put(client_socket)

        thread_accept = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread_accept.start()


if __name__ == "__main__":
    start_server()