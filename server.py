import socket
from _thread import *
from Game import Game
from constants import *
import pickle
from Lobby import Lobby

import sys
import traceback

class Server:
    def __init__(self) -> None:
        pygame.init()

        self.hostname = socket.gethostname()
        self.local_ip = socket.gethostbyname(self.hostname)
        self.port = NETWORK_PORT

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.socket.bind((self.local_ip, self.port))
        except socket.error as e:
            str(e)

        self.socket.listen(2)
        print(f'Server started on {self.local_ip}:{self.port}')

        self.playerCount = 0
        self.playerColors = [COLOR_BLUE, COLOR_RED, COLOR_YELLOW]
        self.playerShipUpdates = []
        self.game = Game()

        self.clock = pygame.time.Clock()
        self.currentPlayer = 0
        self.running = False
        self.game_started = True
        self.lobby = Lobby()
        start_new_thread(self.loop, ())
    
    def run(self):
        self.running = True
        while self.running:
            self.accept_connections()

    def loop(self):
        while self.running:
            self.game.update()
            self.clock.tick(60)


    def threaded_client(self, conn, player):
        conn.send(pickle.dumps(self.playerColors[player]))
        print(self.playerColors[player])
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
                    # print("Received: ", data)
                    if data == 'get':
                        if self.game_started:
                            gameCopy = Game()
                            gameCopy.planets = self.game.planets
                            res = gameCopy
                        else:
                            res = self.lobby
                    elif data == 'getShipUpdates':
                        res = self.playerShipUpdates[player]
                        self.playerShipUpdates[player] = []
                    else:
                        #send ships
                        shipCountBefore = self.game.planets[data[0]].ships
                        self.game.sendShips(data[0], data[1])
                        for i in range(0, self.playerCount):
                            if i != player:
                                shipsSent = shipCountBefore - self.game.planets[data[0]].ships
                                self.playerShipUpdates[i].append([data[0], data[1], shipsSent])
                        gameCopy = Game()
                        gameCopy.planets = self.game.planets
                        res = gameCopy

                    # print("Sending : ", res)

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
        self.lobby.players_connected -= 1
        conn.close()

    def accept_connections(self):
        conn, addr = self.socket.accept()
        try:
            message = pickle.loads(conn.recv(2048))
            print(message)
            if message == 'checking':
                print('got check message from ', addr)
            elif message == 'connect':
                print("Connected to:", addr)
                self.playerShipUpdates.append([])
                start_new_thread(self.threaded_client, (conn, self.currentPlayer))
                self.currentPlayer += 1
                self.playerCount += 1
                self.lobby.players_connected += 1
        except:
            print('got invalid message from ', addr)
            conn.close()
    
    def end(self):
        self.running = False
        self.socket.close()