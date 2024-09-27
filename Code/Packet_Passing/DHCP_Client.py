import netifaces
import os
import threading
from threading import Event
import time

from scapy.all import *
from scapy.layers.dhcp import *
from scapy.layers.inet import *

from Code.Packet_Passing.DHCP_Server import server_ip

stop_event = Event()

def get_wifi_interface():
    for interface in netifaces.interfaces():
        try:
            if os.path.exists(f'/sys/class/net/{interface}/wireless'):
                return interface
        except Exception as e:
            print(f"Error checking interface {interface}: {e}")
            print("Fail to start DHCP client")

# Clients WiFi interafce
wifi_interface = get_wifi_interface()
# Clients MAC
client_mac_address = get_if_hwaddr(wifi_interface)
# Clients id for DHCP
x_id = 0x01234567

# DHCP packet
def create_dhcp_discover_packet():
    print("Making DHCP discovery packet")

    # Make ethernet unavailable b/c we are using WiFi
    ethernet = Ether(dst='ff:ff:ff:ff:ff:ff',
                     src=client_mac_address,
                     type=0x800)
    # Source and destination IP, source is assumed to be 0 empty at first
    ip = IP(src='0.0.0.0',
            dst='255.255.255.255')
    # UDP ports
    udp = UDP(sport=68,
              dport=67)
    # xid is the transaction ID and should be the same on all the networks
    bootp = BOOTP(chaddr=client_mac_address,
                  ciaddr='0.0.0.0',
                  xid=x_id, flags=1)
    dhcp = DHCP(options=[("message-type", "discover"),
                         "end"])

    discovery_packet = ethernet / ip / udp / bootp / dhcp

    return discovery_packet

# Send DHCP discovery packets
def send_dhcp_discover():
    print("sending DHCP discovery packet")
    discovery_packet = create_dhcp_discover_packet()
    delay = 3
    while not stop_event.is_set():
        sendp(discovery_packet, iface=wifi_interface)
        print(f"Packet sent, wait for {delay} seconds before next send...")
        time.sleep(delay)

def create_dhcp_request(offer_packet):
    print("Making DHCP request packet")
    # This is the IP offered by the server
    offered_ip = offer_packet[BOOTP].yiaddr
    # This is the IP of the server or the server IP itself because the IP = ID
    server_id = [opt[1] for opt in offer_packet[DHCP].options if opt[0] == 'server_id'][0]
    # Make ethernet unavailable b/c we are using WiFi
    ethernet = Ether(dst='ff:ff:ff:ff:ff:ff',
                     src=client_mac_address,
                     type=0x800)
    # Source and destination IP, source is assumed to be 0 empty at first
    ip = IP(src='0.0.0.0',
            dst='255.255.255.255')
    # UDP ports
    udp = UDP(sport=68,
              dport=67)

    # xid is the transaction ID and should be the same on all the networks
    bootp = BOOTP(chaddr=client_mac_address,
                  xid=x_id,
                  flags=1)

    # DHCP message
    dhcp = DHCP(options=[("message-type", "request"),
                         ('client_id', b'\x01' + mac2str(client_mac_address)),
                         ("requested_addr", offered_ip),
                         ("server_id", server_id),
                         "end"])

    discovery_packet = ethernet / ip / udp / bootp / dhcp

    return discovery_packet

def handle_dhcp_offer(packet):
    if packet.haslayer(DHCP):
        if packet[DHCP] and packet[DHCP].options[0][1] == 2:
            print(f"Received offer from server{packet.src}")
            stop_event.set()
            request_packet = create_dhcp_request(packet)
            sendp(request_packet, iface=wifi_interface)
            print(f"Sent request packet from client {client_mac_address}")

def sniff_DHCP_offers():
    sniff(filter="arp or (udp and (port 67 or 68))", prn=handle_dhcp_offer, store=0)

def start_dhcp_client():
    print("Starting DHCP Client")
    discovery_thread = threading.Thread(target=send_dhcp_discover)
    discovery_thread.start()

    sniff_thread = threading.Thread(target=sniff_DHCP_offers())
    sniff_thread.start()

    discovery_thread.join()
    sniff_thread.join()

if __name__ == "__main__":
    if wifi_interface:
        start_dhcp_client()
    else:
        print("No wifi interface, client did not start")