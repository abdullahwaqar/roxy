import sys
import socket
from threading import Thread

class Proxy2Server(Thread):

    def __init__(self, host, port):
        super(Proxy2Server, self).__init__()
        self.port = port
        self.host = host
        self.client  = None
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((host, port))

    #run in thread
    def run(self):
        while True:
            data = self.server.recv(4096)
            if data:
                #forward it to client
                print("[ {} ] -> {}".format(self.port, data[:100].encode('hex')))
                self.client.sendall(data)


class Client2Proxy(Thread):

    def __init__(self, host, port):
        super(Client2Proxy, self).__init__()
        self.port = port
        self.host = host
        self.server = None
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(1)
        #wait for connection
        self.client, addr = sock.accept()

    def run(self):
        while True:
            data = self.client.recv(4096)
            if data:
                #forward to server
                print("[ {} ] <- {}".format(self.port, data[:100].encode('hex')))
                self.server.sendall(data)


class Proxy(Thread):

    def __init__(self, from_host, to_host, port):
        super(Proxy, self).__init__()
        self.from_host = from_host
        self.to_host = to_host
        self.port = port

    def run(self):
        while True:
            print("~->[ proxy({}) ] Setting Up".format(self.port))
            self.c2p = Client2Proxy(self.from_host, self.port)
            self.s2p = Client2Proxy(self.to_host, self.port)
            print("~->[ proxy({}) ] Connection Established".format(self.port))
            self.c2p.server = self.s2p.server
            self.s2p.server = self.c2p.server

            self.c2p.start()
            self.s2p.start()

if __name__ == '__main__':
    try:
        #Listen on All Interfaces, Real Server IP
        master_server = Proxy('0.0.0.0', str(sys.argv[1]), int(sys.argv[2]))
        master_server.start()
    except KeyboardInterrupt:
        try:
            sys.exit(0)
        except Exception as e:
            print(e)
    except Exception as identifier:
        print(identifier)