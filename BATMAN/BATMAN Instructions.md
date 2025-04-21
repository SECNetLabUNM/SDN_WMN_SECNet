For our BATMAN installation, we used Ubuntu 20.04.06 LTS and Raspberry Pi OS (64-bit). We have confirmed that these two operating systems can run Batman IV and Batman V. 

The official BATMAN documentation can be referenced here:

[https://www.open-mesh.org/projects/batman-adv/wiki](https://www.open-mesh.org/projects/batman-adv/wiki)

## Installation of BATMAN
On a terminal, run:
<pre> sudo apt install batctl bridge-utils </pre>
To confirm it is installed correctly, run:
<pre> sudo modprobe batman-adv` </pre>
## Setup Script
After downloading BATMAN. Use this script courtesy of this Reddit article:

[https://www.reddit.com/r/darknetplan/comments/68s6jp/how_to_configure_batmanadv_on_the_raspberry_pi_3/?rdt=44892](https://www.reddit.com/r/darknetplan/comments/68s6jp/how_to_configure_batmanadv_on_the_raspberry_pi_3/?rdt=44892)

<pre>
# 
sudo modprobe batman-adv

sudo rfkill unblock 1

sudo ip link set $NIC$ down
sudo iwconfig $NIC$ mode ad-hoc
sudo iwconfig $NIC$ essid my-mesh-network
sudo iwconfig $NIC$ ap any
sudo iwconfig $NIC$ channel 8

sleep 1s
sudo ip link set $NIC$ up

sleep 1s
sudo batctl routing_algo BATMAN_IV
sudo batctl if add $NIC$

sleep 1s
sudo ip addr add dev bat0 $IP_ADDRESS$
sudo ip link set dev bat0 up
</pre>

### Fill In the Details
- \$NIC\$ -  The name of your wireless interface the host is using
- \$IP\_ADDRESS\$ - The IP address you will give for your BATMAN host. We recommend using something memorable over the usual 192.168.x.x.
- To change between routing algorithms, use either BATMAN_IV or BATMAN_V