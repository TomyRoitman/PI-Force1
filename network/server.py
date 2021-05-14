import sys
from abc import ABC, abstractmethod
import socket
import threading


class Server(socket.socket):

    @abstractmethod
    def run(self):
        pass


class TCPServer(Server, ABC):

    def __init__(self, address, recv_size, handle_client_method, running=True, listen_amount=5):
        super().__init__()
        self.recv_size = recv_size
        self.handle_client_method = handle_client_method
        self.address = address
        self.listen_amount = listen_amount
        self.running = True

    def get_run_method(self):
            return self.run

    def run(self):
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind(self.address)
        self.listen(self.listen_amount)

        while self.running:
            client_socket, address = self.accept()
            self.handle_client_method(client_socket)


class UDPServer(Server, ABC):

    def __init__(self, address, recv_size, running=True):
        super().__init__(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_size = recv_size
        self.address = address
        self.running = running
        self.message_queue_lock = threading.Lock()
        self.message_queue = []

    def get_message(self):
        if not self.message_queue:
            return None
        self.message_queue_lock.acquire()
        msg = self.message_queue.pop(0)
        self.message_queue_lock.release()
        # print("getting message")
        return msg

    def __insert_message_to_queue(self, data):
        self.message_queue_lock.acquire()
        # print("Appending data: ", data)
        self.message_queue.append(data)
        self.message_queue_lock.release()

    def get_run_method(self):
        return self.run

    def run(self):
        print("running")
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind(self.address)
        while self.running:
            data, address = self.recvfrom(self.recv_size)
            # print("Received data: ", data)
            self.__insert_message_to_queue(data)


def main():
    tcp = TCPServer(('localhost', None, 15))
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
