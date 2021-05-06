import threading
import struct

import cv2
import numpy as np
import socket
import math

import image_slicer
class Streamer:

    def __init__(self, udp_socekt: socket.socket, destination_address, split_size, buffer_size,
                 times_to_send):
        self.udp_socket = udp_socekt
        self.destination_address = destination_address
        self.split_size = split_size
        self.buffer_size = buffer_size - 8  # 8 = size of packed indexes
        self.times_to_send = times_to_send

    def __compress_frame(self, frame):
        _, encoded_frame = cv2.imencode('.JPEG', frame)
        return encoded_frame

    def send_image(self, frame):
        compressed_frame_chunks = [self.__compress_frame(chunk).flatten().tobytes() for chunk in
                                   np.split(frame.flatten(), self.split_size)]

        print(len(compressed_frame_chunks), len(compressed_frame_chunks[0]))

        for compressed_chunk_index in range(len(compressed_frame_chunks)):
            packed_compressed_chunk_index = struct.pack('!i', compressed_chunk_index)
            message_chunks = [compressed_frame_chunks[compressed_chunk_index][i:i + self.buffer_size] for i in
                              range(0, len(compressed_frame_chunks[compressed_chunk_index]), self.buffer_size)]
            for message_chunk_index in range(len(message_chunks)):
                for i in range(self.times_to_send):
                    packed_message_chunk_index = struct.pack('!i', message_chunk_index)
                    
                    self.udp_socket.sendto(
                        packed_compressed_chunk_index +
                        packed_message_chunk_index +
                        message_chunks[message_chunk_index],
                        self.destination_address)

        # for chunk in chunks:


