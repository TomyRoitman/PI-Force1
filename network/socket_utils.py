import socket
import threading

from network.communication import TCPServer, UDPServer


def initialize_server(constants, server_name, THREADS, new_thread=True):
    """
    Initialize and start a server
    :param constants: json containing constants
    :param server_name: which server of the constants to start
    :param THREADS: global variable of a list of threads to add the server thread to
    :param new_thread: bool, whether to open a new thread for server
    :return: server object
    """
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


