import netifaces
import os
import threading
from threading import Event
import time

from scapy.all import *
from scapy.layers.dhcp import *
from scapy.layers.inet import *

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
src_mac_address = get_if_hwaddr(wifi_interface)
# Clients id for DHCP
x_id = 0x01234567

class DHCP_Client():
    def __init__(self):
        self._wifi_interface = get_wifi_interface()
        self._clientIP = None
        self._clientMAC = get_if_hwaddr(self._wifi_interface)
        self._serverIP = None
        self._serverMAC = None
        self._client_xID = 0x01234567

    # DHCP packet
    def create_dhcp_discover_packet(self):
        print("Making DHCP discovery packet")

        # Make ethernet unavailable b/c we are using WiFi
        ethernet = Ether(dst='ff:ff:ff:ff:ff:ff',
                         src=self._clientMAC,
                         type=0x800)
        # Source and destination IP, source is assumed to be 0 empty at first
        ip = IP(src='0.0.0.0',
                dst='255.255.255.255')

        # UDP ports
        udp = UDP(sport=68,
                  dport=67)

        # xid is the transaction ID and should be the same on all the networks
        bootp = BOOTP(chaddr=self._clientMAC,
                      ciaddr='0.0.0.0',
                      xid=self._client_xID, flags=1)

        dhcp = DHCP(options=[("message-type", "discover"),
                             "end"])

        discovery_packet = ethernet / ip / udp / bootp / dhcp

        return discovery_packet

    # Send DHCP discovery packets
    def send_dhcp_discover(self):
        print("sending DHCP discovery packet")
        discovery_packet = self.create_dhcp_discover_packet()
        delay = 3
        while not stop_event.is_set():
            sendp(discovery_packet, iface=wifi_interface)
            print(f"Packet sent, wait for {delay} seconds before next send...")
            time.sleep(delay)

    def create_dhcp_request(self, offer_packet):
        print("Making DHCP request packet")
        # This is the IP offered by the server
        self._clientIP = offer_packet[BOOTP].yiaddr
        # This is the IP of the server or the server IP itself because the IP = ID
        self._serverIP = [opt[1] for opt in offer_packet[DHCP].options if opt[0] == 'server_id'][0]
        # Make ethernet unavailable b/c we are using WiFi
        ethernet = Ether(dst='ff:ff:ff:ff:ff:ff',
                         src=src_mac_address,
                         type=0x800)
        # Source and destination IP, source is assumed to be 0 empty at first
        ip = IP(src='0.0.0.0',
                dst='255.255.255.255')
        # UDP ports
        udp = UDP(sport=68,
                  dport=67)

        # xid is the transaction ID and should be the same on all the networks
        bootp = BOOTP(chaddr=src_mac_address,
                      xid=x_id,
                      flags=1)

        # DHCP message
        dhcp = DHCP(options=[("message-type", "request"),
                             ('client_id', b'\x01' + mac2str(self._clientMAC)),
                             ("requested_addr", self._clientIP),
                             ("server_id", self._serverIP),
                             "end"])

        discovery_packet = ethernet / ip / udp / bootp / dhcp

        return discovery_packet

    def handle_dhcp_offer(self, packet):
        if packet.haslayer(DHCP):
            if packet[DHCP] and packet[DHCP].options[0][1] == 2:
                print(f"Received offer from server{packet.src}")
                stop_event.set()
                request_packet = self.create_dhcp_request(packet)
                sendp(request_packet, iface=wifi_interface)
                print(f"Sent request packet from client {src_mac_address}")

    def sniff_DHCP_offers(self):
        sniff(filter="arp or (udp and (port 67 or 68))", prn=self.handle_dhcp_offer, store=0)

def start_dhcp_client():
    print("Starting DHCP Client")
    dhcp_client = DHCP_Client()
    discovery_thread = threading.Thread(target=dhcp_client.send_dhcp_discover)
    discovery_thread.start()

    sniff_thread = threading.Thread(target=dhcp_client.sniff_DHCP_offers)
    sniff_thread.start()

    discovery_thread.join()
    sniff_thread.join()

if __name__ == "__main__":
    if wifi_interface:
        start_dhcp_client()
    else:
        print("No wifi interface, client did not start")
