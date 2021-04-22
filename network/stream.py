import struct

import cv2
import numpy as np
import socket


class Streamer:

    def __init__(self, udp_client_socekt: socket.socket, address, destination_address, split_size, buffer_size,
                 times_to_send):
        self.udp_client_socket = udp_client_socekt
        self.destination_address = destination_address
        self.split_size = split_size
        self.buffer_size = buffer_size - 8  # 8 = size of packed indexes
        self.times_to_send = times_to_send

    def __compress_frame(self, frame):
        _, encoded_frame = cv2.imencode('.JPEG', frame)
        return encoded_frame

    def send_image(self, frame, address):
        compressed_frame_chunks = [self.__compress_frame(chunk).flatten().tobytes() for chunk in
                                   np.split(frame, self.split_size)]

        for compressed_chunk_index in range(len(compressed_frame_chunks)):
            packed_compressed_chunk_index = struct.pack('!i', compressed_frame_chunks)
            message_chunks = [compressed_frame_chunks[compressed_chunk_index][i:i + self.buffer_size] for i in
                              range(0, len(compressed_frame_chunks[compressed_chunk_index]), self.buffer_size)]
            for message_chunk_index in range(len(message_chunks)):
                for i in self.times_to_send:
                    packed_message_chunk_index = struct.pack('!i', message_chunk_index)
                    self.udp_client_socket.sendto(
                        packed_compressed_chunk_index + packed_message_chunk_index + message_chunks[
                            message_chunk_index], address)

        # for chunk in chunks:


class StreamReceiver:

    def __init__(self, udp_client_socekt: socket.socket, address, destination_address, split_size, buffer_size,
                 times_to_send):
        self.udp_client_socket = udp_client_socekt
        self.destination_address = destination_address
        self.split_size = split_size
        self.buffer_size = buffer_size - 8  # 8 = size of packed indexes
        self.times_to_send = times_to_send


def main():
    streamer = Streamer(5, 10, 2)
    img = cv2.imread(r'C:\Users\User\Desktop/france-in-pictures-beautiful-places-to-photograph-eiffel-tower.jpg', 0)
    streamer.send_image(img)


if __name__ == '__main__':
    main()
