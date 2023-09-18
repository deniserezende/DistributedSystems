import logging
from datetime import datetime

import numpy as np
from PIL import Image, ImageTk
import tkinter as tk

from PIL.Image import Transpose
import Pyro4

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Bin1Client(tk.Tk):
    def __init__(self):
        super().__init__()

        self.IMG_SIZE = 512
        self.pic = np.zeros((self.IMG_SIZE, self.IMG_SIZE), dtype=np.uint8)
        self.lut = [0] * 256

        try:
            with open("server_uri.txt", "r") as f:
                server_uri1 = f.readline().strip()
                server_uri2 = f.readline().strip()
            logging.info(f"server_uri1:[{server_uri1}]")
            logging.info(f"server_uri2:[{server_uri2}]\n")
            if server_uri1 == "" or server_uri2 == "":
                logging.error("You did not run the server code twice.")
                exit()
        except FileNotFoundError:
            logging.error("You did not run the server code.")
            exit()
        self.myServer1 = Pyro4.Proxy(server_uri1)
        self.myServer2 = Pyro4.Proxy(server_uri2)

        self.img = Image.new("RGB", (self.IMG_SIZE, self.IMG_SIZE))

        self.title("Binarization")
        self.geometry(f"{self.IMG_SIZE}x{self.IMG_SIZE + 25 + 40}")

        self.lut[0] = (0, 0, 0)
        self.lut[1] = (255, 255, 255)

        logging.info("Processing...")
        logging.info("Please wait.\n")

        im = self.get_image()
        pixels = np.array(im)

        if len(pixels.shape) == 3:  # Check if the image is RGB
            self.pic = np.array(pixels[:, :, 0], dtype=np.uint8)
        else:
            self.pic = pixels

        self.pic_list = self.pic.tolist()  # Convert numpy array to list
        self.pic_list1 = self.process_image_with_server(self.myServer1, self.pic_list)
        self.pic_list2 = self.process_image_with_server(self.myServer2, self.pic_list)

        self.pic_list_combined = (np.array(self.pic_list1) + np.array(self.pic_list2)) // 2

        self.paint()
        logging.info("Done.")
        logging.info("Close the opened window, your file has been saved.\n")

        self.save_processed_image()  # Save the processed image to a file

    def process_image_with_server(self, server, pic_list):
        return server.bin(pic_list, self.IMG_SIZE)

    def paint(self):
        for i in range(self.IMG_SIZE):
            for j in range(self.IMG_SIZE):
                self.img.putpixel((i, j), self.lut[self.pic_list_combined[i][j]])

        self.img = self.img.transpose(Transpose.ROTATE_270)
        self.img = self.img.transpose(Transpose.FLIP_LEFT_RIGHT)
        self.tk_img = ImageTk.PhotoImage(self.img)
        canvas = tk.Canvas(self, width=self.IMG_SIZE, height=self.IMG_SIZE)
        canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
        canvas.pack()

    def get_image(self):
        # file_path = filedialog.askopenfilename()
        # return Image.open(file_path)
        return Image.open("im1.JPG")

    def save_processed_image(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"processed_image_{timestamp}.png"
        self.img.save(filename)
        logging.info(f"Processed image saved as {filename}")


if __name__ == "__main__":
    app = Bin1Client()
    app.mainloop()