class StreamReceiver:

    def __init__(self, udp_socekt: socket.socket, frame_size, running, split_size, buffer_size):
        self.udp_socket = udp_socekt
        self.frame_size = frame_size
        self.running = running
        self.split_size = split_size
        self.buffer_size = buffer_size
        self.frame_data = self.__get_blank_image(self.frame_size)
        self.lock = threading.Lock()
        self.chunks = self.__initialize_chunks(self.__get_blank_image(self.frame_size))
        print(len(self.chunks), len(self.chunks[0]))

    def __initialize_chunks(self, blank_image):
        chunks = [cv2.imencode(".JPEG", chunk)[1].flatten().tobytes() for chunk in np.split(blank_image, self.split_size)]
        compressed_chunks_in_dictionaries = []
        for compressed_chunk in chunks:
            dictionary = {}
            for index in range(math.ceil(len(compressed_chunk) / self.buffer_size)):
                dictionary[index] = compressed_chunk[index * self.buffer_size : index * self.buffer_size + self.buffer_size]
            compressed_chunks_in_dictionaries.append(dictionary)
        return compressed_chunks_in_dictionaries

        return [{i: i for i in cv2.imencode(".JPEG", chunk)[1].flatten().tobytes()} for chunk in np.split(blank_image, self.split_size)]

    def __decompress_frame(self, encoded_frame):
        _, decoded_frame = cv2.imdecode(encoded_frame, 1)
        return decoded_frame

    def __get_blank_image(self, frame_size):
        return np.zeros(frame_size, np.uint8)

    def __sort_chunk_pieces(self, chunk_pieces):
        items = list(chunk_pieces.items())
        # print(items)
        items.sort(key=lambda piece: piece[0])
        # print("Sort result: ", list(map(lambda piece: piece[1], items)))
        return list(filter(lambda piece: piece != None, map(lambda piece: piece[1], items)))

    def __format_frame(self, chunks, frame_data):
        if any(None in chunk.values() for chunk in chunks):
            return self.frame_data
        chunks = [cv2.imdecode(np.frombuffer(b"".join(self.__sort_chunk_pieces(chunk)), np.uint8), 1).flatten() for chunk in chunks]
        jump_size = frame_data.flatten().shape[0] // self.split_size
        for i in range(frame_data.shape[0] // jump_size):
            frame_data[i * jump_size:i * jump_size + jump_size] = chunks[i]
        return frame_data 

    def get_frame(self):
        if any(None in chunk.values() for chunk in self.chunks):
            return self.frame_data
        self.lock.acquire()
        self.frame_data = self.__format_frame(self.chunks, self.frame_data)
        frame = self.frame_data
        self.lock.release()
        return frame

    def receive_stream(self):        
        """
        This method is designated to receive a video stream from client on a separate thread.
        """
        packed_compressed_chunk_index = b""
        packed_message_chunk_index = b""
        unpacked_compressed_chunk_index = 0
        unpacked_message_chunk_index = 0

        self.lock.acquire()
        frame = self.frame_data.flatten()
        self.lock.release()

        while self.running:
            message = self.udp_socket.get_message()
            
            if not message:
                continue

            # print(f"Message: {message}")
            packed_compressed_chunk_index = message[:4]
            packed_message_chunk_index = message[4:8]

            unpacked_compressed_chunk_index = struct.unpack('!i', packed_compressed_chunk_index)[0]
            unpacked_message_chunk_index = struct.unpack('!i', packed_message_chunk_index)[0]

            # print(f"{unpacked_compressed_chunk_index} / {unpacked_message_chunk_index}")
            data = message[8:]
            self.lock.acquire()
            self.chunks[unpacked_compressed_chunk_index][unpacked_message_chunk_index] = data
            
            self.lock.release()


def main():
    # streamer = Streamer(5, 10, 2)
    img = cv2.imread(r'D:\CFO\CFO\resources\bg.png', 1)
    encoded = cv2.imencode(".JPEG", img)[1]
    encoded_bytes = encoded.tobytes()
    nparray = np.frombuffer(encoded_bytes, dtype="uint8")
    decoded = cv2.imdecode(nparray, 1)
    decoded = np.reshape(decoded, (1024, 1920, 3))
    print(decoded.shape)
    print(img.shape)
    # print(f"{img}\n\n\n\n------------------------\n\n\n\n")
    # print(decoded)
    print(np.array_equal(img, decoded))
    # np.reshape(decoded, (1024, 1920))
    
    original = img
    duplicate = decoded
    # 1) Check if 2 images are equals
    if original.shape == duplicate.shape:
        print("The images have same size and channels")
        difference = cv2.subtract(original, duplicate)
        b, g, r = cv2.split(difference)
        if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 and cv2.countNonZero(r) == 0:
            print("The images are completely Equal")


def __compress_frame(frame):
        _, encoded_frame = cv2.imencode('.JPEG', frame)
        return encoded_frame


def chunkify(img, block_width=4, block_height=4):
    shape = img.shape
    x_len = shape[0]//block_width
    y_len = shape[1]//block_height

    chunks = []
    x_indices = [i for i in range(0, shape[0]+1, block_width)]
    y_indices = [i for i in range(0, shape[1]+1, block_height)]

    shapes = list(zip(x_indices, y_indices))
    print(shapes)
    for i in range(len(shapes)):
        try:
            start_x = shapes[i][0]
            start_y = shapes[i][1]
            end_x = shapes[i+1][0]
            end_y = shapes[i+1][1]
            chunks.append(shapes[start_x:end_x][start_y:end_y] )
        except IndexError:
            print('End of Array')

    print(chunks)

    return chunks

        

def main3():
    pic_path = "D:\pic\pic.jpg"
    frame = cv2.imread(pic_path)
    frame = cv2.resize(frame, (480, 640))
    cv2.imshow("original", frame)
    print("Shape: ", frame.shape)
    
    chunkify(frame, math.ceil(frame.shape[0] / 5), math.ceil(frame.shape[1] / 5))

    # compressed_frame_chunks = [__compress_frame(chunk).tobytes() for chunk in
    #                                chunkify(frame, math.ceil(frame.shape[0] / 5), math.ceil(frame.shape[1] / 5))]

    decompressed = np.concatenate([cv2.imdecode(np.frombuffer(chunk, np.uint8), 1) for chunk in compressed_frame_chunks])
    cv2.imwrite("decompressed.jpg", decompressed)

if __name__ == '__main__':
    main3()
