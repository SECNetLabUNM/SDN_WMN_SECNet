#!/bin/bash
# --- Setup B.A.T.M.A.N wireless network ---

source ./config.sh

# Activate batman-adv
sudo modprobe batman-adv

# Remove RFKill error, check using `sudo rfkill list`
sudo rfkill unblock 1

# Disable and configure $wireless_interface
sudo ip link set $wireless_interface down
sudo iwconfig $wireless_interface mode ad-hoc
sudo iwconfig $wireless_interface essid my-mesh-network
sudo iwconfig $wireless_interface ap any
sudo iwconfig $wireless_interface channel $network_channel
sleep 1s
sudo ip link set $wireless_interface up

# Setup batman
sleep 1s
# FOR BATMAN VERSIONS
# sudo batctl ra BATMAN_V
sudo batctl ra $batman_algo
sudo batctl if add $wireless_interface

# x = [1,2,3,4,...]
sleep 1s
sudo ip addr add dev bat0 $self_CIDR
sudo ip link set dev bat0 up

# Configure interface to apply a penalty to calculated thoroughput of 255/255 (100%) for multi-hop through this device effectively disabling multi-hop. Allows SDN more control over routing. See <https://www.open-mesh.org/projects/batman-adv/wiki/Tweaking#hop-penalty>
sudo batctl meshif bat0 hop_penalty 255
