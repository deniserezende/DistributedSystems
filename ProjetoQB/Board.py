import time
import tkinter as tk
from tkinter import simpledialog, colorchooser
import threading
import json


class Board:
    def __init__(self, shared_sock, my_address, is_host, board_name, host_name, host_ports, board_owner,
                 get_online_hosts_function, stop_election_function):
        self.is_host = is_host
        self.board_name = board_name
        self.host_name = host_name
        self.host_ports = host_ports
        self.board_owner = board_owner
        self.my_address = my_address
        self.start_x = None
        self.start_y = None
        self.pencil_color = "black"

        self.root = tk.Tk()
        self.root.title(f"Board: {self.board_name} || Host: {self.board_owner} || You: {self.host_name}")

        self.canvas = None
        self.context_menu = None
        self.sock = shared_sock

        threading.Thread(target=self.receive_data).start()

        self.get_online_hosts_function = get_online_hosts_function
        self.stop_election_function = stop_election_function

        self.all_objects_data = None
        if self.board_owner != self.host_name:
            shared_sock.sendto("GET_ALL_OBJECTS".encode(), (self.host_ports[self.board_owner][0],
                                                        self.host_ports[self.board_owner][1]))

    def create_board(self):
        self.canvas = tk.Canvas(self.root, width=800, height=600, bg="white")
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)

        self.copy_owner_canva()

        self.canvas.bind("<Button-1>", self.start_rectangle)
        self.canvas.bind("<B1-Motion>", self.draw_rectangle_drag)
        self.canvas.bind("<ButtonRelease-1>", self.end_rectangle)
        self.canvas.bind("<Button-3>", self.show_context_menu)

        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Clear Screen", command=self.clear_screen)
        self.context_menu.add_command(label="Change Pencil Color", command=self.change_pencil_color)

        # Associar o menu de contexto à tecla "D"
        self.root.bind("d", self.show_context_menu)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def copy_owner_canva(self):
        if self.all_objects_data is not None:
            list_all_obj = eval(self.all_objects_data)
            for obj_str in list_all_obj:
                message_parts = obj_str.split(
                    ";")  # 'type:rectangle;      coords:[41.0, 92.0, 42.0, 420.0];     color:black'
                data = {}
                for part in message_parts:
                    key, value = part.split(":")
                    data[key] = value

                # Agora você pode acessar os dados
                list_coords = eval(data["coords"])
                # obj_coords = [float(coord) for coord in list_coords.split(",")]
                obj_color = data["color"]
                self.canvas.create_rectangle(list_coords[0], list_coords[1], list_coords[2], list_coords[3],
                                             outline=obj_color)

    def receive_data(self):
        while True:
            try:
                data, address = self.sock.recvfrom(1024)
                if not data:
                    break
                decoded_data = data.decode()
                if decoded_data.startswith("heartbeat"):
                    pass
                elif decoded_data.startswith("RECTANGLE"):
                    self.draw_rectangle(decoded_data[9:])
                    if self.host_name == self.board_owner:
                        self.broadcast(decoded_data, self.is_host)
                elif decoded_data.startswith("CLEAR_CANVAS"):
                    self.clear_canvas()
                    if self.host_name == self.board_owner:
                        self.broadcast(decoded_data, self.is_host)
                elif decoded_data.startswith("ELECTION_RESULT"):
                    self.stop_election_function()
                    parts = decoded_data.split('/')
                    self.board_owner = parts[1]
                    if self.host_name == self.board_owner:
                        self.is_host = True
                    self.root.title(f"Host: {self.board_owner} || You: {self.host_name}")
                elif decoded_data.startswith("GET_ALL_OBJECTS"):
                    all_objects_data = self.get_all_objects()
                    self.sock.sendto(f"COPY_CANVAS/{str(all_objects_data)}".encode(), address)
                elif decoded_data.startswith("COPY_CANVAS"):
                    parts = decoded_data.split('/')
                    self.all_objects_data = parts[1]
                    self.copy_owner_canva()
            except Exception as e:
                pass

    def send_message(self):
        message = simpledialog.askstring("Input", "Enter your message:")
        self.sock.send(message.encode())

    def on_closing(self):
        self.sock.close()
        self.root.destroy()

    def draw_rectangle(self, rect_data):
        values = rect_data.split(',')
        start_x, start_y, end_x, end_y = map(int, values[1:])

        self.canvas.create_rectangle(start_x, start_y, end_x, end_y, outline=values[0])

    def clear_canvas(self):
        self.canvas.delete("all")

    def start_rectangle(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def draw_rectangle_drag(self, event):
        if self.start_x is not None and self.start_y is not None:
            current_x, current_y = event.x, event.y
            self.canvas.delete("temp_rectangle")
            self.canvas.create_rectangle(self.start_x, self.start_y, current_x, current_y, outline=self.pencil_color,
                                         tags="temp_rectangle")

    def end_rectangle(self, event):
        if self.start_x is not None and self.start_y is not None:
            end_x, end_y = event.x, event.y
            self.canvas.create_rectangle(self.start_x, self.start_y, end_x, end_y, outline=self.pencil_color)
            message = f"RECTANGLE{self.pencil_color},{self.start_x},{self.start_y},{end_x},{end_y}"
            self.broadcast(message, self.is_host)
            self.send_to_owner(message, self.is_host)
            self.start_x, self.start_y = None, None
            self.canvas.delete("temp_rectangle")

    # se for cliente ele envia para o dono
    # se for host envia para todos

    def broadcast(self, message, is_host):  # Tem que ser host para usar essa função
        if not is_host:
            return

        print(f"Broadcasting")
        online_hosts = self.get_online_hosts_function()
        print(f"online_hosts={online_hosts}")
        online_hosts.remove(self.host_name)
        for host, address in self.host_ports.items():
            ip, port, status, _, _ = address
            if host in online_hosts:
                try:
                    self.sock.sendto(message.encode(), (ip, port))
                except Exception as e:
                    print(f"Exception={e}")
                    # Handle the exception as needed
                    pass

    def send_to_owner(self, message, is_host):
        if is_host:
            return
        print(f"Sending to board owner {self.board_owner}")
        address = self.host_ports[self.board_owner]
        ip, port, status, _, _ = address
        try:
            self.sock.sendto(message.encode(), (ip, port))
        except Exception as e:
            print(f"Exception={e}")
            # Handle the exception as needed
            pass

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def clear_screen(self):
        self.clear_canvas()
        self.broadcast("CLEAR_CANVAS", self.is_host)
        self.send_to_owner("CLEAR_CANVAS", self.is_host)

    def change_pencil_color(self):
        color_name, color_hex = colorchooser.askcolor(title="Select a color", parent=self.root)

        if color_hex:
            self.pencil_color = color_hex

    def is_within_rectangle(self, x, y):
        items = self.canvas.find_enclosed(x - 1, y - 1, x + 1, y + 1)
        return bool(items)

    def edit_rectangle_color(self, event):
        if self.is_within_rectangle(event.x, event.y):
            color_name, color_hex = colorchooser.askcolor(title="Select a color", parent=self.root)

            if color_hex:
                items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
                if items:
                    rect_item = items[0]
                    self.canvas.itemconfig(rect_item, outline=color_hex)

    def copy_canvas_state(self, all_objects):
        for obj_id in all_objects:
            obj_type = self.canvas.type(obj_id)
            if obj_type == "rectangle":
                coords = self.canvas.coords(obj_id)
                color = self.canvas.itemcget(obj_id, "outline")
                self.canvas.draw_rectangle_drag(coords[0], coords[1], coords[2], coords[3], color)

    def get_all_objects(self):
        all_objects = self.canvas.find_all()
        objects_data = []

        for obj_id in all_objects:
            obj_type = self.canvas.type(obj_id)
            if obj_type == "rectangle":
                coords = self.canvas.coords(obj_id)
                color = self.canvas.itemcget(obj_id, "outline")
                message = f"type:rectangle;coords:{coords};color:{color}"
                objects_data.append(message)
        return objects_data
