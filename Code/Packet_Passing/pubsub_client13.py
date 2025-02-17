import socket as sck
import threading
import json
import random
import time
from multiprocessing.connection import Client


def get_local_ip():
    try:
        # Create a temporary socket to an external address (e.g., Google's public DNS server)
        # This doesn't establish a connection, so the target address can be almost anything
        s = sck.socket(sck.AF_INET, sck.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google DNS server IP and port
        local_ip = s.getsockname()[0]  # Get the socket's own address
        s.close()
    except Exception as e:
        print(f"Error: {e}")
        local_ip = "Unable to determine local IP"
    return local_ip

server_ADDR = get_local_ip()
server_PORT = 9559

class ClientHandler:
    def __init__(self, addr, port):
        self._ADDR = addr
        self._Port = port
        self.device_id = self.gen_random_number()
        # This is the main dictionary packet
        self.device_info = {
            "ID": self.device_id,
            "MAC": "00:A0:C9:14:C8:29",
            "IP": f"192.168.1.{self.gen_random_255()}",
            "Neighbor_Tuple": [False],
            "XYZ_Tuple": [False]
        }

    def gen_random_number(self):
        return random.randint(0, 999)

    def gen_random_255(self):
        return random.randint(1, 255)

    def make_device(self, subbed_info, subbed_XYZ):
        if subbed_info:
            device_neighbors = {
                "nMAC": ["00:A0:C9:14:C8:30", "00:A0:C9:14:C8:31", "00:A0:C9:14:C8:32"],
                "nIP": ["192.168.1.19", "192.168.1.20", "192.168.1.12"],
                "LQ": [self.gen_random_255(), self.gen_random_255(), self.gen_random_255()]
            }
            self.device_info["Neighbor_Tuple"] = [True, device_neighbors]
        else:
            self.device_info["Neighbor_Tuple"] = [False]

        if subbed_XYZ:
            device_xyz = {
                "x": self.gen_random_number(),
                "y": self.gen_random_number(),
                "z": self.gen_random_number()
            }
            self.device_info["XYZ_Tuple"] = [True, device_xyz]
        else:
            self.device_info["XYZ_Tuple"] = [False]

    def reply_server(self, client_socket):
        try:
            while True:
                data = client_socket.recv(1024)
                if data:
                    conditions = json.loads(data.decode('utf-8'))
                    print(f"Received! {conditions}")
                    condition_neighbors = conditions["Req_Neigh"]
                    condition_XYZ = conditions["Req_XYZ"]
                    self.make_device(condition_neighbors, condition_XYZ)
        except Exception as e:
            print(f"Error in the reply service{e}")
            client_socket.close()

    def connection(self):
        first_connection = True
        client_socket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
        while True:
            try:
                client_socket.connect((self._ADDR, self._Port))
                reply_server_thread = threading.Thread(target=self.reply_server,
                                                       args=(client_socket,))
                #reply_server_thread.start()
                while True:
                    if first_connection:
                        first_connection = False
                    else:
                        data = client_socket.recv(1024)
                        if data:
                            conditions = json.loads(data.decode('utf-8'))
                            print(f"From server! {conditions}")
                            condition_neighbors = conditions["Req_Neigh"]
                            condition_XYZ = conditions["Req_XYZ"]
                            self.make_device(condition_neighbors, condition_XYZ)

                    # TODO: Optimize this to make it only send the TUPLES. The other datas should be static
                    # TODO: do not troll and try to actually do this
                    print(f"To server: {self.device_info}")
                    json_data = json.dumps(self.device_info)
                    client_socket.sendall(json_data.encode('utf-8'))

                    time.sleep(3)

            except sck.error:
                print(f"Error: {sck.error}")
                print(f"Retrying to connect to server: {self._ADDR}")
                client_socket.close()
                time.sleep(3)

if __name__ == "__main__":
    client = ClientHandler(server_ADDR, server_PORT)
    client.connection()
