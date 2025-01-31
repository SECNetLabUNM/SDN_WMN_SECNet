import socket as sck
import threading
import json
import random
import time

server_ADDR = "192.168.1.26"
server_PORT = 9559

def gen_random_number():
    return random.randint(0, 999)

def send_info():
    return 0

def client_handler():
    device_id = gen_random_number()
    device_info = {
        "ID": device_id,
        "MAC": "00:A0:C9:14:C8:29",
        "IP": "192.168.1.1",
        "nMAC": ["00:A0:C9:14:C8:30", "00:A0:C9:14:C8:31", "00:A0:C9:14:C8:32"],
        "nIP": [1234, 23455, 12323],
        "LQ": "255"
    }

    device_xyz = {
        "ID": device_id,
        "x": gen_random_number(),
        "y": gen_random_number(),
        "z": gen_random_number()
    }
    client_socket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
    client_socket.connect((server_ADDR, server_PORT))

    while True:
        json_data = json.dumps(device_id)
        client_socket.sendall(json_data.encode('utf-8'))
        # Every 5 seconds we will send to the server
        time.sleep(5)

client_handler()
