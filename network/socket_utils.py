import socket
import threading

from network.communication import TCPServer, UDPServer


def initialize_server(constants, server_name, THREADS, new_thread=True):
    server_info = constants[server_name]
    print(f"[Log] - Started server - {server_info}")
    if server_info["type"] == "tcp":
        server = TCPServer((server_info["ip"], int(server_info["port"])), server_info["recv_size"])
    elif server_info["type"] == "udp":
        server = UDPServer((server_info["ip"], int(server_info["port"])), server_info["recv_size"])
    else:
        raise ValueError(f"Invalid server_type: {server_name}")

    if new_thread:
        server_thread = threading.Thread(target=server.run, args=())
        THREADS.append(server_thread)
        server_thread.start()
    else:
        server.run()

    return server


