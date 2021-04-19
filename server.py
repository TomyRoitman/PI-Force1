import json
import threading

from network.server import TCPServer, UDPServer
# from car import Car

CONSTANTS_PATH = "constants.json"
THREADS = []


def handle_client(socket):
    pass


def initialize_server(constants, server_name, new_thread=True):
    global THREADS
    server_info = constants[f"{server_name}"]
    if server_info["type"] == "tcp":
        server = TCPServer((server_info["ip"], int(server_info["port"])))
    elif server_info["type"] == "udp":
        server = UDPServer((server_info["ip"], int(server_info["port"])))
    else:
        raise ValueError(f"Invalid server_type: {server_name}")
    server.set_handle_client_method(handle_client)

    if new_thread:
        server_thread = threading.Thread(target=server.run)
        THREADS.append(server_thread)
        server_thread.run()
    else:
        server.run()


def main():
    constants = json.load(open(CONSTANTS_PATH))

    # car = Car()
    initialize_server(constants, "main_tcp_server")
    initialize_server(constants, "main_udp_server", new_thread=False)


if __name__ == '__main__':
    main()
