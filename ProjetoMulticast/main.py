import socket
import struct
import sys
import time
import logging
import os
import datetime

# timeout poderia ajustar automatico
# ajustar para dois delta t - basicamente min = 1 s
# reajusta por cliente 
# reajuste para mais tempo caso seja maior
# timeout por cliente
# timeout do cliente sempre 0.5 OK

# menu 
# setar atraso artificial + 0.5 do cliente - para esse tempo depois responde que recebeu - simular um problema
# enviar mensagem

#acknowledge junto com o delta que demorou pra responder ok

# o heartbeat desliga ele da sua lista e religa, então tem que ficar mandando para eles ok



# Configurações do grupo multicast
MULTICAST_GROUP = '224.1.1.1'
MULTICAST_PORT = 5007
localhost = 'localhost'
TIMEOUT = 2

host_ports = {}

with open('multicast.txt', 'r') as file:
    for line in file:
        ip, port, host = line.strip().split()
        # (x,y, 1 é online e 0 é offline, timeout)
        host_ports[host] = (ip, int(port), 0, 2) 

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
file_content = []


def add_online_host(host):
    host_ports[host] = host_ports[host][:2] + (1,) + host_ports[host][3:] # Para mudar para 1 (online)

def remove_online_host(host):
    host_ports[host] = host_ports[host][:2] + (0,)  + host_ports[host][3:] # Para mudar para 0 (offline)

def change_timeout_host(host, new_timeout):
    host_ports[host] = host_ports[host][:3] + (new_timeout,)



global_amount = 0


def _send_message_(message, host, address):
    ip, port = address
    await_time = host_ports[host][-1]*2
    print(f"timeout={await_time/2}")
    try:
        start_time = time.time()
        print(f'Sending "{message}" to ({ip}, {port})')
        sock.sendto(message.encode(), (ip, port))
        sock.settimeout(await_time)
        response, address = sock.recvfrom(1024)
        decoded_response = response.decode()
        if decoded_response == 'acknowledge':
            end_time = time.time()
            print(f"Acknowledged {end_time-start_time}")
            change_timeout_host(host, end_time-start_time)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file_content.append(f'{timestamp} || Mensagem: "{message}" enviada para {ip}, {port}')
        else:
            # Manda a mensagem novamente caso não tiver sido recebida
            _send_message_(message, host, address)
    except socket.timeout:
        change_timeout_host(host, await_time * 2)
        # print(f"Timeout: A mensagem não foi recebida em {TIMEOUT} segundos.")
        # Manda a mensagem novamente caso tenha ocorrido timeout
        global global_amount
        global_amount += 1
        if global_amount < 2:
            _send_message_(message, host, address)
        global_amount = 0
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_content.append(f'{timestamp} || Mensagem: "{message}" não enviada para {ip}, {port}')
    except Exception as e:
        pass
        # logging.warning(f"Error: {e}")


# Função para enviar mensagens
def send_message(message):
    offline_hosts = []
    for host, address in host_ports.items():
        ip, port, status, timeout = address  
        if status == 1:
            _send_message_(message, host, address[:2])
        else:
            offline_hosts.append(host)
    for h in offline_hosts:
        print(f"Host: {h} seems to be offline.")

# Função para receber mensagens
def receive_message():
    elapsed_time = 1
    last_heartbeat = time.time()  # Defina last_heartbeat antes do loop
    key = None
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(current_address_info[:2]) 
        sock.settimeout(5) # Configura um timeout de 5 segundos para ser esse o limite do heartbeat
        while True:
            try:
                data, address = sock.recvfrom(1024)
                ip, port = address
                decoded_data = data.decode()
                # Separar a string usando '/'
                parts = decoded_data.split('/')
                # Obter a segunda parte (o host)
                message = parts[0]
                if message == 'heartbeat':
                    key = parts[1]
                    add_online_host(key)
                    last_heartbeat = time.time()
                else:
                    print(f'Received "{message}" from ({ip}, {port})')
                    sock.sendto("acknowledge".encode(), (ip, port))  # MULTICAST_PORT))
                    print(f"Digite uma mensagem: ")
            except Exception as e:
                elapsed_time = time.time() - last_heartbeat
                if elapsed_time > 5 and key != None:
                    remove_online_host(key)
                    key = None


# Função para enviar heartbeat
def send_message_heartbeat():
    while True:
        for host, address in host_ports.items():
            message = f"heartbeat/{host_name}"
            ip, port, status, timeout = address
            try:
                logging.info(f'Sending "heartbeat" to ({ip}, {port})')
                sock.sendto(message.encode(), (ip, port))
                sock.settimeout(TIMEOUT)
            except socket.timeout:
                logging.warning(f"{host}: ({ip}, {port}) seems to be offline.")
                remove_online_host(host)
            except Exception as e:
                remove_online_host(host)
                # desligar o host
                pass
                # logging.warning(f"Error: {e}")
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
