import threading
import socket
import time
import logging
from Election import Election


class HeartBeat:
    def __init__(self, shared_sock, host_ports, my_host_name, my_address, elected_name):
        self.sock = shared_sock
        # Dicionário assin host_ports[host] = (ip, int(port), bool(online/offline), DELETE, time.time())
        self.host_ports = host_ports
        self.host_name = my_host_name  # O nome do próprio host
        self.timeout_heartbeat = 5
        self.my_address = my_address
        self.elected_name = elected_name
        self.election_instance = Election(self.host_name, self.host_ports, self.broadcast, self.send_message)
        self.heartbeat_port = None

    def start_threads(self):
        # Inicia a thread para receber mensagens
        heartbeat_receiving_thread = threading.Thread(target=self.receive_message_heartbeat)
        heartbeat_receiving_thread.start()

        # Thread para heartbeat
        heartbeat_sending_thread = threading.Thread(target=self.send_message_heartbeat)
        heartbeat_sending_thread.start()

    def add_online_host(self, host, last_heartbeat):
        self.host_ports[host] = self.host_ports[host][:2] + (1,) + (self.host_ports[host][3],) + (
            last_heartbeat,)  # Para mudar para 1 (online)

    def remove_online_host(self, host):
        self.host_ports[host] = self.host_ports[host][:2] + (0,) + self.host_ports[host][3:]
        # Para mudar para 0 (offline)

    def check_hosts(self):
        for host, address in self.host_ports.items():
            if self.host_ports[host][2] == 1 and time.time() - self.host_ports[host][-1] > 3:
                self.remove_online_host(host)
                self.check_elected()

    def send_message(self, message, ip, port):
        try:
            self.sock.sendto(message.encode(), (ip, port + 1000))

            # Defina um tempo limite para aguardar a resposta
            timeout = time.time() + 5  # 5 segundos

            while time.time() < timeout:
                self.sock.settimeout(self.timeout_heartbeat)
                try:
                    response, address = self.sock.recvfrom(1024)
                    decoded_response = response.decode()
                    if decoded_response.startswith('ACCEPT'):
                        return 'ACCEPTED'
                except socket.timeout:
                    pass  # Ignorar o timeout na recepção, continuar esperando
                except TimeoutError:
                    pass
            # Se o tempo limite for atingido e não houver resposta, considerar como recusa
            print("Timeout esperando por resposta.")
        except Exception as e:
            print(f"Exception={e}")
            # Trate a exceção conforme necessário

        return 'REFUSED'

    def get_online_hosts(self):
        online_hosts = [host for host, details in self.host_ports.items() if details[2] == 1]
        online_hosts.append(self.host_name)
        online_hosts.sort()
        return online_hosts

    def check_elected(self):
        if self.host_name == self.elected_name:
            return
        info = self.host_ports[self.elected_name]
        _, _, online, _, _ = info
        if online == 0:
            # Call for election
            online_hosts = self.get_online_hosts()
            print("Online Hosts:", online_hosts)
            self.election_instance.start_election(online_hosts)

    def broadcast(self, message):
        print(f"Broadcasting in HB")
        online_hosts = self.get_online_hosts()
        if message.startswith("ELECTION_RESULT"):
            parts = message.split('/')
            self.elected_name = parts[1]
            self.election_instance.abort_election()
        for host in online_hosts:
            if host == self.host_name:
                # print(f"Letting myself know")
                try:
                    self.sock.sendto(message.encode(), self.my_address)
                except Exception as e:
                    pass
            else:
                address = self.host_ports[host]
                ip, port, status, _, _ = address
                if status == 1:
                    try:
                        self.sock.sendto(message.encode(), (ip, port))
                    except Exception as e:
                        print(f"Exception={e}")
                        # Handle the exception as needed
                        pass

    def send_message_heartbeat(self):
        while True:
            for host, address in self.host_ports.items():
                message = f"heartbeat/{self.host_name}"
                ip, port, status, timeout, last_heartbeat = address
                new_port = port + 1000
                try:
                    logging.info(f'Sending "heartbeat" to ({ip}, {new_port})')
                    self.sock.sendto(message.encode(), (ip, new_port))
                except socket.timeout:
                    logging.warning(f"{host}: ({ip}, {new_port}) seems to be offline.")
                    self.remove_online_host(host)
                    # self.check_elected()
                except Exception as e:
                    self.remove_online_host(host)
                    # self.check_elected()
                time.sleep(1)

    def stop_election(self):
        self.election_instance.abort_election()

    def receive_message_heartbeat(self):
        last_heartbeat = time.time()  # Defina last_heartbeat antes do loop
        key = None

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            ip, port = self.my_address
            sock.bind((ip, port+1000))
            sock.settimeout(self.timeout_heartbeat)

            while True:
                try:
                    data, address = sock.recvfrom(1024)
                    decoded_data = data.decode()
                    if decoded_data.startswith("heartbeat"):
                        # Separar a string usando '/'
                        parts = decoded_data.split('/')
                        # Obter a segunda parte (o host)
                        key = parts[1]
                        last_heartbeat = time.time()
                        self.add_online_host(key, last_heartbeat)
                        self.check_hosts()
                        # self.check_elected()
                    elif decoded_data == 'ELECTION_REQUEST':
                        self.election_instance.abort_election()
                        ip, port = address
                        sock.sendto(f"ACCEPT".encode(), (ip, port+1000))  # AQUIDE
                except socket.timeout:
                        self.check_hosts()
                except Exception:
                    elapsed_time = time.time() - last_heartbeat
                    if elapsed_time > self.timeout_heartbeat:
                        self.check_elected()
                except TimeoutError:
                    # self.check_hosts()
                    pass
