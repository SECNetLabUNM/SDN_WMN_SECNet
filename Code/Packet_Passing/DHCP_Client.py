import netifaces
import os
import threading
import time

from scapy.all import *
from scapy.layers.dhcp import *
from scapy.layers.inet import *

def response_dhcp_discover():
    return 0

# DHCP packet
def create_dhcp_discover_packet(wifi_interface):
    print("creating the packet")
    src_mac_address = get_if_hwaddr(wifi_interface)
    x_id = 0x01234567

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
                  ciaddr='0.0.0.0',
                  xid=x_id, flags=1)
    dhcp = DHCP(options=[("message-type", "discover"),
                         "end"])

    discovery_packet = ethernet / ip / udp / bootp / dhcp

    return discovery_packet

# Send DHCP discovery packets
def send_dhcp_discover(wifi_interface):
    print("sending DHCP discovery packet")
    packet = create_dhcp_discover_packet(wifi_interface)
    delay = 3
    interval = 10
    for _ in range(interval):
        sendp(packet, iface=wifi_interface)
        print(f"Packet sent, wait for {delay} seconds before next send...")
        time.sleep(delay)

def start_dhcp_client(wifi_interface):
    print("Starting DHCP Client")
    send_dhcp_discover(wifi_interface)

if __name__ == "__main__":
    for interface in netifaces.interfaces():
        try:
            if os.path.exists(f'/sys/class/net/{interface}/wireless'):
                start_dhcp_client(interface)
        except Exception as e:
            print(f"Error checking interface {interface}: {e}")
            print("Fail to start DHCP client")