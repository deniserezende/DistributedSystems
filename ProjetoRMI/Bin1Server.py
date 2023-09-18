import logging
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import Pyro4
import os
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@Pyro4.expose
class Bin1Server:
    def __init__(self):
        self.shutdown_flag = False  # Flag to indicate if the server should shut down

    def shutdown(self):
        logging.info("Shutting down the server...")
        self.shutdown_flag = True

    def bin(self, pic_list, IMG_SIZE):
        # Raise an exception if shutdown is requested
        if self.shutdown_flag:
            raise Pyro4.errors.CommunicationError("Server is shutting down")
        pic = np.array(pic_list).reshape((IMG_SIZE, IMG_SIZE))  # Convert back to numpy array
        rpic = np.zeros_like(pic)

        desvio = 0.0
        tot = 0
        media = 0
        sum2 = 0
        dif = 0
        K = 2.0
        sob = 20
        Ydim, Xdim = pic.shape

        mask_d = 2 * sob + 1
        pixeis_mask = mask_d * mask_d

        def process_pixel(i, j):
            nonlocal desvio
            nonlocal tot
            nonlocal media
            nonlocal sum2
            nonlocal dif

            tot = np.sum(pic[i - sob:i + sob + 1, j - sob:j + sob + 1])
            media = tot // pixeis_mask

            sum2 = np.sum(np.abs(pic[i - sob:i + sob + 1, j - sob:j + sob + 1] - media))
            desvio = sum2 / pixeis_mask

            if pic[i, j] >= media - K * desvio:
                return 0
            else:
                return 1

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_pixel, i, j) for i in range(sob, Ydim - sob) for j in range(sob, Xdim - sob)]

            index = 0
            for i in range(sob, Ydim - sob):
                for j in range(sob, Xdim - sob):
                    rpic[i, j] = futures[index].result()
                    index += 1

        logging.info(f"Média={media}")
        logging.info(f"Desvio={desvio}\n")

        return rpic.tolist()


def main():
    server = Bin1Server()
    daemon = Pyro4.Daemon()
    uri = daemon.register(server)

    print("Server URI:", uri)

    with open("server_uri.txt", "a") as f:
        f.write(str(uri) + '\n')

    print("Press Ctrl + C to exit.")

    try:
        daemon.requestLoop()
    except KeyboardInterrupt:
        server.shutdown()  # Call the shutdown method when a keyboard interrupt (Ctrl+C) is detected
        daemon.shutdown()
    finally:
        try:
            os.remove("server_uri.txt")
        except FileNotFoundError:
            logging.info("File was already been deleted.")
        print("\nServer has exited.")


if __name__ == "__main__":
    main()
