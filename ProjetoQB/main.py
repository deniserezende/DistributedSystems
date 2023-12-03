
import socket
import struct
import sys
import time
import logging

# TODO
# ReadMe
# Como executa

# TODO editar um retângulo

from Board import Board
from Heartbeat import HeartBeat

MULTICAST_GROUP = '224.1.1.1'
MULTICAST_PORT = 5007
localhost = 'localhost'
TIMEOUT_HEARTBEAT = 2
DELAY = 0


def get_current_address_info(_host_ports, _host_name):
    current_address_info = _host_ports.get(_host_name)
    if not current_address_info:
        logging.error(f"O host '{_host_name}' não possui uma porta associada.")
        sys.exit()
    return current_address_info


def config_socket(my_address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))
    if my_address is not None:
        sock.bind(my_address)
    else:
        sock.bind(('', 0))
    mreq = struct.pack('4sl', socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    return sock


host_ports = {}

with open('hosts.txt', 'r') as file:
    for index, line in enumerate(file):
        ip, port, host = line.strip().split()
        host_ports[host] = (ip, int(port), 0, index, time.time())

print(host_ports)

host_name = sys.argv[1]
my_address_info = get_current_address_info(host_ports, host_name)
del host_ports[host_name]

shared_sock = config_socket(my_address_info[:2])


def create_or_connect_board(_host_name, _host_ports):
    print("MENU:")
    print("(1): Create a board")
    print("(2): Connect to an existing board")
    menu = int(input("Select an option: "))

    if menu == 1:
        board_name = input("Enter the name of the board: ")
        board_owner = _host_name
        is_host = True
        all_objects_from_main_board = []  # A lista de objetos do canvas principal
    elif menu == 2:
        print(f"Make sure that the board you select is online.")
        for idx, (board_name, _) in enumerate(_host_ports.items(), start=1):
            print(f"({idx}): {board_name}")
        choice = int(input("Select a board to connect: "))
        board_name = list(_host_ports.keys())[choice - 1]
        board_owner = board_name
        is_host = False
    else:
        print("Invalid option. Exiting.")
        sys.exit()

    heartbeat_instance = HeartBeat(shared_sock, host_ports, host_name, my_address_info[:2], board_owner)
    heartbeat_instance.start_threads()
    board = Board(shared_sock, my_address_info[:2], is_host, board_name, _host_name, _host_ports, board_owner,
                  heartbeat_instance.get_online_hosts, heartbeat_instance.stop_election)
    board.create_board()


if __name__ == '__main__':
    # while True:
    create_or_connect_board(host_name, host_ports)
