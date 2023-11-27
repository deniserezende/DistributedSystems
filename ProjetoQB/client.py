import socket
import threading
import tkinter as tk
from tkinter import colorchooser
# Falta só adicionar para conseguir editar a cor de um retangulo

class ClientGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cliente")

        self.canvas = tk.Canvas(root, bg="white", width=400, height=400)
        self.canvas.pack(expand=True, fill='both')

        self.entry = tk.Entry(root)
        self.entry.pack(side=tk.BOTTOM, fill=tk.X)
        self.entry.bind("<Return>", self.send_message)

        # Configurar o cliente
        self.host = '127.0.0.1'
        self.port = 12345

        # Criar um objeto de socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Conectar ao servidor
        self.client_socket.connect((self.host, self.port))

        # Iniciar uma nova thread para receber dados do servidor em segundo plano
        threading.Thread(target=self.receive_data).start()

        # Iniciar a interface gráfica
        root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Variáveis para rastrear os pontos iniciais e finais do retângulo
        self.start_x = None
        self.start_y = None
        self.pencil_color = "black"

        self.selected_rectangle = None

        # Adicionar menu de contexto
        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(label="Clear Screen", command=self.clear_screen)
        self.context_menu.add_command(label="Change Pencil Color", command=self.change_pencil_color)

        # Associar o menu de contexto à tecla "D"
        root.bind("d", self.show_context_menu)

        self.canvas.bind("<Button-3>", self.edit_rectangle_color)


    def receive_data(self):
        while True:
            # Receber dados do servidor
            data = self.client_socket.recv(1024)
            if not data:
                break  # Se não houver mais dados, sair do loop

            # Decodificar os dados e chamar a função para desenhar
            decoded_data = data.decode()
            if decoded_data.startswith("RECTANGLE"):
                # Se a mensagem começa com "RECTANGLE", desenhe o retângulo
                self.draw_rectangle(decoded_data[9:])
            elif decoded_data.startswith("CLEAR_CANVAS"):
                # Se a mensagem começa com "CLEAR_CANVAS", limpe o canvas
                self.clear_canvas()

    def draw_rectangle(self, rect_data):
        # A função para desenhar o retângulo com base nos dados recebidos
        # Os dados devem ser da forma "start_x,start_y,end_x,end_y"
        values = rect_data.split(',')
        start_x, start_y, end_x, end_y = map(int, values[1:])

        # Desenhar o retângulo no canvas
        self.canvas.create_rectangle(start_x, start_y, end_x, end_y, outline=values[0])

    def clear_canvas(self):
        # Limpar o canvas
        self.canvas.delete("all")

    def send_message(self, event):
        # Enviar mensagem para o servidor
        message = self.entry.get()
        self.client_socket.send(message.encode())
        self.entry.delete(0, tk.END)  # Limpar a entrada

    def on_closing(self):
        # Função chamada quando a janela é fechada
        # Fechar a conexão com o servidor e sair do programa
        self.client_socket.close()
        self.root.destroy()

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
            self.client_socket.send(message.encode())
            # Limpar os pontos iniciais para o próximo retângulo
            self.start_x, self.start_y = None, None
            # Limpar o retângulo temporário
            self.canvas.delete("temp_rectangle")

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def clear_screen(self):
        # Limpar o canvas
        self.clear_canvas()
        # Enviar mensagem para o servidor indicando para limpar o canvas
        self.client_socket.send("CLEAR_CANVAS".encode())

    def change_pencil_color(self):
        # Exibir a caixa de diálogo de seleção de cor
        color_name, color_hex = colorchooser.askcolor(title="Select a color", parent=self.root)

        # Se o usuário escolheu uma cor, configurar a cor da caneta
        if color_hex:
            self.pencil_color = color_hex

    def is_within_rectangle(self, x, y):
        print("CLICOU")
        # Verificar se as coordenadas (x, y) estão dentro de algum retângulo existente
        items = self.canvas.find_enclosed(x - 1, y - 1, x + 1, y + 1)  # Adiciona uma margem de 1 pixel
        return bool(items)


    def edit_rectangle_color(self, event):
        print(f"in edit_rectangle_color")
        # Verificar se o clique do botão direito foi feito dentro de um retângulo
        if self.is_within_rectangle(event.x, event.y):
            # Exibir a caixa de diálogo de seleção de cor
            color_name, color_hex = colorchooser.askcolor(title="Select a color", parent=self.root)

            # Se o usuário escolheu uma cor, obter os itens do retângulo e atualizar a cor
            if color_hex:
                items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
                if items:
                    rect_item = items[0]
                    self.canvas.itemconfig(rect_item, outline=color_hex)

if __name__ == "__main__":
    root = tk.Tk()
    client_gui = ClientGUI(root)

    # Bind dos eventos do mouse para desenhar retângulos
    client_gui.canvas.bind("<Button-1>", client_gui.start_rectangle)
    client_gui.canvas.bind("<B1-Motion>", client_gui.draw_rectangle_drag)
    client_gui.canvas.bind("<ButtonRelease-1>", client_gui.end_rectangle)

    # Adicionar o evento de clique direito para editar a cor do retângulo
    # client_gui.canvas.bind("<Button-3>", client_gui.edit_rectangle_color)

    root.mainloop()
