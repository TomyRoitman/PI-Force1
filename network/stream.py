from os.path import join
import threading
import struct
import itertools

import cv2
import numpy as np
import socket
import math

HEADERS_SIZE = 12  # Bytes


class StreamUtils:

    @staticmethod
    def split_frame_to_grid(frame, block_rows, block_cols):
        print("Split params: ", block_rows, block_cols)
        # height, width = frame.shape[:2]
        # block_height, block_width = math.ceil(height / grid_size), math.ceil(width / grid_size)
        # chunks = [[] for i in range(grid_size)]
        # for y in range(0, grid_size):
        #     for x in range(0, grid_size):
        #         chunk = frame[y*block_height:y*block_height+block_height, x*block_width:x*block_width+block_width]                
        #         if chunk.shape[1] == 0:
        #             break
        #         chunks[y].append(StreamUtils.compress_frame(chunk))
        # return chunks
        h, w = frame.shape[:2]
        # assert h % block_rows == 0, "{} rows is not evenly divisble by {}".format(h, block_rows)
        # assert w % block_cols == 0, "{} cols is not evenly divisble by {}".format(w, block_cols)
        # return (frame.reshape(h // block_rows, block_rows, -1, block_cols)
        #         .swapaxes(1, 2)
        #         .reshape(-1, block_rows, block_cols, 3))
        return frame.reshape(block_rows * block_cols, h // block_rows, w // block_cols, 3)
    @staticmethod
    def format_frame(grid, frame_data, grid_rows, grid_columns, block_height, block_width):
        # chunks = [cv2.imdecode(np.frombuffer(b"".join(self.__sort_chunk_pieces(chunk)), np.uint8), 1).flatten() for chunk in chunks]
        # height, width = frame_data.shape[:2]
        # block_height, block_width = int(math.ceil(height / grid_size)), int(math.ceil(width / grid_size))
        # for row_index in range(len(grid)):
        #     row = grid[row_index]
        #     for block_index in range(len(row)):
        #         block = row[block_index]
        #         sorted_block_chunks = StreamUtils.sort_chunk_pieces(block)
        #         block_data = np.frombuffer(b"".join(sorted_block_chunks), np.uint8)
        #         decoded_block_data = cv2.imdecode(block_data, 1)

        #         block_longitude = block_height * row_index
        #         block_latitude = block_width * block_index
        #         frame_data[block_longitude:block_longitude + block_height, block_latitude:block_latitude+block_width] = decoded_block_data
        # print(grid.shape)
        # print([np.frombuffer(b"".join(block) if len(block) > 1 else block[0], dtype=np.uint8) for block in grid.values()])
        # joined_blocks = [cv2.imdecode(np.frombuffer(b"".join(block) if len(block) > 1 else block[0], dtype=np.uint8), 1) for block in grid.values()]
        # print("------------- format_frame -------------\n")
        # joined_blocks = [cv2.imdecode(np.frombuffer(b"".join(block), dtype=np.uint8), 1).reshape(block_height, block_width, 3) for block in grid.values()]
        values = StreamUtils.sort_grid_pieces(grid)
        joined_blocks = [cv2.imdecode(np.frombuffer(b"".join(block), dtype=np.uint8), 1) for block in values]
        if joined_blocks[0] is None:
            return frame_data
        try:
            formatted_blocks = np.array(joined_blocks, dtype=np.uint8)
            # formatted_blocks = formatted_blocks.reshape(grid_rows, grid_columns,
            #                                             math.ceil(frame_data.shape[0] / float(grid_rows)),
            #                                             math.ceil(frame_data.shape[1] / float(grid_columns)), 3)
            # # print(frame_data.shape)
            frame = formatted_blocks.reshape(frame_data.shape)
        except:
            # print("\n----------------------------------------\n")
            return frame_data
        # print("\n----------------------------------------\n")
        return frame

    @staticmethod
    def compress_frame(frame):
        ret, encoded_frame = cv2.imencode('.JPEG', frame)
        return encoded_frame if ret else None

    @staticmethod
    def decompress_frame(encoded_frame):
        decoded_frame = cv2.imdecode(encoded_frame, 1)
        return decoded_frame

    @staticmethod
    def get_blank_image(frame_size):
        return np.zeros(frame_size, np.uint8)

    @staticmethod
    def initialize_chunks(blank_image, buffer_size, grid_rows, grid_columns):
        grid = StreamUtils.split_frame_to_grid(blank_image, grid_rows, grid_columns)
        print("Initial grid: ", grid.shape)

        # _, encoded = cv2.imencode(".JPEG", grid[0])
        # print(encoded.shape)
        #
        # block_length = len(encoded.tobytes())
        return {i: StreamUtils.create_block(grid[i], buffer_size, b"\xFF") for i in range(len(grid))}

    @staticmethod
    def create_block(block, buffer_size, content=b"\x00"):
        ret, encoded = cv2.imencode(".JPEG", block)
        encoded_bytes = encoded.tobytes()
        return [encoded_bytes[i:i + buffer_size] for i in range(0, len(encoded_bytes), buffer_size)] if ret else None

    @staticmethod
    def sort_grid_pieces(grid):
        """
        Sort chunk pieces and filter out null ones.
        """
        items = list(grid.items())
        items.sort(key=lambda piece: piece[0])
        values = list(map(lambda piece: piece[1], items))
        return list(filter(lambda value: value is not None, values))


class Streamer:

    def __init__(self, udp_socekt: socket.socket, destination_address, grid_rows, grid_columns, buffer_size,
                 times_to_send):
        self.udp_socket = udp_socekt
        self.destination_address = destination_address
        self.grid_rows = grid_rows
        self.grid_columns = grid_columns
        self.buffer_size = buffer_size - HEADERS_SIZE
        self.times_to_send = times_to_send

    def send_image(self, frame):
        if frame is None:
            return frame
        # grid = StreamUtils.split_frame_to_grid(frame, math.ceil(frame.shape[0] / float(self.grid_rows)),
        #                                        math.ceil(frame.shape[1] / float(self.grid_columns)))
        grid = StreamUtils.split_frame_to_grid(frame, self.grid_rows,
                                               self.grid_columns)

        # for i in range(1):
        #     for row_index in range(len(grid)):
        #         packed_row_index = struct.pack('!i', row_index)
        #         row = grid[row_index]

        #         for compressed_chunk_index in range(len(row)):
        #             packed_compressed_chunk_index = struct.pack('!i', compressed_chunk_index)

        #             compressed_chunk = grid[row_index][compressed_chunk_index] 
        #             message_chunks = [compressed_chunk[i:i + self.buffer_size] for i in range(0, len(compressed_chunk), self.buffer_size)]    

        #             for message_chunk_index in range(len(message_chunks)):
        #                 packed_message_chunk_index = struct.pack('!i', message_chunk_index)

        #                 for i in range(self.times_to_send):
        #                     self.udp_socket.sendto(packed_row_index + packed_compressed_chunk_index + packed_message_chunk_index + compressed_chunk.tobytes(), self.destination_address)
        print("Shape: ", grid.shape)
        for block_index in range(grid.shape[0]):
            packed_block_index = struct.pack('!i', block_index)
            block = grid[block_index]

            compressed_block = StreamUtils.compress_frame(block)
            block_bytes = compressed_block.tobytes()

            message_chunks = [block_bytes[i: i + self.buffer_size] for i in
                              range(0, len(block_bytes), self.buffer_size)]
            packed_size = struct.pack('!i', len(message_chunks))

            for chunk_index in range(len(message_chunks)):
                packed_chunk_index = struct.pack('!i', chunk_index)

                self.udp_socket.sendto(
                    packed_block_index + packed_size + packed_chunk_index + message_chunks[chunk_index],
                    self.destination_address)


class StreamReceiver:

    def __init__(self, udp_socekt: socket.socket, frame_size, running, grid_rows, grid_columns, buffer_size):
        self.udp_socket = udp_socekt
        self.running = running
        self.lock = threading.Lock()

        self.frame_size = frame_size
        self.grid_rows = grid_rows
        self.grid_columns = grid_columns
        self.buffer_size = buffer_size
        self.block_height = math.ceil(frame_size[0] / float(grid_rows))
        self.block_width = math.ceil(frame_size[1] / float(grid_columns))
        self.frame_data = StreamUtils.get_blank_image(self.frame_size)
        self.grid = StreamUtils.initialize_chunks(self.frame_data, self.buffer_size, self.grid_rows, grid_columns)
        # print("\n\n\n--------------------------------\nGrid: " + str(len(self.grid)) + "\n", self.grid, "\n--------------------------------\n\n\n")

    def get_frame(self):

        # if any(None in block.values() for block in itertools.chain([*grid])):
        #     return self.frame_data

        self.lock.acquire()
        self.frame_data = StreamUtils.format_frame(self.grid, self.frame_data, self.grid_rows, self.grid_columns,
                                                   self.block_height, self.block_width)
        frame = self.frame_data
        self.lock.release()
        return frame

    def receive_stream(self):
        """
        This method is designated to receive a video stream from client on a separate thread.
        """

        block_index = 0
        size = 0
        index = 0

        while self.running:
            message = self.udp_socket.get_message()

            if not message:
                continue

            block_index, received_size, index, data = self.__parse_message(message)
            # block_index = received_block_index
            size = received_size
            self.lock.acquire()
            # self.grid[block_index] = [b"\x00" * self.buffer_size for i in range(size)]
            if size != len(self.grid[block_index]):
                self.grid[block_index] = self.__make_list_of_size(self.grid[block_index], size)
            self.grid[block_index][index] = data
            self.lock.release()

            # while index < size:
            #     message = self.udp_socket.get_message()
            #
            #     if not message:
            #         continue
            #
            #     received_block_index, received_size, index, data = self.__parse_message(message)
            #     if received_block_index != block_index:
            #         break
            #
            #     self.lock.acquire()
            #     self.grid[block_index][index] = data
            #     self.lock.release()

    def __make_list_of_size(self, source, size):
        if size > len(source):
            return source + [source[0],] * (size - len(source))
        elif size < len(source):
            return source[:size]
        else:
            return source

    def __parse_message(self, message):

        packed_block_index = message[:4]
        packed_size = message[4:8]
        packed_chunk_index = message[8:12]

        block_index = struct.unpack('!i', packed_block_index)[0]
        compressed_chunk_index = struct.unpack('!i', packed_size)[0]
        message_chunk_index = struct.unpack('!i', packed_chunk_index)[0]

        data = message[HEADERS_SIZE:]

        return block_index, compressed_chunk_index, message_chunk_index, data


if __name__ == '__main__':
    pass
