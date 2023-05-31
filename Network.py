import socket
import pickle
from constants import *
import random
from Lobby import Lobby


class Network:
    def __init__(self, nickname: str = None):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(0.300)
        self.nickname = f'player#{random.randint(0, 1000):04d}'
        if nickname:
            self.nickname = nickname
        self.player_id = random.randint(0, 10000000)
        print (self.nickname)
        self.color = None
        self.connected = False

    def getColor(self):
        return self.color

    def connect(self, ip: str):
        print('connecting as '+self.nickname)
        try:
            self.client.connect((ip, NETWORK_PORT))
            self.client.send(pickle.dumps(['connect', self.nickname, self.player_id]))
            response = pickle.loads(self.client.recv(2048))
            if response == '404':
                return
            self.color = response
            self.connected = True
        except:
            pass

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            serverResp = self.client.recv(2048)
            return pickle.loads(serverResp)
        except socket.error as e:
            print(e)
            return False
    
    def find_games(self):
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        network = '.'.join(local_ip.split('.')[0:3])
        lobbies: list[Lobby] = []
        for i in range(1, 255):
            lobby: Lobby = self.check(f'{network}.{i}', NETWORK_PORT)
            if lobby:
                if lobby.open:
                    print(f'server found {network}.{i}')
                    lobbies.append(lobby)
        return lobbies
    
    def check(self, host, port):
        # print(f'checking {host}:{port}')
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #presumably 
        sock.settimeout(0.01)
        try:
            sock.connect((host,port))
            sock.send(pickle.dumps('checking'))
            reply = pickle.loads(sock.recv(2048))
            print(reply)
        except:
            return None
        else:
            sock.close()
        return reply
