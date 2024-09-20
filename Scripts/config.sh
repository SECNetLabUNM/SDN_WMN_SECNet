#!/bin/bash
# Remove this after reading, naming the file to `config.sh`, and setting values.
echo Remember to setup config.sh before running!
exit 1

# Terminology
# ip address - the raw ip address e.g. 192.168.0.1
# CIDR address - the [CIDR](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing) address e.g. 192.168.0.1/24

# Keep in mind that in bash the lack of spaces when assigning is nessessary i.e. `var = 0` won't work but `var=0` will.
# Also keep in mind that specify strings requires using `""` or `''` if they include spaces


# --- BATMAN config ---

# The CIDR of this device on the BATMAN network.
# e.g. 100.100.1.6/24
self_CIDR=
wireless_interface=wlan0
network_name=my-mesh-network
network_channel=8
batman_algo=BATMAN_V # BATMAN_IV or BATMAN_V

# --- Openvswitch config ---

# The name to use for the openvswitch bridge.
# e.g. br_1
openvswitch_bridge_name=

# The ip address of the probe VM of this device on the overlay network.
# e.g. 50.50.50.6/24
probe_CIDR=

# The ip of the controller for networking.
# If using batman this is the batman ip. If using a wireless acess point it is the ip assigned to the controller on the wireless LAN.
# e.g. 192.168.1.38 or 100.100.1.6
controller_ip=

# The name of this device.
# e.g. pi1
self_name=
# The name of all devices including this device.
# This should be able to be the same among all the devices.
declare -a device_names=(
    pi1
    pi2
    # ... etc
)
# The attributes per device. It is important to match the format of [<device>_<attribute>] as the key.
# This should be able to be the same among all the devices.
declare -A devices=(
    # pi1:
    [pi1_ip]= # e.g. 100.100.1.6
    [pi1_id]=1
    [pi1pi2_port]= # e.g. 10
    # pi2:
    [pi2_ip]= # e.g. 100.100.1.7
    [pi2_id]=2
    [pi2pi1_port]= # same as pi1pi2_port
    # ... etc
)
