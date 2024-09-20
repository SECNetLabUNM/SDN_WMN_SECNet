import socket
import time
import threading

def get_local_ip():
    try:
        # Create a temporary socket to an external address (e.g., Google's public DNS server)
        # This doesn't establish a connection, so the target address can be almost anything
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google DNS server IP and port
        local_ip = s.getsockname()[0]  # Get the socket's own address
        s.close()
    except Exception as e:
        print(f"Error: {e}")
        local_ip = "Unable to determine local IP"
    return local_ip

SERVER_IP = get_local_ip()

def UDPGiverHandler(udp_socket, addr):
    print("Received message from:", addr)
    udp_socket.sendto(SERVER_IP.encode(), addr)

def UDPGiveSourceIP():
    t_end = time.time() + 5
    udp_port = 5555
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_socket.bind(('', udp_port))


    print("Server listening for broadcasts on port", udp_port)

    thread = None
    while time.time() < t_end:
        data, addr = udp_socket.recvfrom(1024)
        thread = threading.Thread(target=UDPGiverHandler,
                                  args=(udp_socket, addr))
        thread.start()
        print(f"[Active Connection] {threading.activeCount() - 1}")

    print("Done giving all server IP")
    if thread:
        thread.join()
    udp_socket.close()

def TCPHandler(socket_obj, addr):
    pass
def TCPServer():
    TCP_PORT = 1000
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind((SERVER_IP, TCP_PORT))
    tcp_socket.listen()
    print(f"[Listening] on {SERVER_IP}, port:{TCP_PORT}")
    while True:
        obj, addr = tcp_socket.accept()
        thread = threading.Thread(target=TCPHandler, args=(obj, addr))

        thread.start()
        print(f"[Active Connection] {addr}")

if __name__ == "__main__":
    #UDPGiveSourceIP()
    TCPServer()
