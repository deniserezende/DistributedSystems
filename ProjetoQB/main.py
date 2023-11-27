import socket
import threading
import json

class Quadro:
    def __init__(self):
        self.quadrados = []
        self.lock = threading.Lock()

    def inserir_quadrado(self, quadrado):
        with self.lock:
            self.quadrados.append(quadrado)

    def editar_quadrado(self, indice, novas_coordenadas):
        with self.lock:
            if 0 <= indice < len(self.quadrados):
                self.quadrados[indice]['coordenadas'] = novas_coordenadas

    def obter_estado_quadro(self):
        with self.lock:
            return self.quadrados.copy()

class ServidorQuadro:
    def __init__(self, host, porta):
        self.host = host
        self.porta = porta
        self.quadro = Quadro()
        self.servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor_socket.bind((host, porta))
        self.servidor_socket.listen()

    def aceitar_conexoes(self):
        while True:
            cliente_socket, endereco_cliente = self.servidor_socket.accept()
            threading.Thread(target=self.lidar_com_cliente, args=(cliente_socket,)).start()

    def lidar_com_cliente(self, cliente_socket):
        with cliente_socket:
            while True:
                mensagem = cliente_socket.recv(1024)
                if not mensagem:
                    break

                mensagem_decodificada = json.loads(mensagem.decode('utf-8'))
                comando = mensagem_decodificada.get('comando')

                if comando == 'obter_estado':
                    estado_quadro = self.quadro.obter_estado_quadro()
                    cliente_socket.send(json.dumps({'estado_quadro': estado_quadro}).encode('utf-8'))

                elif comando == 'inserir_quadrado':
                    quadrado = mensagem_decodificada.get('quadrado')
                    self.quadro.inserir_quadrado(quadrado)

                elif comando == 'editar_quadrado':
                    indice = mensagem_decodificada.get('indice')
                    novas_coordenadas = mensagem_decodificada.get('novas_coordenadas')
                    self.quadro.editar_quadrado(indice, novas_coordenadas)

if __name__ == "__main__":
    host = 'localhost'
    porta = 12345

    servidor_quadro = ServidorQuadro(host, porta)

    # Iniciar thread para aceitar conexões de clientes
    threading.Thread(target=servidor_quadro.aceitar_conexoes).start()

    # O restante do código aqui seria responsável por iniciar eleições,
    # lidar com falhas e atualizar os clientes sobre o novo endereço do serviço.


#######

# import socket
# import threading
#
#
# def receive_data(client_socket):
#     while True:
#         # Receber dados do servidor
#         data = client_socket.recv(1024)
#         if not data:
#             break  # Se não houver mais dados, sair do loop
#
#         print(f"Recebido do servidor: {data.decode()}")
#
#
# def main():
#     # Configurar o cliente
#     host = '127.0.0.1'
#     port = 12345
#
#     # Criar um objeto de socket
#     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
#     # Conectar ao servidor
#     client_socket.connect((host, port))
#
#     # Iniciar uma nova thread para receber dados do servidor em segundo plano
#     receive_thread = threading.Thread(target=receive_data, args=(client_socket,))
#     receive_thread.start()
#
#     try:
#         while True:
#             # Enviar dados ao servidor
#             message = input("Digite uma mensagem para o servidor (ou 'exit' para sair): ")
#             client_socket.send(message.encode())
#
#             if message.lower() == 'exit':
#                 break
#
#     except KeyboardInterrupt:
#         pass  # Tratar interrupção do teclado (Ctrl+C)
#
#     finally:
#         # Fechar a conexão com o servidor
#         client_socket.close()
#
#
# if __name__ == "__main__":
#     main()


##### HOST

# import socket
# import threading
#
#
# def handle_client(client_socket):
#     # Este é o código que lidará com as conexões individuais dos clientes
#     # Aqui você pode adicionar lógica personalizada para processar as mensagens dos clientes
#
#     # Exemplo: Enviar uma mensagem de boas-vindas
#     client_socket.send("Bem-vindo ao servidor!".encode())
#
#     while True:
#         # Receber dados do cliente
#         data = client_socket.recv(1024)
#         if not data:
#             break  # Se não houver mais dados, sair do loop
#
#         # Exemplo: Enviar de volta os dados recebidos
#         client_socket.send(data)
#
#     # Fechar a conexão com o cliente quando o loop terminar
#     client_socket.close()
#
#
# def main():
#     # Configurar o servidor
#     host = '127.0.0.1'
#     port = 12345
#
#     # Criar um objeto de socket
#     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
#     # Configurar o socket para reutilizar a porta, permitindo reiniciar o servidor rapidamente
#     server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#
#     # Vincular o socket ao endereço e porta
#     server_socket.bind((host, port))
#
#     # Começar a ouvir por conexões
#     server_socket.listen(5)
#
#     print(f"[*] Escutando em {host}:{port}")
#
#     while True:
#         # Aceitar a conexão do cliente
#         client_socket, addr = server_socket.accept()
#         print(f"[*] Conexão aceita de {addr[0]}:{addr[1]}")
#
#         # Iniciar uma nova thread para lidar com a conexão do cliente
#         client_handler = threading.Thread(target=handle_client, args=(client_socket,))
#         client_handler.start()
#
#
# if __name__ == "__main__":
#     main()