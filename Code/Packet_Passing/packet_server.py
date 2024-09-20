import socket as sck
import threading

FORMAT = 'utf-8'
HEADER = 128
DISCONNECT_MSG = "!!!DISCONNECT!!!"
PORT = 67
# ADJUST THE SERVER IP
SERVER_IP = "192.168.1.113"
ADDR = ('', PORT)

# Creates the server socket
server_socket = sck.socket(sck.AF_INET, sck.SOCK_STREAM)
# Binds the socket to the ip and port #
server_socket.bind(ADDR)

# Individual connection handler
def client_handler(connected_obj, address):
    print(f"[New Connection] {address} connected!")
    connected = True
    while connected:
        # Padding the packet to make sure that it fits?
        msg_length = connected_obj.recv(HEADER).decode(FORMAT)

        # If the message is NOT empty, then do the decoding
        if msg_length:
            msg_length = int(msg_length)
            msg = connected_obj.recv(msg_length).decode(FORMAT)

            # Disconnect handler
            if msg == DISCONNECT_MSG:
                connected = False

            print(f"[{address}] {msg}")
            # Sending back to client
            connected_obj.send("Message received".encode(FORMAT))

    connected_obj.close()

def server_side_handler():
    server_socket.listen()
    print(f"[Listening] Server is listening on {SERVER_IP}")
    while True:
        # This line is waiting for a new connection to the server
        # (object, IP and port)
        connected_obj, address = server_socket.accept()
        # Thread for the client handler
        thread = threading.Thread(target=client_handler,
                                  args=(connected_obj, address))
        thread.start()
        # Prints out active client threads
        print(f"[Active Connection] {threading.activeCount() - 1}")

print("[Starting] server socket is starting!")
server_side_handler()


