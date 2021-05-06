import threading
import struct
import itertools

import cv2
import numpy as np
import socket
import math

HEADERS_SIZE = 12 # Bytes

class StreamUtils:

    @staticmethod
    def split_frame_to_grid(frame, grid_size):
        height, width = frame.shape[:2]
        block_height, block_width = math.ceil(height / grid_size), math.ceil(width / grid_size)
        chunks = [[] for i in range(grid_size)]
        for y in range(0, grid_size):
            for x in range(0, grid_size):
                chunk = frame[y*block_height:y*block_height+block_height, x*block_width:x*block_width+block_width]                
                if chunk.shape[1] == 0:
                    break
                chunks[y].append(StreamUtils.compress_frame(chunk))
        return chunks

    @staticmethod
    def format_frame(grid, frame_data, grid_size):

        # chunks = [cv2.imdecode(np.frombuffer(b"".join(self.__sort_chunk_pieces(chunk)), np.uint8), 1).flatten() for chunk in chunks]
        height, width = frame_data.shape[:2]
        block_height, block_width = int(math.ceil(height / grid_size)), int(math.ceil(width / grid_size))
        for row_index in range(len(grid)):
            row = grid[row_index]
            for block_index in range(len(row)):
                block = row[block_index]
                sorted_block_chunks = StreamUtils.sort_chunk_pieces(block)
                block_data = np.frombuffer(b"".join(sorted_block_chunks), np.uint8)
                decoded_block_data = cv2.imdecode(block_data, 1)

                block_longitude = block_height * row_index
                block_latitude = block_width * block_index
                frame_data[block_longitude:block_longitude + block_height, block_latitude:block_latitude+block_width] = decoded_block_data
        return frame_data 


    @staticmethod
    def compress_frame(frame):
            _, encoded_frame = cv2.imencode('.JPEG', frame)
            return encoded_frame

    @staticmethod
    def decompress_frame(encoded_frame):
        decoded_frame = cv2.imdecode(encoded_frame, 1)
        return decoded_frame


    @staticmethod
    def get_blank_image(frame_size):
        return np.zeros(frame_size, np.uint8)


    @staticmethod
    def initialize_chunks(blank_image, buffer_size, grid_size):
        
        grid = StreamUtils.split_frame_to_grid(blank_image, grid_size)
        frame_dict = []
        for row in grid:
            new_row = []
            for block in row:
                block_chunks = [block[i:i + buffer_size, :] for i in range(0, block.shape[0], buffer_size)]    
                new_row.append({i: block_chunks[i] for i in range(len(block_chunks))})
            frame_dict.append(new_row)
        return frame_dict
        
    @staticmethod
    def sort_chunk_pieces(block):
        """
        Sort chunk pieces and filter out null ones.
        """
        items = list(block.items())
        items.sort(key=lambda piece: piece[0])
        values = list(map(lambda piece: piece[1], items))
        return list(filter(lambda value: value is not None, values))

    


class Streamer:

    def __init__(self, udp_socekt: socket.socket, destination_address, grid_size, buffer_size,
                 times_to_send):
        self.udp_socket = udp_socekt
        self.destination_address = destination_address
        self.grid_size = grid_size
        self.buffer_size = buffer_size - HEADERS_SIZE
        self.times_to_send = times_to_send
    

    def send_image(self, frame):
        grid = StreamUtils.split_frame_to_grid(frame, self.grid_size)
        for i in range(1):
            for row_index in range(len(grid)):
                packed_row_index = struct.pack('!i', row_index)
                row = grid[row_index]

                for compressed_chunk_index in range(len(row)):
                    packed_compressed_chunk_index = struct.pack('!i', compressed_chunk_index)
                    
                    compressed_chunk = grid[row_index][compressed_chunk_index] 
                    message_chunks = [compressed_chunk[i:i + self.buffer_size] for i in range(0, len(compressed_chunk), self.buffer_size)]    

                    for message_chunk_index in range(len(message_chunks)):
                        packed_message_chunk_index = struct.pack('!i', message_chunk_index)

                        for i in range(self.times_to_send):
                            self.udp_socket.sendto(packed_row_index + packed_compressed_chunk_index + packed_message_chunk_index + compressed_chunk.tobytes(), self.destination_address)
                
        
        # for row_index in range(len(grid[::-1])):
        #     packed_row_index = struct.pack('!i', row_index)
        #     row = grid[row_index][::-1]

        #     for compressed_chunk_index in range(len(row)):
        #         packed_compressed_chunk_index = struct.pack('!i', compressed_chunk_index)
                
        #         compressed_chunk = grid[row_index][compressed_chunk_index] 
        #         message_chunks = [compressed_chunk[i:i + self.buffer_size] for i in range(0, len(compressed_chunk), self.buffer_size)][::-1]

        #         for message_chunk_index in range(len(message_chunks)):
        #             packed_message_chunk_index = struct.pack('!i', message_chunk_index)

        #             for i in range(self.times_to_send):
        #                 self.udp_socket.sendto(packed_row_index + packed_compressed_chunk_index + packed_message_chunk_index + compressed_chunk.tobytes(), self.destination_address)


class StreamReceiver:

    def __init__(self, udp_socekt: socket.socket, frame_size, running, grid_size, buffer_size):
        self.udp_socket = udp_socekt
        self.running = running
        self.lock = threading.Lock()

        self.frame_size = frame_size
        self.grid_size = grid_size
        self.buffer_size = buffer_size

        self.frame_data = StreamUtils.get_blank_image(self.frame_size)
        self.grid = StreamUtils.initialize_chunks(StreamUtils.get_blank_image(self.frame_size), self.buffer_size, self.grid_size)

    
    def get_frame(self):

        # if any(None in block.values() for block in itertools.chain([*grid])):
        #     return self.frame_data

        self.lock.acquire()
        self.frame_data = StreamUtils.format_frame(self.grid, self.frame_data, self.grid_size)
        frame = self.frame_data
        self.lock.release()
        return frame

    def receive_stream(self):        
        """
        This method is designated to receive a video stream from client on a separate thread.
        """
        packed_row_index = b""
        packed_compressed_chunk_index = b""
        packed_message_chunk_index = b""
        unpacked_row_index = 0
        unpacked_compressed_chunk_index = 0
        unpacked_message_chunk_index = 0

        self.lock.acquire()
        frame = self.frame_data
        self.lock.release()

        while self.running:
            message = self.udp_socket.get_message()
            
            if not message:
                continue

            packed_row_index = message[:4]
            packed_compressed_chunk_index = message[4:8]
            packed_message_chunk_index = message[8:12]

            row_index = struct.unpack('!i', packed_row_index)[0]
            compressed_chunk_index = struct.unpack('!i', packed_compressed_chunk_index)[0]
            message_chunk_index = struct.unpack('!i', packed_message_chunk_index)[0]

            data = message[HEADERS_SIZE:]
            self.lock.acquire()
            self.grid[row_index][compressed_chunk_index][message_chunk_index] = data
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
