from scapy.all import *
from scapy.layers.dhcp import *
from scapy.layers.inet import *
from scapy.layers.l2 import Ether

import socket
import netifaces

# This is to get the current computer running the server IP, don't think about it
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
server_mac = get_if_hwaddr(wifi_interface)

ip_pool = iter(["192.168.1.100", "192.168.1.101", "192.168.1.102"])
def dhcp_discovery_handler(packet):
    # Checks if the packet has a DHCP layer, otherwise ignore
    if packet.haslayer(DHCP):
        # If DHCP discover, do DHCP offer
        if packet[DHCP] and packet[DHCP].options[0][1] == 1:
            print(f"DHCP discovery packet received from {packet.src}")
            send_dhcp_offer(packet)
        # If DHCP request, do DHCP acknowledge
        elif packet[DHCP] and packet[DHCP].options[0][1] == 3:
            print(f"DHCP acknowledgement packet received {packet.src}")
            send_dhcp_acknowledge(packet)

# This function is to create a DHCP offer packet for the sender
def create_dhcp_offer(packet):
    client_mac = packet.src
    client_xid = packet[BOOTP].xid

    # Make ethernet nothing b/c we are not using it
    ethernet = Ether(dst='ff:ff:ff:ff:ff:ff',
                     src=server_mac,
                     type=0x800)
    # Source is the server IP, destination is a broadcast for the client to respond to
    ip = IP(src=server_ip,
            dst='255.255.255.255')
    # UDP ports
    udp = UDP(sport=67,
              dport=68)

    # Bootp options
    bootp = BOOTP(op=2,
                  yiaddr="192.168.1.100",
                  siaddr=server_ip,
                  giaddr='0.0.0.0',
                  chaddr=client_mac,
                  xid=client_xid)

    # DHCP options
    dhcp = DHCP(options=[("message-type", "offer"),
                         ("server_id", server_ip),
                         ("subnet_mask", "255.255.255.0"),
                         "end"])
    offer_packet = ethernet / ip / udp / bootp / dhcp

    return offer_packet

def send_dhcp_offer(packet):
    offer_packet = create_dhcp_offer(packet)
    sendp(offer_packet, iface=wifi_interface)
    print(f"Server sent DHCP offer to {packet.src}!\n")

def send_dhcp_acknowledge(packet):
    print("DHCP ACk packet detected\n")
    return 0

def start_dhcp_server():
    print("Starting DHCP Server")
    # Sniffer for DHCP request packets sent from the client side
    sniff(filter="arp or (udp and (port 67 or 68))", prn=dhcp_discovery_handler, store=0)

if __name__ == "__main__":
    if wifi_interface:
        start_dhcp_server()
    else:
        print("No wifi interface, server will not start!")
