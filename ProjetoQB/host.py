import socket
import threading
import tkinter as tk
from tkinter import colorchooser


class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Servidor")

        self.canvas = tk.Canvas(root, bg="white", width=400, height=400)
        self.canvas.pack(expand=True, fill='both')

        # Configurar o servidor
        self.host = '127.0.0.1'
        self.port = 12345

        # Criar um objeto de socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Configurar o socket para reutilizar a porta, permitindo reiniciar o servidor rapidamente
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Vincular o socket ao endereço e porta
        self.server_socket.bind((self.host, self.port))

        # Começar a ouvir por conexões
        self.server_socket.listen(5)

        self.clients = set()

        self.text_area = tk.Text(root, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill='both')

        self.text_area.insert(tk.END, f"[*] Escutando em {self.host}:{self.port}\n")

        # Aceitar conexões em uma nova thread
        threading.Thread(target=self.accept_connections).start()

        # Configurar eventos de desenho no canvas do servidor
        self.canvas.bind("<Button-1>", self.start_rectangle)
        self.canvas.bind("<B1-Motion>", self.draw_rectangle_drag)
        self.canvas.bind("<ButtonRelease-1>", self.end_rectangle)

        # Inicializar as variáveis de desenho
        self.start_x = None
        self.start_y = None
        self.pencil_color = 'black'

        self.selected_rectangle = None

        # Adicionar menu de contexto
        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(label="Clear Screen", command=self.clear_screen)
        self.context_menu.add_command(label="Change Pencil Color", command=self.change_pencil_color)

        # Associar o menu de contexto ao evento de clique direito
        self.canvas.bind("<Button-3>", self.show_context_menu)

        # Associar o menu de contexto à tecla "D"
        root.bind("d", self.show_context_menu)

    def accept_connections(self):
        while True:
            # Aceitar a conexão do cliente
            client_socket, addr = self.server_socket.accept()
            self.text_area.insert(tk.END, f"[*] Conexão aceita de {addr[0]}:{addr[1]}\n")

            # Adicionar o cliente à lista de clientes
            self.clients.add(client_socket)

            # Iniciar uma nova thread para lidar com a conexão do cliente
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        while True:
            # Receber dados do cliente
            data = client_socket.recv(1024)
            if not data:
                break  # Se não houver mais dados, sair do loop

            # Decodificar os dados e enviar para todos os clientes, incluindo o remetente

            decoded_data = data.decode()
            # Criar uma cópia do conjunto de clientes para evitar RuntimeError
            clients_copy = self.clients.copy()
            # Enviar uma mensagem para todos os clientes
            for client in clients_copy:
                try:
                    client.send(decoded_data.encode())
                except:
                    # Remover clientes que não podem ser alcançados
                    self.clients.remove(client)


            # Se a mensagem começa com "RECTANGLE", desenhar no quadro do servidor
            if decoded_data.startswith("RECTANGLE"):
                self.draw_on_server(decoded_data[9:])
            elif decoded_data.startswith("CLEAR_CANVAS"):
                # Se a mensagem começa com "CLEAR_CANVAS", limpe o canvas
                self.clear_canvas()

        # Fechar a conexão com o cliente quando o loop terminar
        client_socket.close()

    def draw_on_server(self, rect_data):
        # A função para desenhar no quadro do servidor com base nos dados recebidos
        # Os dados devem ser da forma "x1,y1,x2,y2"
        values = rect_data.split(',')
        coords = list(map(int, values[1:]))

        # Desenhar no canvas do servidor
        self.canvas.create_rectangle(coords[0], coords[1], coords[2], coords[3], outline=values[0])

        # Enviar os dados de desenho para todos os clientes
        message = f"RECTANGLE{rect_data}"
        for client in self.clients:
            try:
                client.send(message.encode())
            except:
                # Remover clientes que não podem ser alcançados
                self.clients.remove(client)

    def start_rectangle(self, event):
        # Função chamada quando o usuário clica no canvas para iniciar um retângulo
        self.start_x = event.x
        self.start_y = event.y

    def draw_rectangle_drag(self, event):
        # Função chamada enquanto o usuário arrasta o mouse para ajustar o tamanho do retângulo
        if self.start_x is not None and self.start_y is not None:
            current_x, current_y = event.x, event.y
            # Atualizar o retângulo temporário para mostrar o tamanho ajustado
            self.canvas.delete("temp_rectangle")
            self.canvas.create_rectangle(self.start_x, self.start_y, current_x, current_y, outline=self.pencil_color,
                                         tags="temp_rectangle")

    def end_rectangle(self, event):
        # Função chamada quando o usuário solta o botão do mouse para desenhar o retângulo final
        if self.start_x is not None and self.start_y is not None:
            end_x, end_y = event.x, event.y
            # Desenhar o retângulo final no canvas
            self.canvas.create_rectangle(self.start_x, self.start_y, end_x, end_y, outline=self.pencil_color)
            # Enviar os pontos iniciais e finais do retângulo para o servidor
            message = f"RECTANGLE{self.pencil_color},{self.start_x},{self.start_y},{end_x},{end_y}"
            self.broadcast(message)
            # Limpar os pontos iniciais para o próximo retângulo
            self.start_x, self.start_y = None, None
            # Limpar o retângulo temporário
            self.canvas.delete("temp_rectangle")

    def broadcast(self, message):
        # Criar uma cópia do conjunto de clientes para evitar RuntimeError
        clients_copy = self.clients.copy()

        # Enviar uma mensagem para todos os clientes
        for client in clients_copy:
            try:
                client.send(message.encode())
            except:
                # Remover clientes que não podem ser alcançados
                self.clients.remove(client)

    def clear_canvas(self):
        # Limpar o canvas
        self.canvas.delete("all")

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def clear_screen(self):
        # Limpar o canvas
        self.clear_canvas()
        # Enviar mensagem para o servidor indicando para limpar o canvas
        self.broadcast("CLEAR_CANVAS")

    def change_pencil_color(self):
        # Exibir a caixa de diálogo de seleção de cor
        color_name, color_hex = colorchooser.askcolor(title="Select a color", parent=self.root)

        # Se o usuário escolheu uma cor, configurar a cor da caneta
        if color_hex:
            self.pencil_color = color_hex

if __name__ == "__main__":
    root = tk.Tk()
    server_gui = ServerGUI(root)
    root.mainloop()
