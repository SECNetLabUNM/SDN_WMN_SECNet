from scapy.all import *
from scapy.layers.dhcp import *
from scapy.layers.inet import *
from scapy.layers.l2 import Ether
import socket
import netifaces

# This is to get the current computer running the server IP, dont think about it
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

def get_wifi_interface():
    for interface in netifaces.interfaces():
        try:
            if os.path.exists(f'/sys/class/net/{interface}/wireless'):
                return interface
        except Exception as e:
            print(f"Error checking interface {interface}: {e}")
            print("Fail to start DHCP client")

server_ip = get_local_ip()
wifi_interface = get_wifi_interface()

ip_pool = iter(["192.168.1.100", "192.168.1.101", "192.168.1.102"])
def dhcp_discovery_handler(packet):
    # If DHCP discover, do DHCP offer
    if packet[DHCP] and packet[DHCP].options[0][1] == 1:
        print("DHCP discovery packet received")
        send_dhcp_offer(packet)
    # If DHCP request, do DHCP acknowledge
    if packet[DHCP] and packet[DHCP].options[0][1] == 3:
        print("DHCP acknowledgement packet received")
        send_dhcp_acknowledge(packet)

def send_dhcp_offer(packet):
    offer_packet = 0
    client_mac = packet.src
    print("\nDHCP Discover packet detected")
    '''
    ethernet = Ether(dst=,src=client_mac)
    sendp(
        Ether(src=server_mac, dst="ff:ff:ff:ff:ff:ff") /
        IP(src=server_ip, dst="255.255.255.255") /
        UDP(sport=67, dport=68) /
        BOOTP(
            op=2,
            yiaddr=client_ip,
            siaddr=server_ip,
            giaddr=gateway,
            chaddr=client_mac,
            xid=pkt[BOOTP].xid
        )
    DHCP(options=[('messagetype', 'offer')]) /
    DHCP(options=[('subnet_mask', subnet_mask)]) /
    DHCP(options=[('server_id', server_ip), ('end')])
    )
    print"DHCP Offer packet sent\n."
    ###
    '''
    return 0

def send_dhcp_acknowledge(packet):
    return 0

def start_dhcp_server():
    print("Starting DHCP Server")
    # Sniffer for DHCP request packets sent from the client side
    sniff(filter="arp or (udp and (port 67 or 68))", prn=dhcp_discovery_handler, store=0)

if __name__ == "__main__":
    print(server_ip)
    print(wifi_interface)
    #start_dhcp_server()