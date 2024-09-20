import socket

def find_server():
    udp_port = 5555
    server_ip = None
    broadcast_msg = "server discovery request"

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client_socket.sendto(broadcast_msg.encode(), ('<broadcast>', udp_port))

    try:
        # time out limit for 5 seconds
        print("Attempting search")
        client_socket.settimeout(5)
        data, addr = client_socket.recvfrom(1024)
        if data:
            print("Received from the server")
            server_ip = data.decode()
    except socket.timeout:
        print("search timed out")
    finally:
        client_socket.close()

    return server_ip

def TCPClient(s_ip):
    TCP_Port = 1000
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.bind((s_ip, TCP_Port))
    client_socket.connect(s_ip)

def run_everything():
    #SERVER_IP = find_server()
    SERVER_IP = "192.168.1.113"
    TCPClient(SERVER_IP)

