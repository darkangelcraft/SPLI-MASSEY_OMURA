from socket import *


# from mylibrary import *
class mysocket:
    __MSGLEN = 100

    def __init__(self, sock=None):
        if sock is None:
            self.__sock = socket(AF_INET, SOCK_STREAM)
            self.__sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        else:
            self.__sock = sock

    def connect(self, host, port):
        self.__sock.connect((host, port))

    # ridefinisce la send in maniera tale da inviare messaggi lunghi
    def send(self, msg):
        MSGLEN = len(msg)
        totalsent = 0
        while totalsent < MSGLEN:
            sent = self.__sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("connessioni socket interrotta")
            totalsent = totalsent + sent

    # ridefinisce la receive
    def receive(self, MSGLEN):
        msg = b''
        while len(msg) < MSGLEN:
            chunk = self.__sock.recv(MSGLEN - len(msg))
            if chunk == b'':
                raise RuntimeError("Connessione socket interrotta")
            msg += chunk
        return msg

    # definisce il bind
    def bind(self, host, port):
        self.__sock.bind((host, port))

    # def bind(self, port):
    #	self.__sock.bind((gethostname(), port))

    # definisce listen
    def listen(self, value):
        self.__sock.listen(value)

    # definisce accept
    def accept(self):
        return self.__sock.accept()

    # definisce shutdown
    def shutdown(self, arg):
        return self.__sock.shutdown(arg)

    # definisce close
    def close(self):
        return self.__sock.close()

    # imposta la lunghezza massima del messaggio bufferizzato
    # def setLength(self, length):
    # if(not(is_integer(length))):
    # print "errore lunghezza messaggio bufferizzato, impostato valore di default 100B"
    # else: self.__MSGLEN = length
