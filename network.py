import socket
import pickle
from constants import *


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.settimeout(0.01)
        self.connected = False
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        network = '.'.join(local_ip.split('.')[0:3])
        for i in range(1, 255):
            serverFound = self.check(f'{network}.{i}', NETWORK_PORT)
            if serverFound:
                print('server found')
                self.server = f'{network}.{i}'
                self.port = NETWORK_PORT
                self.addr = (self.server, self.port)
                self.p = self.connect()
                self.connected = True
                break
        if not self.connected:
            print('didnt find any server on lan')

    def getP(self):
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)
            self.client.send(pickle.dumps('connect'))
            return pickle.loads(self.client.recv(2048))
        except:
            pass

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            serverResp = self.client.recv(2048)
            return pickle.loads(serverResp)
        except socket.error as e:
            print(e)
    
    def check(self, host, port):
        print(f'checking {host}:{port}')
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #presumably 
        sock.settimeout(0.01)
        try:
            sock.connect((host,port))
        except:
            return False
        else:
            sock.send(pickle.dumps('checking'))
            sock.close()
        return True