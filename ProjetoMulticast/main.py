import socket
import struct
import sys
import time
import logging
import os
import datetime

# Configurações do grupo multicast
MULTICAST_GROUP = '224.1.1.1'
MULTICAST_PORT = 5007
localhost = 'localhost'
TIMEOUT = 2

host_ports = {}

with open('multicast.txt', 'r') as file:
    for line in file:
        ip, port, host = line.strip().split()
        host_ports[host] = (ip, int(port))

print(host_ports)


def get_current_address_info(host_ports, host_name):
    # Obtém a porta do host atual
    current_address_info = host_ports.get(host_name)
    # Verifica se o nome do host é válido
    if not current_address_info:
        logging.error(f"O host '{host_name}' não possui uma porta associada.")
        sys.exit()
    return current_address_info


# Obtém o nome do host a partir dos argumentos de linha de comando
host_name = sys.argv[1]

# Obtém a porta do host atual
current_address_info = get_current_address_info(host_ports, host_name)
# Remove o host
del host_ports[host_name]


def config_socket():
    # Criação do socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Configuração para permitir o multicast
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))

    # Junta-se ao grupo multicast
    # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.bind(('', 0))
    mreq = struct.pack('4sl', socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    return sock


sock = config_socket()
online_hosts = []
offline_hosts = []
file_content = []


def add_online_host(host):
    if host not in online_hosts:
        online_hosts.append(host)
        if host in offline_hosts:
            offline_hosts.remove(host)


def remove_online_host(host):
    if host not in offline_hosts:
        offline_hosts.append(host)
        if host in online_hosts:
            online_hosts.remove(host)


global_amount = 0


def _send_message_(message, host, address):
    ip, port = address
    try:
        print(f'Sending "{message}" to ({ip}, {port})')
        sock.sendto(message.encode(), (ip, port))
        sock.settimeout(TIMEOUT)
        response, address = sock.recvfrom(1024)
        decoded_response = response.decode()
        if decoded_response == 'acknowledge':
            print("Acknowledged")
            add_online_host(port)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file_content.append(f'{timestamp} || Mensagem: "{message}" enviada para {ip}, {port}')
        else:
            # Manda a mensagem novamente caso não tiver sido recebida
            _send_message_(message, host, address)
    except socket.timeout:
        print(f"Timeout: A mensagem não foi recebida em {TIMEOUT} segundos.")
        # Manda a mensagem novamente caso tenha ocorrido timeout
        global global_amount
        global_amount += 1
        if global_amount < 3:
            _send_message_(message, host, address)
        global_amount = 0
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_content.append(f'{timestamp} || Mensagem: "{message}" não enviada para {ip}, {port}')
    except Exception as e:
        logging.warning(f"Error: {e}")


# Função para enviar mensagens
def send_message(message):
    for host, address in host_ports.items():
        _send_message_(message, host, address)


# Função para receber mensagens
def receive_message():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(current_address_info)
        while True:
            data, address = sock.recvfrom(1024)
            ip, port = address
            decoded_data = data.decode()
            if decoded_data == 'heartbeat':
                add_online_host(port)
            else:
                print(f'Received "{decoded_data}" from ({ip}, {port})')
                sock.sendto("acknowledge".encode(), (ip, port))  # MULTICAST_PORT))
                add_online_host(port)
                print(f"Digite uma mensagem: ")


# Função para enviar heartbeat
def send_message_heartbeat():
    message = "heartbeat"
    while True:
        for host, address in host_ports.items():
            ip, port = address
            try:
                logging.info(f'Sending "heartbeat" to ({ip}, {port})')
                sock.sendto("heartbeat".encode(), (ip, port))
                sock.settimeout(TIMEOUT)
            except socket.timeout:
                logging.warning(f"({ip}, {port}) seems to be offline.")
                remove_online_host(port)
            except Exception as e:
                logging.warning(f"Error: {e}")
        time.sleep(2)  # Espera 20 segundos antes de enviar o próximo heartbeat


# Exemplo de uso
if __name__ == '__main__':
    import threading

    # Inicia a thread para receber mensagens
    recebendo_thread = threading.Thread(target=receive_message)
    recebendo_thread.start()

    # Thread para heartbeat
    heartbeat_thread = threading.Thread(target=send_message_heartbeat)
    heartbeat_thread.start()

    # Envia mensagens
    while True:
        message = input("Digite uma mensagem: \n")
        if message.lower() == 'exit':
            file_name = 'output-' + host_name + '.txt'
            with open(file_name, 'a') as file:
                for fc in file_content:
                    file.write(fc + '\n')
            os._exit(0)  # Exit with status 0 (success)
        else:
            send_message(message)
