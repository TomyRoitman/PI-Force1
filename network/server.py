import sys
from abc import ABC, abstractmethod
import socket


class Server(socket.socket):

    @property
    @abstractmethod
    def handle_client_method(self):
        pass

    @abstractmethod
    def run(self):
        pass


class TCPServer(Server, ABC):

    def __init__(self, address, running=True, listen_amount=5):
        super().__init__()
        self.address = address
        self.listen_amount = listen_amount
        self.running = True

    def set_handle_client_method(self, method):
        self.__handle_client_method = method

    @property
    def handle_client_method(self):
        return self.__handle_client_method

    def run(self):
        self.bind(self.address)
        self.listen(self.listen_amount)

        while self.running:
            client_socket, address = self.accept()
            self.handle_client_method.value(client_socket)


class UDPServer(Server, ABC):

    def __init__(self, address, running=True):
        super().__init__(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = address

    def set_handle_client_method(self, method):
        self.__handle_client_method = method

    @property
    def handle_client_method(self):
        return self.__handle_client_method

    def run(self):
        self.bind(self.address)


def main():
    tcp = TCPServer(('localhost', 15))
    repr(tcp)
    print(type(tcp))
    tcp.bind(('localhost', 15))
    tcp.listen(5)

    udp = UDPServer(('localhost', 16))
    repr(udp)
    print(type(udp))
    udp.bind(('localhost', 16))
    while True:
        print(sys.stderr, '\nwaiting to receive message')
        data, address = udp.recvfrom(4096)

        print(sys.stderr, 'received %s bytes from %s' % (len(data), address))
        print(sys.stderr, data)

        if data:
            sent = udp.sendto(data, address)
            print(sys.stderr, 'sent %s bytes back to %s' % (sent, address))


if __name__ == '__main__':
    main()
