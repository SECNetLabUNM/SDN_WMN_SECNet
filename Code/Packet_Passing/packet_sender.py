import socket as sck
import json
import time
#from pushFlows import PushFlow

FORMAT = 'utf-8'
HEADER = 128
DISCONNECT_MSG = "!!!DISCONNECT!!!"
PORT = 5500
# ADJUST THE SERVER IP
SERVER_IP = "192.168.1.113"
CLIENT_IP = "192.168.1.113"
ADDR = (SERVER_IP, PORT)

# Connect to the server
client_socket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
client_socket.bind((CLIENT_IP, 0))
client_socket.connect(ADDR)

def send_json_handler(msg):
    # Encode into bytes sized object
    json_msg = json.dumps(msg)
    message = json_msg.encode(FORMAT)
    # Gets the message length
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    # This adds blank padding of sie HEADER - message length to make sure we are
    # always sending something of length HEADER
    send_length += b' ' * (HEADER - len(send_length))
    client_socket.send(send_length)
    client_socket.send(message)
    # Response message for received
    print(client_socket.recv(HEADER).decode(FORMAT))

def send_interval(sec):
    while True:
        #test_switch = PushFlow()
        #sendMe = test_switch.GetBridgeAll(0)
        #orgIP = '100.100.100.10'

        #sendMe = [{**entry, 'origin': orgIP} for entry in sendMe]
        sendMe = [{1: 'Hello', 2: 'World'}]
        send_json_handler(sendMe)
        time.sleep(sec)

send_interval(2)