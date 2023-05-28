import socket
from _thread import *
from Game import Game
from constants import *
import pickle
from Lobby import Lobby

import sys
import traceback

class Server:
    def __init__(self, lobby_leader_id: int) -> None:
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
        self.playerShipUpdates: dict = {}
        self.game = Game()

        self.clock = pygame.time.Clock()
        self.currentPlayer = 0
        self.running = False
        self.game_started = False
        self.lobby = Lobby(self.local_ip, lobby_leader_id)
        start_new_thread(self.run, ())
    
    def run(self):
        self.running = True
        while self.running:
            self.accept_connections()

    def loop(self):
        while self.running:
            self.game.update()
            self.clock.tick(60)


    def threaded_client(self, conn, player_id: int):
        player_data = self.lobby.get_player(player_id)
        player_id = player_data['player_id']
        conn.send(pickle.dumps(player_data['color']))
        reply = ""
        while self.running:
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
                        res = self.playerShipUpdates[str(player_id)]
                        self.playerShipUpdates[str(player_id)] = []
                    elif data == 'ready':
                        self.lobby.set_player_ready(player_id, True)
                        res = 'ok'
                    elif data == 'notReady':
                        self.lobby.set_player_ready(player_id, False)
                        res = 'ok'
                    elif data == 'start':
                        start_new_thread(self.loop, ())
                        self.game_started = True
                        self.lobby.open = False
                        res = 'ok'
                    else:
                        #send ships
                        shipCountBefore = self.game.planets[data[0]].ships
                        self.game.sendShips(data[0], data[1])
                        #update for other players
                        for id in self.playerShipUpdates.keys():
                            if id != player_id:
                                shipsSent = shipCountBefore - self.game.planets[data[0]].ships
                                self.playerShipUpdates[id].append([data[0], data[1], shipsSent])
                        gameCopy = Game()
                        gameCopy.planets = self.game.planets
                        res = gameCopy

                    # print("Sending : ", res)

                conn.sendall(pickle.dumps(res))

            except Exception as e:
                # # Get current system exception
                # ex_type, ex_value, ex_traceback = sys.exc_info()

                # # Extract unformatter stack traces as tuples
                # trace_back = traceback.extract_tb(ex_traceback)

                # # Format stacktrace
                # stack_trace = list()

                # for trace in trace_back:
                #     stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))

                # print("Exception type : %s " % ex_type.__name__)
                # print("Exception message : %s" %ex_value)
                # print("Stack trace : %s" %stack_trace)
                break

        print("Lost connection")
        self.lobby.remove_player(player_data['player_id'])
        conn.close()

    def accept_connections(self):
        print('server waiting for client ping')
        conn, addr = self.socket.accept()
        try:
            message = pickle.loads(conn.recv(2048))
            print('message: ',message)
            if message == 'checking':
                print('got check message from ', addr)
                conn.send(pickle.dumps(self.lobby))
            elif message[0] == 'connect':
                nick = message[1]
                player_id = message[2]
                if self.lobby.add_player(player_id, nick):
                    print("Connected to:", addr)
                    self.playerShipUpdates[str(player_id)] = []
                    start_new_thread(self.threaded_client, (conn, player_id))
                else:
                    conn.send(pickle.dumps('403'))
                    conn.close()
        # except Exception as e:
        #     # Get current system exception
        #     ex_type, ex_value, ex_traceback = sys.exc_info()

        #     # Extract unformatter stack traces as tuples
        #     trace_back = traceback.extract_tb(ex_traceback)

        #     # Format stacktrace
        #     stack_trace = list()

        #     for trace in trace_back:
        #         stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))

        #     print("Exception type : %s " % ex_type.__name__)
        #     print("Exception message : %s" %ex_value)
        #     print("Stack trace : %s" %stack_trace)
        #     print(message)
        #     print('got invalid message from ', addr)
        except:
            conn.close()
    
    def end(self):
        print('server end')
        self.running = False
        self.socket.close()