# =================================================================================================
# Contributing Authors:	    Roshan Shrestha & David Webster
# Email Addresses:          rsh251@uky.edu dwe245@uky.edu
# Date:                     11/03/20
# Purpose:                  To handle the client side of the game
# =================================================================================================

import pygame
import tkinter as tk
import sys
import socket
import json
import time
from assets.code.helperCode import *

def acknowledge(client:socket.socket):
    data = {"ack": 'surething'}
    jsonData = json.dumps(data)
    client.sendall(jsonData.encode('utf-8'))

# This is the main game loop.  For the most part, you will not need to modify this.  The sections
# where you should add to the code are marked.  Feel free to change any part of this project
# to suit your needs.
def playGame(screenWidth:int, screenHeight:int, playerPaddle:str, client:socket.socket) -> None:

    # Pygame inits
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()

    # Constants
    WHITE = (255,255,255)
    clock = pygame.time.Clock()
    scoreFont = pygame.font.Font("./assets/fonts/pong-score.ttf", 32)
    winFont = pygame.font.Font("./assets/fonts/visitor.ttf", 20)
    pointSound = pygame.mixer.Sound("./assets/sounds/point.wav")
    bounceSound = pygame.mixer.Sound("./assets/sounds/bounce.wav")

    # Display objects
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    topWall = pygame.Rect(-10,0,screenWidth+20, 10)
    bottomWall = pygame.Rect(-10, screenHeight-10, screenWidth+20, 10)
    centerLine = []
    for i in range(0, screenHeight, 10):
        centerLine.append(pygame.Rect((screenWidth/2)-5,i,5,5))

    # Paddle properties and init
    paddleHeight = 50
    paddleWidth = 10
    paddleStartPosY = (screenHeight/2)-(paddleHeight/2)
    leftPaddle = Paddle(pygame.Rect(10,paddleStartPosY, paddleWidth, paddleHeight))
    rightPaddle = Paddle(pygame.Rect(screenWidth-20, paddleStartPosY, paddleWidth, paddleHeight))

    ball = Ball(pygame.Rect(screenWidth/2, screenHeight/2, 5, 5), -5, 0)

    if playerPaddle == "l":
        opponentPaddleObj = rightPaddle
        playerPaddleObj = leftPaddle
    else:
        opponentPaddleObj = leftPaddle
        playerPaddleObj = rightPaddle

    lScore = 0
    rScore = 0

    while True:
        # Wiping the screen
        screen.fill((0,0,0))
        
        # WAIT FOR THE SERVER TO SEND US A COMMAND....
        while True:
            data = client.recv(1024)
            cmd = json.loads(data.decode('utf-8'))
            
            if cmd['command'] == 'send_me_paddle_data':
                paddleData = {
                    'y': playerPaddleObj.rect.y,  
                    'ball': [ball.rect.x, ball.rect.y],  # Ball position [x, y]
                    'score': [lScore, rScore],  # Scores for left and right players
                }
                jsonData = json.dumps(paddleData)
                client.sendall(jsonData.encode('utf-8'))
            elif cmd['command'] == 'UPDATE_TIME':
                lscore = cmd['score'][0]
                rscore = cmd['score'][1]
                ball.rect.x = cmd['ball'][0]
                ball.rect.y = cmd['ball'][1]
                opponentPaddleObj.rect.y = cmd['enemys_y']
                # todo: ack
                acknowledge(client)
            elif cmd['command'] == 'youwin':
                textSurface = winFont.render("bro you won", False, WHITE, (0,0,0))
                textRect = textSurface.get_rect()
                textRect.center = ((screenWidth/2), screenHeight/2)
                screen.blit(textSurface, textRect)
                while True:
                    pygame.display.flip()
                    clock.tick(60)
            elif cmd['command'] == 'youlose':
                textSurface = winFont.render("step it up bro", False, WHITE, (0,0,0))
                textRect = textSurface.get_rect()
                textRect.center = ((screenWidth/2), screenHeight/2)
                screen.blit(textSurface, textRect)
                while True:
                    pygame.display.flip()
                    clock.tick(60)
            elif cmd['command'] == 'justgo':
                acknowledge(client)
                break

        

        # Getting keypress events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    playerPaddleObj.moving = "down"

                elif event.key == pygame.K_UP:
                    playerPaddleObj.moving = "up"

            elif event.type == pygame.KEYUP:
                playerPaddleObj.moving = ""

        # =========================================================================================
        # Your code here to send an update to the server on your paddle's information,
        # where the ball is and the current score.
        # Feel free to change when the score is updated to suit your needs/requirements




        # =========================================================================================

        # Update the player paddle and opponent paddle's location on the screen
        for paddle in [playerPaddleObj, opponentPaddleObj]:
            if paddle.moving == "down":
                if paddle.rect.bottomleft[1] < screenHeight-10:
                    paddle.rect.y += paddle.speed
            elif paddle.moving == "up":
                if paddle.rect.topleft[1] > 10:
                    paddle.rect.y -= paddle.speed

        # ==== Ball Logic =====================================================================
        ball.updatePos()

        # If the ball makes it past the edge of the screen, update score, etc.
        if ball.rect.x > screenWidth:
            lScore += 1
            pointSound.play()
            ball.reset(nowGoing="left")
        elif ball.rect.x < 0:
            rScore += 1
            pointSound.play()
            ball.reset(nowGoing="right")

        # If the ball hits a paddle
        if ball.rect.colliderect(playerPaddleObj.rect):
            bounceSound.play()
            ball.hitPaddle(playerPaddleObj.rect.center[1])
        elif ball.rect.colliderect(opponentPaddleObj.rect):
            bounceSound.play()
            ball.hitPaddle(opponentPaddleObj.rect.center[1])

        # If the ball hits a wall
        if ball.rect.colliderect(topWall) or ball.rect.colliderect(bottomWall):
            bounceSound.play()
            ball.hitWall()

        pygame.draw.rect(screen, WHITE, ball)
            # ==== End Ball Logic =================================================================

        # Drawing the dotted line in the center
        for i in centerLine:
            pygame.draw.rect(screen, WHITE, i)

        # Drawing the player's new location
        for paddle in [playerPaddleObj, opponentPaddleObj]:
            pygame.draw.rect(screen, WHITE, paddle)

        pygame.draw.rect(screen, WHITE, topWall)
        pygame.draw.rect(screen, WHITE, bottomWall)
        updateScore(lScore, rScore, screen, WHITE, scoreFont)
        pygame.display.flip()
        clock.tick(60)
   
        


        # =========================================================================================




