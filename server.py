import socket
from _thread import *
from Game import Game
from constants import *
import pickle

import sys
import traceback

pygame.init()

server = NETWORK_HOST
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")

playerCount = 0
playerColors = [COLOR_BLUE, COLOR_RED]
playerShipUpdates = []
game = Game()

clock = pygame.time.Clock()

def loop():
    while True:
        game.update()
        clock.tick(60)


def threaded_client(conn, player):
    conn.send(pickle.dumps(playerColors[player]))
    reply = ""
    while True:
        try:
            data = pickle.loads(conn.recv(2048))
            # players[player] = data

            if not data:
                print("Disconnected")
                break
            # elif data[0] == 'sendUpdate':
            #     game = data[1]
            else:
                print("Received: ", data)
                if data == 'get':
                    gameCopy = Game()
                    gameCopy.planets = game.planets
                    res = gameCopy
                elif data == 'getShipUpdates':
                    res = playerShipUpdates[player]
                    playerShipUpdates[player] = []
                else:
                    #send ships
                    print("TAK NEVIM PICO")
                    shipCountBefore = game.planets[data[0]].ships
                    game.sendShips(data[0], data[1])
                    for i in range(0, playerCount):
                        if i != player:
                            shipsSent = shipCountBefore - game.planets[data[0]].ships
                            playerShipUpdates[i].append([data[0], data[1], shipsSent])
                    gameCopy = Game()
                    gameCopy.planets = game.planets
                    res = gameCopy

                print("Sending : ", res)

            conn.sendall(pickle.dumps(res))
        except Exception as e:
            # Get current system exception
            ex_type, ex_value, ex_traceback = sys.exc_info()

            # Extract unformatter stack traces as tuples
            trace_back = traceback.extract_tb(ex_traceback)

            # Format stacktrace
            stack_trace = list()

            for trace in trace_back:
                stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))

            print("Exception type : %s " % ex_type.__name__)
            print("Exception message : %s" %ex_value)
            print("Stack trace : %s" %stack_trace)
            break

    print("Lost connection")
    conn.close()

currentPlayer = 0

start_new_thread(loop, ())

while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    start_new_thread(threaded_client, (conn, currentPlayer))
    playerShipUpdates.append([])
    currentPlayer += 1
    playerCount += 1