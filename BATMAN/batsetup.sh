# 0. Checks for BATMAN availability
sudo modprobe batman-adv

sudo rfkill unblock 1

# 1. Setting up the network NIC
sudo ip link set $NIC$ down
sudo iwconfig $NIC$ mode ad-hoc
sudo iwconfig $NIC$ essid my-mesh-network
sudo iwconfig $NIC$ ap any
sudo iwconfig $NIC$ channel 8

sleep 1s
sudo ip link set $NIC$ up

# 2. Setting up BATMAN
sleep 1s
sudo batctl routing_algo BATMAN_IV
sudo batctl if add $NIC$

# 3. Create IP address and turn BATMAN on
sleep 1s
sudo ip addr add dev bat0 $IP_ADDRESS$/24
sudo ip link set dev bat0 up