# This is where you will connect to the server to get the info required to call the game loop.  Mainly
# the screen width, height and player paddle (either "left" or "right")
# If you want to hard code the screen's dimensions into the code, that's fine, but you will need to know
# which client is which

waiting_for_opponent = False  # Global flag to indicate if the client is waiting
game_started = False  # Global flag to indicate if the game has started


def joinServer(ipEntry:str, portEntry:str, errorLabel:tk.Label, app:tk.Tk) -> None:
    # Purpose:      This method is fired when the join button is clicked
    # Arguments:
    # ip            A string holding the IP address of the server
    # port          A string holding the port the server is using
    # errorLabel    A tk label widget, modify it's text to display messages to the user (example below)
    # app           The tk window object, needed to kill the window

    # Create a socket and connect to the server
    # You don't have to use SOCK_STREAM, use what you think is best
    global waiting_for_opponent
    global game_started
    
    if ipEntry == '':
        ipEntry = "127.0.0.1"
    if portEntry == '':
        portEntry = "9999"


    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ipEntry, int(portEntry)))


    errorLabel.config(text="Waiting for another player to join . . .")
    errorLabel.update()
    
    
    screenWidth = 0
    screenHeight = 0
    side = 0


             
    while True:
        #1 receive command from server
        received = client.recv(1024)
        data = received.decode('utf-8')
        jsonData = json.loads(data)


        #Get game parameters

        # Huh?
        if jsonData['command'] == 'game_parameters':
            side = jsonData.get("whoami", None)
            screenHeight = jsonData['screen_height']
            screenWidth = jsonData['screen_width']
            acknowledge(client)
        elif jsonData['command'] == 'start_game':
            waiting_for_opponent = False
            game_started = True
            acknowledge(client)
            break
        time.sleep(1)  
    print(f"Received request from server: {data}")

    #client.close()

    # Close this window and start the game with the info passed to you from the server
    app.withdraw()     # Hides the window (we'll kill it later)
    playGame(screenWidth, screenHeight, side, client)  # User will be either left or right paddle
    app.quit()         # Kills the window


# This displays the opening screen, you don't need to edit this (but may if you like)
def startScreen():
    app = tk.Tk()
    app.title("Server Info")

    image = tk.PhotoImage(file="./assets/images/logo.png")

    titleLabel = tk.Label(image=image)
    titleLabel.grid(column=0, row=0, columnspan=2)

    ipLabel = tk.Label(text="Server IP:")
    ipLabel.grid(column=0, row=1, sticky="W", padx=8)

    ipEntry = tk.Entry(app)
    ipEntry.grid(column=1, row=1)

    portLabel = tk.Label(text="Server Port:")
    portLabel.grid(column=0, row=2, sticky="W", padx=8)

    portEntry = tk.Entry(app)
    portEntry.grid(column=1, row=2)

    errorLabel = tk.Label(text="")
    errorLabel.grid(column=0, row=4, columnspan=2)

    joinButton = tk.Button(text="Join", command=lambda: joinServer(ipEntry.get(), portEntry.get(), errorLabel, app))
    joinButton.grid(column=0, row=3, columnspan=2)

    waiting_label = tk.Label(text="Waiting for Opponent to Join...", fg="blue")
    waiting_label.grid(column=0, row=4, columnspan=2)
    waiting_label.grid_remove()  # Hide the label initially

    while True:
        if waiting_for_opponent:
            joinButton.config(state="disabled")
            waiting_label.grid()
        else:
            joinButton.config(state="normal")
            waiting_label.grid_remove()

        app.update()
        if game_started:
            break

    app.mainloop()

if __name__ == "__main__":
    startScreen()

    # Uncomment the line below if you want to play the game without a server to see how it should work
    # the startScreen() function should call playGame with the arguments given to it by the server this is
    # here for demo purposes only
    #playGame(640, 480,"left",socket.socket(socket.AF_INET, socket.SOCK_STREAM))
