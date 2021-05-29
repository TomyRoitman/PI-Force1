import socket
import sys
import threading
from os import urandom

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto import Random
from network.aes_utils import AESCipher
RSA_KEY_SIZE = 128

class TCPStream:
    """
    Allowing tcp stream between client and server.
    """

    def __init__(self, sock, recv_size, msg_code_size, msg_size_header_size, msg_chunk_size, is_server: bool = False):
        """
        Initialize TCPStream object
        :param sock: socket.socket
        :param recv_size: how many bytes to receive every time
        :param msg_code_size: size of msg_code
        :param msg_size_header_size: size of msg_size_header
        :param msg_chunk_size: size of msg_chunk
        :param is_server: Is the stream on the server side.
    """
        self.sock = sock
        self.recv_size = recv_size
        self.msg_code_size = msg_code_size
        self.msg_size_header_size = msg_size_header_size
        self.msg_chunk_size = msg_chunk_size
        self.is_server = is_server
        self.aes_cipher = None
        if self.is_server:
            self.generate_aes_key_from_server_side()
        else:
            self.generate_aes_key_from_client_side()

    def generate_aes_key_from_client_side(self):
        """
        Generate aes keys with RSA from client side
        :param is_server:
        Creates AESCipher object for aes encryption.
        """
        data_length, data = self.recv_by_size()
        pub_key = RSA.import_key(data, passphrase=None)
        rsa_cipher = PKCS1_OAEP.new(pub_key)
        aes_key = urandom(16)
        aes_key_ciphered = rsa_cipher.encrypt(aes_key)
        self.send_by_size(aes_key_ciphered)
        self.aes_cipher = AESCipher(aes_key)

    def generate_aes_key_from_server_side(self):
        """
        Generate aes key with RSA from server side
        Creates AESCipher object for aes encryption.
        """
        random_generator = Random.new().read
        key = RSA.generate(RSA_KEY_SIZE * 8, random_generator)
        self.send_by_size(key.publickey().exportKey(format='PEM', passphrase=None, pkcs=1))
        cipher = PKCS1_OAEP.new(key)
        data_length, data = self.recv_by_size()
        aes_key = cipher.decrypt(data)
        self.aes_cipher = AESCipher(aes_key)

    def recv_by_size(self):
        """
        Receive tcp message by a certain size mentioned in the first 8 characters of the message.
        :return: content_length, content
        """
        size_header = ""
        while len(size_header) < self.msg_size_header_size:
            size_header += self.sock.recv(self.msg_size_header_size - len(size_header)).decode()

        content_length = int(size_header)
        content = b""
        while len(content) < content_length:
            content += self.sock.recv(content_length - len(content))

        if self.aes_cipher is not None:
            self.aes_cipher.decrypt(content)
        return content_length, content

    def recv_by_size_with_timeout(self, interval):
        """
        Receive tcp message by a certain size mentioned in the first 8 characters of the message, limited to a certain
        waiting time.
        :param interval: How long to wait for a message.
        :return: content_length, content
        """
        self.sock.settimeout(interval)

        size_header = ""
        while len(size_header) < self.msg_size_header_size:
            try:
                size_header += self.sock.recv(self.msg_size_header_size - len(size_header)).decode()
            except socket.timeout:
                return "Not received yet"
        content_length = int(size_header)
        content = ""
        while len(content) < content_length:
            try:
                content += self.sock.recv(content_length - len(content)).decode()
            except socket.timeout:
                return "Not received yet"

        if self.aes_cipher is not None:
            self.aes_cipher.decrypt(content)

        return content_length, content

    def __split_by_len(self, seq, length):
        """
        :param seq: Sequence to split
        :param length: Chunks size
        :return: List containing chunks of a sequence, split by length.
        """
        return [seq[x: x + length] for x in range(0, len(seq), length)]

    def send_by_size(self, message):
        """
        Sends message with the size in the beginning.
        :param message:
        """
        header = str(len(message)).zfill(self.msg_size_header_size).encode()
        self.sock.send(header)
        encrypted = self.aes_cipher.encrypt(message)
        chunks = self.__split_by_len(encrypted, self.msg_chunk_size)
        for chunk in chunks:
            self.sock.send(chunk)


class TCPServer(socket.socket):

    def __init__(self, address, recv_size, msg_code_size=4, msg_size_header_size=8, msg_chunk_size=1024, running=True,
                 listen_amount=5):
        super().__init__()
        # self.tcp_stream = TCPStream(recv_size, msg_code_size, msg_size_header_size, msg_chunk_size)
        self.recv_size = recv_size
        self.msg_code_size = msg_code_size
        self.msg_size_header_size = msg_size_header_size
        self.msg_chunk_size = msg_chunk_size
        self.address = address
        self.listen_amount = listen_amount
        self.running = True
        self.client_socket = None
        self.lock = threading.Lock()

    def get_client(self):
        while self.running:
            if isinstance(self.client_socket, socket.socket):
                client_tcp_stream = TCPStream(self.client_socket, 1024, 4, 8, 1024, True)
                return client_tcp_stream
    def run(self):
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind(self.address)
        self.listen(self.listen_amount)
        client_socket, address = self.accept()
        self.lock.acquire()
        self.client_socket = client_socket
        self.lock.release()
        #
        # while self.running:
        #     client_socket, address = self.accept()
        #     self.handle_client_method(client_socket)


class UDPServer(socket.socket):

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
        return msg

    def __insert_message_to_queue(self, data):
        self.message_queue_lock.acquire()
        # print("Appending data: ", data)
        self.message_queue.append(data)
        self.message_queue_lock.release()

    def get_run_method(self):
        return self.run

    def run(self):
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bind(self.address)
        print("[Log] - Server running on address: ", self.address)
        while self.running:
            data, address = self.recvfrom(self.recv_size)
            # print("[Log] - Received data: ", data)
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
